"""
Konstruktimi i Search Tree - pjesa e perbashket per te tre problemet.

Nje problem duhet te kete:
    initial                 - gjendja fillestare
    is_goal(state)          - testi i qellimit
    successors(state)       - lista (veprimi, gjendja_e_re, arsye)
                              arsye = None nese gjendja eshte valide,
                              perndryshe teksti pse eshte jo-valide
    label(state)            - teksti i shkurter per nyjen
    label_lines(state)      - (opsionale) lista rreshtash per diagram

Pema ndertohet nivel pas niveli. Cdo nyje ka nje status:
    ""          - nyje e zakonshme (zgjerohet)
    "GOAL"      - gjendja e qellimit
    "REPEATED"  - gjendja eshte pare me pare (nuk zgjerohet)
    "INVALID"   - gjendja shkel kufizimet (nuk zgjerohet)
    "LIMIT"     - arriti thellesine maksimale (nuk zgjerohet)
"""

from collections import deque


class Node:
    _next_id = 0

    def __init__(self, state, parent=None, action=None, status=""):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = 0 if parent is None else parent.depth + 1
        self.status = status
        self.children = []
        self.on_path = False
        self.id = Node._next_id
        Node._next_id += 1

    def path(self):
        node, nodes = self, []
        while node:
            nodes.append(node)
            node = node.parent
        return nodes[::-1]


def build_tree(problem, max_depth, repeated="graph"):
    """
    Nderton search tree deri ne thellesine max_depth (BFS, nivel pas niveli).

    repeated = "graph": nje gjendje e pare ne cdo pjese te pemes nuk zgjerohet
                        perseri (graph search, eliminon ciklet dhe duplikatet)
             = "path":  vetem gjendjet qe jane paraardhes ne te njejten dege
                        konsiderohen te perseritura (tree search pa cikle)
    """
    Node._next_id = 0
    root = Node(problem.initial)
    seen = {problem.initial}
    queue = deque([root])
    if problem.is_goal(root.state):
        root.status = "GOAL"
        return root

    while queue:
        node = queue.popleft()
        if node.depth == max_depth:
            node.status = node.status or "LIMIT"
            continue
        ancestors = {n.state for n in node.path()}
        for action, state, reason in problem.successors(node.state):
            child = Node(state, node, action)
            node.children.append(child)
            if reason:
                child.status = "INVALID"
                child.reason = reason
            elif (state in seen) if repeated == "graph" else (state in ancestors):
                child.status = "REPEATED"
            elif problem.is_goal(state):
                child.status = "GOAL"
                seen.add(state)
            else:
                seen.add(state)
                queue.append(child)
    return root


def mark_path(root, goal_test):
    """Shenjon rrugen nga rrenja te nyja e pare e qellimit (ne rend BFS)."""
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if goal_test(node):
            for n in node.path():
                n.on_path = True
            return node
        queue.extend(node.children)
    return None


def stats(root):
    counts = {"nodes": 0, "expanded": 0, "GOAL": 0, "REPEATED": 0,
              "INVALID": 0, "LIMIT": 0, "depth": 0}
    stack = [root]
    while stack:
        n = stack.pop()
        counts["nodes"] += 1
        counts["depth"] = max(counts["depth"], n.depth)
        if n.children:
            counts["expanded"] += 1
        if n.status:
            counts[n.status] += 1
        stack.extend(n.children)
    return counts


# ---------------------------------------------------------------------------
# Shfaqja e pemes
# ---------------------------------------------------------------------------

def ascii_tree(root, problem, max_depth=None):
    """Pema si tekst, me ├── dhe └── (si komanda `tree`)."""
    lines = []

    def describe(n):
        text = problem.label(n.state)
        if n.action is not None:
            text = f"{n.action} -> {text}"
        tags = []
        if n.on_path:
            tags.append("*")
        if n.status == "INVALID":
            tags.append(f"INVALID: {n.reason}")
        elif n.status:
            tags.append(n.status)
        return text + (f"   [{', '.join(tags)}]" if tags else "")

    def rec(n, prefix, last):
        connector = "" if n.parent is None else ("└── " if last else "├── ")
        lines.append(prefix + connector + describe(n))
        if max_depth is not None and n.depth >= max_depth:
            if n.children:
                lines.append(prefix + ("    " if last else "│   ") + "└── ...")
            return
        child_prefix = prefix + ("" if n.parent is None else ("    " if last else "│   "))
        for i, c in enumerate(n.children):
            rec(c, child_prefix, i == len(n.children) - 1)

    rec(root, "", True)
    return "\n".join(lines)


def mermaid_tree(root, problem, max_depth=None, only_path_below=None):
    """
    Pema ne formatin Mermaid (GitHub e vizaton automatikisht ne README).
    only_path_below: nen kete thellesi shfaqen vetem nyjet e rruges se zgjidhjes.
    """
    lines = ["graph TD"]
    styles = {"GOAL": "goal", "REPEATED": "repeated", "INVALID": "invalid", "LIMIT": "limit"}

    def visible(n):
        if max_depth is not None and n.depth > max_depth:
            return False
        if only_path_below is not None and n.depth > only_path_below:
            return n.on_path or (n.parent is not None and n.parent.on_path)
        return True

    def text(n):
        rows = problem.label_lines(n.state) if hasattr(problem, "label_lines") \
            else [problem.label(n.state)]
        if n.status == "INVALID":
            rows = rows + [f"✗ {n.reason}"]
        elif n.status == "REPEATED":
            rows = rows + ["↺ e perseritur"]
        elif n.status == "GOAL":
            rows = rows + ["✓ QELLIMI"]
        return "<br/>".join(rows).replace('"', "'")

    stack = [root]
    while stack:
        n = stack.pop()
        lines.append(f'    n{n.id}["{text(n)}"]')
        cls = "path" if n.on_path and n.status != "GOAL" else styles.get(n.status)
        if cls:
            lines.append(f"    class n{n.id} {cls}")
        for c in reversed(n.children):
            if visible(c):
                lines.append(f'    n{n.id} -->|"{c.action}"| n{c.id}')
                stack.append(c)

    lines += [
        "    classDef goal fill:#2e7d32,color:#fff,stroke:#1b5e20",
        "    classDef path fill:#1565c0,color:#fff,stroke:#0d47a1",
        "    classDef repeated fill:#9e9e9e,color:#fff,stroke:#616161",
        "    classDef invalid fill:#c62828,color:#fff,stroke:#8e0000",
        "    classDef limit fill:#f9a825,color:#000,stroke:#f57f17",
    ]
    return "\n".join(lines)
