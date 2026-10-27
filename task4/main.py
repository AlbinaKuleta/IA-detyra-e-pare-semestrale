"""
Detyra 4 - Search Trees per 8-Puzzle, Missionaries and Cannibals dhe
Rotating Workforce Scheduling.

Per secilin problem:
  - ndertohet search tree (nivel pas niveli),
  - shenjohet rruga deri te zgjidhja (*),
  - pema shtypet si tekst dhe ruhet ne folderin output/ si .txt dhe .mmd
    (Mermaid - mund te hapet ne https://mermaid.live ose direkt ne GitHub).

Perdorimi:
    python main.py                  # te tre problemet
    python main.py --problem puzzle # vetem 8-Puzzle (puzzle | mc | rws)
"""

import argparse
import os
import sys

from eight_puzzle import EightPuzzle
from missionaries_cannibals import MissionariesCannibals
from rotating_workforce import RotatingWorkforce
from search_tree import ascii_tree, build_tree, mark_path, mermaid_tree, stats

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def save(name, text):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(text + "\n")


def report(title, root, problem, file_prefix, mermaid_kwargs=None, ascii_depth=None):
    st = stats(root)
    goal = mark_path(root, lambda n: n.status == "GOAL")
    tree = ascii_tree(root, problem, ascii_depth)
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")
    print(tree)
    print(f"\nNyje: {st['nodes']} | te zgjeruara: {st['expanded']} | "
          f"te perseritura: {st['REPEATED']} | jo-valide: {st['INVALID']} | "
          f"te ndalura nga kufiri: {st['LIMIT']} | qellime: {st['GOAL']} | "
          f"thellesia: {st['depth']}")
    if goal:
        steps = [n.action for n in goal.path()[1:]]
        print(f"Zgjidhja ({len(steps)} hapa): {' , '.join(steps)}")
    save(f"{file_prefix}_tree.txt", tree)
    save(f"{file_prefix}_tree.mmd", mermaid_tree(root, problem, **(mermaid_kwargs or {})))
    return goal


def run_puzzle(depth):
    p = EightPuzzle(initial=(1, 2, 3, 0, 4, 6, 7, 5, 8))
    root = build_tree(p, depth, repeated="graph")
    report(f"8-PUZZLE (thellesia max = {depth})", root, p, "8puzzle")


def run_mc():
    p = MissionariesCannibals()
    root = build_tree(p, max_depth=20, repeated="graph")
    report("MISSIONARIES AND CANNIBALS (pema e plote, graph search)", root, p, "missionaries")


def run_rws(depth):
    p = RotatingWorkforce()
    solution = p.solve()

    root = build_tree(p, depth, repeated="path")
    # shenjo prefiksin e zgjidhjes ne pemen e vizatuar
    prefix = solution[:depth]
    mark_path(root, lambda n: n.state == prefix)
    st = stats(root)
    tree = ascii_tree(root, p)
    print(f"\n{'=' * 70}\nROTATING WORKFORCE SCHEDULING (nivelet e para, thellesia = {depth})\n{'=' * 70}")
    print(tree)
    print(f"\nNyje: {st['nodes']} | te zgjeruara: {st['expanded']} | jo-valide: {st['INVALID']} | "
          f"te ndalura nga kufiri: {st['LIMIT']}")
    print(f"Pema e plote ka thellesi {p.length} (nje nivel per cdo dite) dhe deri ne "
          f"4^{p.length} ≈ 7.2e16 gjethe; prandaj vizatohen vetem nivelet e para.")
    print(f"\nZgjidhja me DFS + backtracking ({p.expanded} nyje te zgjeruara):")
    print(p.format_schedule(solution))
    print(f"Rruga ne peme: {' → '.join(solution)}")
    save("rws_tree.txt", tree)
    save("rws_tree.mmd", mermaid_tree(root, p))
    save("rws_solution.txt", p.format_schedule(solution))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Search Trees")
    ap.add_argument("--problem", choices=["puzzle", "mc", "rws", "all"], default="all")
    ap.add_argument("--puzzle-depth", type=int, default=3)
    ap.add_argument("--rws-depth", type=int, default=2)
    args = ap.parse_args()

    if args.problem in ("puzzle", "all"):
        run_puzzle(args.puzzle_depth)
    if args.problem in ("mc", "all"):
        run_mc()
    if args.problem in ("rws", "all"):
        run_rws(args.rws_depth)
    print(f"\nPemet u ruajten ne: {OUT}")


if __name__ == "__main__":
    main()
