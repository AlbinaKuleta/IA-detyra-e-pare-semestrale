"""
8-Puzzle.

Rrjete 3x3 me pllakat 1..8 dhe nje hapesire bosh (0). Ne cdo levizje,
nje pllake fqinje rreshqet ne hapesiren bosh. Qellimi:
    1 2 3
    4 5 6
    7 8 _

Reprezentimi: gjendja = tuple me 9 vlera (rresht pas rreshti), 0 = bosh.
Veprimet: levizja e hapesires bosh Up / Down / Left / Right.
Faktori i degezimit: 2 (kend), 3 (buze) ose 4 (qender).
"""

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
MOVES = {"Up": -3, "Down": 3, "Left": -1, "Right": 1}


class EightPuzzle:
    name = "8-Puzzle"

    def __init__(self, initial=(1, 2, 3, 4, 0, 6, 7, 5, 8), goal=GOAL):
        self.initial = tuple(initial)
        self.goal = tuple(goal)

    def is_goal(self, state):
        return state == self.goal

    def successors(self, state):
        blank = state.index(0)
        r, c = divmod(blank, 3)
        result = []
        for action, delta in MOVES.items():
            if (action == "Up" and r == 0) or (action == "Down" and r == 2) \
                    or (action == "Left" and c == 0) or (action == "Right" and c == 2):
                continue                    # levizja del jashte rrjetes
            target = blank + delta
            s = list(state)
            s[blank], s[target] = s[target], s[blank]
            result.append((action, tuple(s), None))
        return result

    def label_lines(self, state):
        return [" ".join(str(v) if v else "_" for v in state[r * 3:r * 3 + 3]) for r in range(3)]

    def label(self, state):
        return " | ".join(self.label_lines(state))
