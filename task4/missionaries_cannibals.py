"""
Missionaries and Cannibals.

3 misionare dhe 3 kanibale jane ne bregun e majte te nje lumi me nje varke
qe mban 1 ose 2 persona. Te gjithe duhet te kalojne ne bregun e djathte.
Ne asnje breg kanibalet nuk mund te jene me shume se misionaret
(nese ka te pakten nje misionar ne ate breg).

Reprezentimi: gjendja = (M, C, B)
    M = misionaret ne bregun e majte (0..3)
    C = kanibalet ne bregun e majte  (0..3)
    B = 1 nese varka eshte ne bregun e majte, 0 nese ne te djathtin
Gjendja fillestare: (3, 3, 1)      Qellimi: (0, 0, 0)
Veprimet: varka bart (m, c) persona: (1,0), (2,0), (0,1), (0,2), (1,1).
"""

BOAT_LOADS = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]


class MissionariesCannibals:
    name = "Missionaries and Cannibals"

    def __init__(self, n=3, boat=2):
        self.n = n
        self.loads = [(m, c) for m, c in BOAT_LOADS if 1 <= m + c <= boat]
        self.initial = (n, n, 1)
        self.goal = (0, 0, 0)

    def is_goal(self, state):
        return state == self.goal

    def successors(self, state):
        M, C, B = state
        sign = -1 if B == 1 else 1          # varka niset nga i majti -> zbresin
        result = []
        for m, c in self.loads:
            nm, nc = M + sign * m, C + sign * c
            if not (0 <= nm <= self.n and 0 <= nc <= self.n):
                continue                    # nuk ka mjaftueshem persona per kete veprim
            new = (nm, nc, 1 - B)
            action = f"{m}M{c}C {'→' if B == 1 else '←'}"
            result.append((action, new, self.violation(new)))
        return result

    def violation(self, state):
        M, C, _ = state
        if 0 < M < C:
            return "majtas C > M"
        if 0 < self.n - M < self.n - C:
            return "djathtas C > M"
        return None

    def label(self, state):
        return "  ".join(self.label_lines(state))

    def label_lines(self, state):
        M, C, B = state
        left = "M" * M + "C" * C or "-"
        right = "M" * (self.n - M) + "C" * (self.n - C) or "-"
        return [f"({M},{C},{B})", f"{left} {'B~~' if B else '~~B'} {right}"]
