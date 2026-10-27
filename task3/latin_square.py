"""
Latin Square - Iterative Deepening Depth First Search (IDDFS) me Backtracking.

Problemi: per nje hyrje n, te ndertohet nje matrice n x n me numrat 1..n,
ku secili numer paraqitet saktesisht nje here ne cdo rresht dhe ne cdo kolone.

Reprezentimi:
    grid[r][c] = numri ne rreshtin r, kolonen c   (0 = qelize bosh)

Variablat:  qelizat X[r][c], r, c = 0..n-1   (n^2 variabla)
Domain-i:   {1, 2, ..., n}
Kufizimet:  cdo rresht dhe cdo kolone ka numrat 1..n pa perseritje
            (2n kufizime "all-different").

Perdorimi:
    python latin_square.py 5             # n = 5
    python latin_square.py 7 -v          # shfaq statistikat per cdo iteracion
"""

import argparse
import sys
import time


# ---------------------------------------------------------------------------
# Objective function
# ---------------------------------------------------------------------------

def objective(grid):
    """
    Objective function: numri i perseritjeve ne rreshta dhe kolona.

        f(S) = sum_r (n - |vlerat e ndryshme ne rreshtin r|)
             + sum_c (n - |vlerat e ndryshme ne kolonen c|)

    Nje grid i plote eshte katror latin atehere dhe vetem atehere kur f(S) = 0.
    """
    n = len(grid)
    rows = sum(n - len(set(row)) for row in grid)
    cols = sum(n - len({grid[r][c] for r in range(n)}) for c in range(n))
    return rows + cols


def is_latin(grid):
    n = len(grid)
    return (all(v in range(1, n + 1) for row in grid for v in row)
            and objective(grid) == 0)


# ---------------------------------------------------------------------------
# IDDFS me Backtracking
# ---------------------------------------------------------------------------

class LatinSquareIDDFS:
    """
    Gjendja: grid-i i mbushur pjeserisht; qelizat mbushen me radhe
    (rresht pas rreshti), keshtu thellesia e gjendjes = numri i qelizave
    te mbushura. Qellimi eshte ne thellesine n^2.

    IDDFS: ekzekuton Depth-Limited Search (DLS) me kufi L = 0, 1, 2, ...
    Ne cdo iteracion DFS nuk shkon me thelle se L. Nese ndonje dege
    ndalet per shkak te kufirit (cutoff), kufiri rritet dhe kerkimi fillon
    nga e para.

    Backtracking: brenda DLS, nje vlere provohet vetem nese nuk eshte
    ende ne rreshtin dhe kolonen e qelizes; nese asnje vlere nuk pershtatet,
    hiqet vlera e fundit dhe provohet tjetra.

    Per efikasitet, per cdo rresht dhe kolone mbahet nje bitmask
    me numrat e perdorur.

    Nderprerja e hershme (early_stop=True): DLS(L) kthen vetem njeren nga
    tri pergjigjet: "zgjidhje", "cutoff" ose "deshtim". Te katrori latin
    cdo zgjidhje eshte saktesisht ne thellesine n^2, prandaj nje iteracion
    me L < n^2 nuk mund te gjeje zgjidhje. Sapo ndodh cutoff-i i pare,
    pergjigjja e iteracionit eshte e sigurt ("cutoff") dhe pjesa tjeter e
    pemes nuk ka nevoje te eksplorohet. Rezultati eshte identik me IDDFS
    klasik, por pa eksplorimin eksponencial te iteracioneve te panevojshme.

    Renditja e vlerave (order):
      "cyclic" - per qelizen (r, c) provohet se pari vlera ((c - r - 1) mod n) + 1,
                 pastaj te tjerat me radhe. Kjo jep zgjidhjen ciklike te shembullit
                 te detyres pa asnje backtrack.
      "asc"    - vlerat provohen 1, 2, ..., n (renditje naive, me shume backtracking).
    """

    def __init__(self, n, step=1, early_stop=True, order="cyclic"):
        self.n = n
        self.step = step
        self.early_stop = early_stop
        self.order = order
        self.iterations = []        # statistika per cdo iteracion

    def solve(self):
        n = self.n
        goal_depth = n * n
        limit = 0
        while True:
            self.grid = [[0] * n for _ in range(n)]
            self.row_used = [0] * n
            self.col_used = [0] * n
            self.nodes = self.backtracks = 0
            self.cutoff = False

            found = self._dls(0, limit)
            self.iterations.append((limit, self.nodes, self.backtracks))
            if found:
                return [row[:] for row in self.grid]
            if not self.cutoff:
                return None              # e gjithe hapesira u eksplorua
            limit = min(limit + self.step, goal_depth)

    def _dls(self, depth, limit):
        """Depth-Limited Search me backtracking."""
        self.nodes += 1
        n = self.n
        if depth == n * n:
            return True                  # te gjitha qelizat u mbushen
        if depth == limit:
            self.cutoff = True           # kufiri u arrit, por jo qellimi
            return False

        r, c = divmod(depth, n)
        used = self.row_used[r] | self.col_used[c]
        if self.order == "cyclic":
            start = (c - r - 1) % n
            values = [(start + k) % n + 1 for k in range(n)]
        else:
            values = range(1, n + 1)
        for v in values:
            bit = 1 << v
            if used & bit:
                continue                 # shkel kufizimin -> nuk provohet
            self.grid[r][c] = v
            self.row_used[r] |= bit
            self.col_used[c] |= bit
            if self._dls(depth + 1, limit):
                return True
            self.grid[r][c] = 0          # backtrack
            self.row_used[r] &= ~bit
            self.col_used[c] &= ~bit
            if self.cutoff and self.early_stop and limit < n * n:
                return False             # pergjigjja "cutoff" eshte e sigurt
        self.backtracks += 1
        return False


# ---------------------------------------------------------------------------
# Shfaqja
# ---------------------------------------------------------------------------

def format_grid(grid):
    width = len(str(len(grid)))
    return "\n".join(" ".join(str(v).rjust(width) for v in row) for row in grid)


def main():
    ap = argparse.ArgumentParser(description="Latin Square me IDDFS + Backtracking")
    ap.add_argument("n", type=int, nargs="?", default=5, help="madhesia e katrorit (default 5)")
    ap.add_argument("--step", type=int, default=1,
                    help="sa rritet kufiri i thellesise ne cdo iteracion (default 1)")
    ap.add_argument("--order", choices=["cyclic", "asc"], default="cyclic",
                    help="renditja e vlerave: cyclic (default) ose asc (1..n)")
    ap.add_argument("--classic", action="store_true",
                    help="IDDFS klasik pa nderprerje te hershme (eksponencial, vetem n <= 5)")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="shfaq statistikat per cdo iteracion te IDDFS")
    args = ap.parse_args()
    n = args.n
    if n < 1:
        ap.error("n duhet te jete >= 1")
    sys.setrecursionlimit(max(1000, n * n + 100))

    solver = LatinSquareIDDFS(n, args.step, early_stop=not args.classic, order=args.order)
    t0 = time.perf_counter()
    grid = solver.solve()
    elapsed = time.perf_counter() - t0

    print(f"Hyrja: {n}\n\nDalja:")
    print(format_grid(grid) if grid else "Nuk ka zgjidhje.")

    total_nodes = sum(it[1] for it in solver.iterations)
    total_bt = sum(it[2] for it in solver.iterations)
    last = solver.iterations[-1]
    print(f"\nObjective f(S) = {objective(grid)} | katror latin valid = {is_latin(grid)}")
    print(f"Iteracione IDDFS: {len(solver.iterations)} (kufiri final L = {last[0]})")
    print(f"Nyje ne iteracionin e fundit: {last[1]:,} | backtracks: {last[2]:,}")
    print(f"Nyje gjithsej (te gjitha iteracionet): {total_nodes:,} | "
          f"backtracks gjithsej: {total_bt:,} | koha: {elapsed:.3f}s")

    if args.verbose:
        print("\n  L  |     nyje | backtracks")
        for limit, nodes, bt in solver.iterations:
            print(f"{limit:4} | {nodes:8,} | {bt:10,}")


if __name__ == "__main__":
    main()
