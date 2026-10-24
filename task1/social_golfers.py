"""
Social Golfers Problem - Depth First Search (DFS) me Backtracking.

Problemi: n = g * p lojtare luajne cdo jave ne g grupe me nga p lojtare.
A mund te planifikohen w jave ashtu qe asnje cift lojtaresh te mos
luaje ne te njejtin grup me shume se nje here?

Reprezentimi:
    schedule[week][group] = lista me p lojtare (numra 0 .. n-1)

Variablat:  cdo "slot" (week, group, position) -> nje lojtar
Domain-i:   {0, 1, ..., n-1}
Kufizimet:
    1. Brenda nje jave, cdo lojtar paraqitet saktesisht nje here.
    2. Cdo grup ka saktesisht p lojtare.
    3. Cdo cift lojtaresh takohet ne te njejtin grup te shumten nje here.

Perdorimi:
    python social_golfers.py                     # 8 grupe x 4 lojtare, gjen w maksimal
    python social_golfers.py -g 8 -p 4 -w 6      # zgjidh per w jave
    python social_golfers.py -g 3 -p 3 -w 4      # shembull i vogel (Kirkman)
"""

import argparse
import random
import sys
import time
from itertools import combinations


# ---------------------------------------------------------------------------
# Objective function
# ---------------------------------------------------------------------------

def objective(schedule):
    """
    Objective function: numri i takimeve te perseritura.

        f(S) = sum_{i<j} max(0, takime(i, j) - 1)

    ku takime(i, j) eshte sa here lojtaret i dhe j jane ne te njejtin grup.
    Nje orar eshte zgjidhje valide atehere dhe vetem atehere kur f(S) = 0.
    """
    meetings = {}
    for week in schedule:
        for group in week:
            for pair in combinations(sorted(group), 2):
                meetings[pair] = meetings.get(pair, 0) + 1
    return sum(count - 1 for count in meetings.values() if count > 1)


def is_valid(schedule, g, p):
    """Kontrollon te gjitha kufizimet e problemit."""
    n = g * p
    for week in schedule:
        if len(week) != g or any(len(group) != p for group in week):
            return False
        players = sorted(x for group in week for x in group)
        if players != list(range(n)):
            return False
    return objective(schedule) == 0


def upper_bound_weeks(g, p):
    """
    Kufiri i siperm: cdo lojtar takon p-1 lojtare te rinj cdo jave dhe
    ka vetem n-1 lojtare te tjere, prandaj w <= (n-1) / (p-1).
    """
    n = g * p
    return (n - 1) // (p - 1) if p > 1 else float("inf")


# ---------------------------------------------------------------------------
# DFS me Backtracking
# ---------------------------------------------------------------------------

class SearchTimeout(Exception):
    pass


class NodeLimitReached(Exception):
    """Perdoret nga DFS me restart: kjo provë u nderpre, fillo nje te re."""
    pass


class SocialGolfersDFS:
    """
    DFS me backtracking qe mbush orarin slot pas sloti:
    java -> grupi -> pozita brenda grupit.

    Per efikasitet, per cdo lojtar mbahet nje bitmask `met[i]` me te gjithe
    lojtaret qe i ka takuar deri tani.

    Thyerja e simetrive (symmetry breaking) - nuk humbet asnje zgjidhje,
    vetem eliminon kopjet ekuivalente:
      * lojtaret brenda grupit jane ne rend rrites;
      * cdo grup fillon me lojtarin me te vogel te pacaktuar ende ne ate jave
        (grupet jane te renditura sipas lojtarit te pare);
      * java e pare eshte fikse: {0..p-1}, {p..2p-1}, ...;
      * javet renditen sipas partnerit te dyte te lojtarit 0.

    Nese jepet `rng`, kandidatet provohen ne rend te rastesishem dhe kerkimi
    nderpritet pas `node_limit` nyjeve (DFS me restart - shih run()).
    """

    def __init__(self, g, p, w, timeout=None, rng=None, node_limit=None):
        self.g, self.p, self.w = g, p, w
        self.n = g * p
        self.timeout = timeout
        self.rng = rng
        self.node_limit = node_limit
        self.nodes = 0          # numri i nyjeve te vizituara
        self.backtracks = 0     # numri i kthimeve mbrapa
        self.met = [0] * self.n
        self.schedule = [[[] for _ in range(g)] for _ in range(w)]
        self.full = (1 << self.n) - 1

    # -- ndihmese -----------------------------------------------------------

    def _check_time(self):
        if self.node_limit is not None and self.nodes > self.node_limit:
            raise NodeLimitReached
        if self.timeout is not None and (self.nodes & 0x3FFF) == 0:
            if time.perf_counter() - self.start > self.timeout:
                raise SearchTimeout

    def _place(self, player, group):
        for m in group:
            self.met[m] |= 1 << player
            self.met[player] |= 1 << m
        group.append(player)

    def _unplace(self, group):
        player = group.pop()
        for m in group:
            self.met[m] &= ~(1 << player)
            self.met[player] &= ~(1 << m)

    # -- kerkimi ------------------------------------------------------------

    def solve(self):
        """Kthen orarin nese gjendet, None nese nuk ekziston.
        Ngre SearchTimeout nese kalon koha."""
        self.start = time.perf_counter()
        if self.w > upper_bound_weeks(self.g, self.p):
            return None
        if self.w == 0:
            return []
        # Java e pare fikse (symmetry breaking).
        for gi in range(self.g):
            for player in range(gi * self.p, (gi + 1) * self.p):
                self._place(player, self.schedule[0][gi])
        if self.w == 1 or self._dfs(1, 0, 0, self.full):
            return [[list(gr) for gr in week] for week in self.schedule]
        return None

    def _dfs(self, week, gi, slot, free):
        """
        week, gi, slot - pozita aktuale qe duhet mbushur
        free           - bitmask i lojtareve ende te pacaktuar ne kete jave
        """
        self.nodes += 1
        self._check_time()

        if slot == self.p:                       # grupi u mbush
            gi, slot = gi + 1, 0
            if gi == self.g:                     # java u mbush
                week, gi, free = week + 1, 0, self.full
                if week == self.w:               # te gjitha javet u mbushen
                    return True

        group = self.schedule[week][gi]

        if slot == 0:
            # Grupi i ri fillon me lojtarin me te vogel te lire.
            player = (free & -free).bit_length() - 1
            self._place(player, group)
            if self._dfs(week, gi, 1, free & ~(1 << player)):
                return True
            self._unplace(group)
            self.backtracks += 1
            return False

        # Kandidatet: te lire, me te medhenj se i fundit ne grup,
        # dhe qe nuk jane takuar me asnje anetar te grupit.
        last = group[-1]
        conflicts = 0
        for m in group:
            conflicts |= self.met[m]
        candidates = free & ~conflicts & ~((1 << (last + 1)) - 1)

        # Renditja e javeve: partneri i dyte i lojtarit 0 rritet nga java ne jave.
        if gi == 0 and slot == 1 and week > 1:
            prev = self.schedule[week - 1][0][1]
            candidates &= ~((1 << (prev + 1)) - 1)

        # Prunim: duhen mjaftueshem kandidate per te mbushur grupin.
        if bin(candidates).count("1") < self.p - slot:
            self.backtracks += 1
            return False

        order = []
        while candidates:
            bit = candidates & -candidates
            candidates ^= bit
            order.append(bit.bit_length() - 1)
        if self.rng is not None:
            self.rng.shuffle(order)

        for player in order:
            self._place(player, group)
            if self._dfs(week, gi, slot + 1, free & ~(1 << player)):
                return True
            self._unplace(group)
        self.backtracks += 1
        return False


# ---------------------------------------------------------------------------
# Ndihmese per shfaqje
# ---------------------------------------------------------------------------

def format_schedule(schedule):
    if not schedule:
        return "(orar bosh)"
    g = len(schedule[0])
    cells = [[",".join(map(str, grp)) for grp in week] for week in schedule]
    width = max(len(c) for row in cells for c in row + [f"Group {g}"])
    head = " " * 9 + " | ".join(f"Group {i + 1}".ljust(width) for i in range(g))
    lines = [head, "-" * len(head)]
    for wi, row in enumerate(cells):
        lines.append(f"Week {wi + 1:<3} " + " | ".join(c.ljust(width) for c in row))
    return "\n".join(lines)


class SearchStats:
    def __init__(self):
        self.nodes = self.backtracks = self.restarts = 0


def run(g, p, w, timeout, restarts=False, node_limit=20000, seed=1):
    """
    Ekzekuton DFS per w jave.

    restarts=False: DFS klasik (rend leksikografik), kerkim i plote - nese
                    perfundon pa zgjidhje, vertetohet qe zgjidhja nuk ekziston.
    restarts=True:  DFS me rend te rastesishem te kandidateve; cdo prove ndalet
                    pas `node_limit` nyjeve dhe fillon nje e re, deri ne timeout.
                    Shmang "kurthet" ku DFS klasik ngec ne nje dege te keqe.
    """
    stats = SearchStats()
    rng = random.Random(seed) if restarts else None
    t0 = time.perf_counter()
    result, status = None, "timeout"
    while True:
        remaining = None if timeout is None else timeout - (time.perf_counter() - t0)
        if remaining is not None and remaining <= 0:
            break
        solver = SocialGolfersDFS(g, p, w, remaining, rng,
                                  node_limit if restarts else None)
        try:
            result = solver.solve()
            status = "zgjidhje" if result is not None else "nuk ka zgjidhje"
            break
        except SearchTimeout:
            break
        except NodeLimitReached:
            stats.restarts += 1
        finally:
            stats.nodes += solver.nodes
            stats.backtracks += solver.backtracks
    return result, status, stats, time.perf_counter() - t0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Social Golfers Problem me DFS + Backtracking")
    ap.add_argument("-g", type=int, default=8, help="numri i grupeve (default 8)")
    ap.add_argument("-p", type=int, default=4, help="lojtare per grup (default 4)")
    ap.add_argument("-w", type=int, default=None,
                    help="numri i javeve; pa kete, kerkohet w maksimal")
    ap.add_argument("-t", "--timeout", type=float, default=60.0,
                    help="kufiri kohor per cdo w ne sekonda (default 60)")
    ap.add_argument("-r", "--restarts", action="store_true",
                    help="DFS me rend te rastesishem dhe restart")
    ap.add_argument("--node-limit", type=int, default=20000,
                    help="nyje per cdo prove kur perdoret --restarts (default 20000)")
    ap.add_argument("--seed", type=int, default=1, help="seed per --restarts")
    args = ap.parse_args(argv)
    g, p = args.g, args.p
    n = g * p
    ub = upper_bound_weeks(g, p)
    mode = "DFS me restart (rend i rastesishem)" if args.restarts else "DFS klasik"
    print(f"Social Golfers: n={n} lojtare, g={g} grupe, p={p} lojtare/grup | {mode}")
    print(f"Kufiri teorik i siperm: w <= (n-1)/(p-1) = {ub}\n")

    def search(w):
        return run(g, p, w, args.timeout, args.restarts, args.node_limit, args.seed)

    if args.w is not None:
        result, status, s, el = search(args.w)
        print(f"w={args.w}: {status} | nyje={s.nodes:,} backtracks={s.backtracks:,} "
              f"restarte={s.restarts} koha={el:.2f}s")
        if result is not None:
            print()
            print(format_schedule(result))
            print(f"\nObjective f(S) = {objective(result)}  | valid = {is_valid(result, g, p)}")
        return 0

    best = None
    w = 1
    while w <= ub:
        result, status, s, el = search(w)
        print(f"w={w:>2}: {status:<16} nyje={s.nodes:>12,} backtracks={s.backtracks:>12,} "
              f"restarte={s.restarts:>5} koha={el:7.2f}s")
        if result is None:
            break
        best = result
        w += 1

    if best is not None:
        print(f"\nOrari me i gjate i gjetur: {len(best)} jave\n")
        print(format_schedule(best))
        print(f"\nObjective f(S) = {objective(best)}  | valid = {is_valid(best, g, p)}")
    return 0


if __name__ == "__main__":
    sys.setrecursionlimit(10000)
    sys.exit(main())
