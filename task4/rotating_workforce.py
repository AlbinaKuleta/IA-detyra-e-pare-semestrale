"""
Rotating Workforce Scheduling (RWS).

n punetore punojne sipas te njejtit orar ciklik prej n javesh: punetori i
punon ne javen j rreshtin (i + j) mod n te orarit. Cdo dite ka nderrime:
    D = dite, A = pasdite, N = nate, - = pushim

Instanca (e vogel, qe pema te jete e lexueshme):
    - 4 punetore -> cikel 4 jave = 28 dite
    - cdo dite te javes duhet saktesisht: 1 D, 1 A, 1 N (dhe 1 pushim)
    - blloqet e punes (dite pune radhazi): 3..6 dite
    - blloqet e pushimit: 1..3 dite
    - nje bllok i te njejtit nderrim: 2..5 dite
    - sekuenca te ndaluara (pa pushim te mjaftueshem): N→D, N→A, A→D

Reprezentimi: gjendja = tuple me nderrimet e caktuara deri tani
(dita 0, 1, 2, ...). Cdo nivel i pemes cakton nderrimin e dites se radhes.
Domain-i i cdo dite: {D, A, N, -}. Qellimi: te 28 ditet jane caktuar dhe
te gjitha kufizimet (perfshire kalimin ciklik nga dita 27 te dita 0) plotesohen.
"""

SHIFTS = ["D", "A", "N", "-"]
DAYS = ["Hë", "Ma", "Më", "En", "Pr", "Sh", "Di"]


class RotatingWorkforce:
    name = "Rotating Workforce Scheduling"

    def __init__(self, employees=4, demand=None, work_block=(3, 6), off_block=(1, 3),
                 shift_block=(2, 5), forbidden=(("N", "D"), ("N", "A"), ("A", "D"))):
        self.n = employees
        self.length = 7 * employees
        # demand[shift][weekday]
        self.demand = demand or {s: [1] * 7 for s in ["D", "A", "N"]}
        self.demand["-"] = [employees - sum(self.demand[s][d] for s in ["D", "A", "N"])
                            for d in range(7)]
        self.work_block = work_block
        self.off_block = off_block
        self.shift_block = shift_block
        self.forbidden = set(forbidden)
        self.initial = ()

    def is_goal(self, state):
        return len(state) == self.length and self.violation(state) is None

    # -- kufizimet ------------------------------------------------------------

    @staticmethod
    def _blocks(seq, key):
        """Blloqet (vlera, gjatesia) sipas funksionit key."""
        blocks = []
        for x in seq:
            k = key(x)
            if blocks and blocks[-1][0] == k:
                blocks[-1][1] += 1
            else:
                blocks.append([k, 1])
        return blocks

    def _check_blocks(self, blocks):
        """Kontrollon gjatesite e blloqeve. Blloku i pare mund te vazhdoje nga
        fundi i ciklit, prandaj minimumi i tij kontrollohet vetem ne fund;
        blloku i fundit mund te vazhdoje ende, prandaj per te kontrollohet
        vetem maksimumi."""
        for idx, (k, length) in enumerate(blocks):
            lo, hi = self._limits(k)
            if length > hi:
                return f"bllok '{k}' > {hi}"
            first, last = idx == 0, idx == len(blocks) - 1
            if not first and not last and length < lo:
                return f"bllok '{k}' < {lo}"
        return None

    def _limits(self, k):
        if k == "W":
            return self.work_block
        if k == "-":
            return self.off_block
        return self.shift_block

    def violation(self, state):
        """Kthen arsyen pse gjendja (e pjesshme) eshte jo-valide, ose None."""
        k = len(state)
        if k == 0:
            return None
        cur = state[-1]
        # 1. sekuencat e ndaluara
        if k >= 2 and (state[-2], cur) in self.forbidden:
            return f"{state[-2]}→{cur} e ndaluar"
        # 2. kerkesa ditore: sa punetore ne kete nderrim ne kete dite te javes
        day = (k - 1) % 7
        used = sum(1 for i in range(day, k, 7) if state[i] == cur)
        if used > self.demand[cur][day]:
            return f"{DAYS[day]}: tepër '{cur}'"
        # 3. gjatesite e blloqeve
        complete = k == self.length
        seq = list(state) + (list(state) if complete else [])   # cikli
        work = self._blocks(seq, lambda x: "W" if x != "-" else "-")
        shifts = self._blocks(seq, lambda x: x)
        if complete:
            # ne cikel te plote: blloqet e mesme te kopjes se dyfishte jane te plota
            for blocks in (work, shifts):
                for kk, length in blocks[1:-1]:
                    lo, hi = self._limits(kk)
                    if not lo <= length <= hi:
                        return f"bllok '{kk}' {length} jashte [{lo},{hi}]"
            if (state[-1], state[0]) in self.forbidden:
                return f"{state[-1]}→{state[0]} (cikli) e ndaluar"
            return None
        return self._check_blocks(work) or self._check_blocks(shifts)

    # -- pema -------------------------------------------------------------------

    def successors(self, state):
        if len(state) == self.length:
            return []
        return [(s, state + (s,), self.violation(state + (s,))) for s in SHIFTS]

    def label(self, state):
        if not state:
            return "(bosh)"
        s = "".join(state)
        return "|".join(s[i:i + 7] for i in range(0, len(s), 7))

    # -- zgjidhja me DFS + backtracking ------------------------------------------

    def solve(self):
        """DFS mbi te njejten peme; degët jo-valide priten menjehere."""
        self.expanded = 0

        def dfs(state):
            self.expanded += 1
            if len(state) == self.length:
                return state if self.violation(state) is None else None
            for _, child, reason in self.successors(state):
                if reason is None:
                    found = dfs(child)
                    if found:
                        return found
            return None

        return dfs(self.initial)

    def format_schedule(self, state):
        lines = ["Java  " + " ".join(f"{d:>2}" for d in DAYS)]
        for w in range(self.n):
            row = state[w * 7:(w + 1) * 7]
            lines.append(f"  {w + 1}   " + " ".join(f"{x:>2}" for x in row))
        return "\n".join(lines)
