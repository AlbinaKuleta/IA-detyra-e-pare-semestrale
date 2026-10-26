"""
Sudoku Solver - Breadth First Search (BFS) me Backtracking.

Reprezentimi:
    grid = lista me 81 numra, grid[r*9 + c] eshte vlera ne rreshtin r, kolonen c
    0 = qelize bosh

Variablat:  qelizat bosh X[r][c]
Domain-i:   {1, 2, ..., 9}
Kufizimet:  cdo rresht, cdo kolone dhe cdo kuti 3x3 ka numrat 1..9 pa perseritje
            (27 kufizime "all-different"), dhe qelizat e dhena (givens) nuk ndryshohen.

Perdorimi:
    python sudoku.py                    # zgjidh te gjitha nivelet
    python sudoku.py --level hard       # vetem nivelin Hard
    python sudoku.py --puzzle 53..7....6..195....98....6.8...6...34..8.3..17...2...6.6....28....419..5....8..79
"""

import argparse
import time
from collections import deque

from puzzles import PUZZLES, parse

DIGITS = range(1, 10)
ALL = 0b1111111110          # bitat 1..9 (bit i = numri i eshte i mundshem)


def row_of(i):
    return i // 9


def col_of(i):
    return i % 9


def box_of(i):
    return (i // 27) * 3 + (i % 9) // 3


# 27 njesite: 9 rreshta, 9 kolona, 9 kuti
UNITS = ([[r * 9 + c for c in range(9)] for r in range(9)]
         + [[r * 9 + c for r in range(9)] for c in range(9)]
         + [[i for i in range(81) if box_of(i) == b] for b in range(9)])


# ---------------------------------------------------------------------------
# Objective function
# ---------------------------------------------------------------------------

def objective(grid):
    """
    Objective function: numri i konflikteve ne nje grid te plote.

        f(S) = sum_{u ne 27 njesite} (9 - |vlerat e ndryshme ne u|)

    Sa me shume perseritje ne nje rresht/kolone/kuti, aq me i madh f.
    Nje grid i plote eshte zgjidhje atehere dhe vetem atehere kur f(S) = 0.
    """
    return sum(9 - len({grid[i] for i in unit}) for unit in UNITS)


def is_solution(grid, puzzle):
    return (all(v in DIGITS for v in grid)
            and all(p == 0 or p == g for p, g in zip(puzzle, grid))
            and objective(grid) == 0)


def is_consistent(grid):
    """Kontrollon qe numrat e dhene nuk perseriten ne asnje njesi."""
    for unit in UNITS:
        vals = [grid[i] for i in unit if grid[i]]
        if len(vals) != len(set(vals)):
            return False
    return True


# ---------------------------------------------------------------------------
# BFS me Backtracking
# ---------------------------------------------------------------------------

def candidates(grid):
    """
    Per secilen qelize bosh kthen bitmask-un e vlerave te lejuara
    (forward checking: largohen vlerat qe jane ne te njejtin rresht/kolone/kuti).
    """
    rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
    for i, v in enumerate(grid):
        if v:
            bit = 1 << v
            rows[row_of(i)] |= bit
            cols[col_of(i)] |= bit
            boxes[box_of(i)] |= bit
    return {i: ALL & ~(rows[row_of(i)] | cols[col_of(i)] | boxes[box_of(i)])
            for i, v in enumerate(grid) if v == 0}


def bfs_solve(puzzle, max_states=None):
    """
    BFS mbi gjendjet e pjesshme.

    - Gjendja: grid-i (tuple me 81 vlera).
    - Ne cdo nivel te pemes mbushet nje qelize bosh: ajo me me se paku vlera
      te mundshme (MRV - Minimum Remaining Values).
    - Femijet e nje gjendjeje jane te gjitha vlerat e lejuara per ate qelize.
    - Gjendjet ruhen ne nje radhe FIFO (deque), prandaj eksplorohen nivel pas
      niveli: te gjitha gjendjet me k qeliza te mbushura para atyre me k+1.

    Backtracking: nese nje gjendje ka nje qelize pa asnje vlere te mundshme
    (dead end), ajo hidhet poshte dhe dega nuk vazhdohet me - kerkimi "kthehet"
    te gjendjet e tjera ne radhe. Keshtu nuk ruhen kurre gjendje jo-valide.

    Kthen (zgjidhja ose None, statistikat).
    """
    stats = {"expanded": 0, "generated": 1, "dead_ends": 0,
             "max_frontier": 1, "per_level": []}
    if not is_consistent(puzzle):
        return None, stats

    frontier = deque([tuple(puzzle)])
    level_size, next_level = 1, 0
    stats["per_level"].append(1)

    while frontier:
        grid = frontier.popleft()
        level_size -= 1
        stats["expanded"] += 1

        cand = candidates(grid)
        if not cand:                         # nuk ka qeliza bosh -> qellimi
            return list(grid), stats

        # MRV: qeliza me me se paku kandidate
        cell = min(cand, key=lambda i: bin(cand[i]).count("1"))
        options = cand[cell]
        if options == 0:                     # MRV gjen qelizen pa kandidate
            stats["dead_ends"] += 1          # backtrack: dega hidhet poshte
        else:
            for v in DIGITS:
                if options >> v & 1:
                    child = list(grid)
                    child[cell] = v
                    frontier.append(tuple(child))
                    next_level += 1
                    stats["generated"] += 1

        stats["max_frontier"] = max(stats["max_frontier"], len(frontier))
        if max_states is not None and stats["generated"] > max_states:
            raise MemoryError("BFS kaloi kufirin e gjendjeve")

        if level_size == 0 and frontier:     # niveli u perfundua
            stats["per_level"].append(next_level)
            level_size, next_level = next_level, 0

    return None, stats


# ---------------------------------------------------------------------------
# Shfaqja
# ---------------------------------------------------------------------------

def format_grid(grid):
    lines = []
    for r in range(9):
        if r and r % 3 == 0:
            lines.append("------+-------+------")
        row = ""
        for c in range(9):
            if c and c % 3 == 0:
                row += "| "
            v = grid[r * 9 + c]
            row += (str(v) if v else ".") + " "
        lines.append(row.rstrip())
    return "\n".join(lines)


def side_by_side(a, b, gap="     "):
    la, lb = a.split("\n"), b.split("\n")
    return "\n".join(x.ljust(21) + gap + y for x, y in zip(la, lb))


def solve_and_print(name, puzzle, verbose=False):
    empty = puzzle.count(0)
    print(f"=== {name} | {81 - empty} te dhena, {empty} qeliza bosh ===")
    t0 = time.perf_counter()
    solution, st = bfs_solve(puzzle)
    elapsed = time.perf_counter() - t0
    if solution is None:
        print(format_grid(puzzle))
        print("Nuk ka zgjidhje.\n")
        return
    print(side_by_side("Sudoku".ljust(21) + "\n" + format_grid(puzzle),
                       "Zgjidhja".ljust(21) + "\n" + format_grid(solution)))
    print(f"\nObjective f(S) = {objective(solution)} | valid = {is_solution(solution, puzzle)}")
    print(f"Gjendje te zgjeruara: {st['expanded']:,} | te gjeneruara: {st['generated']:,} | "
          f"dead ends (backtracks): {st['dead_ends']:,}")
    print(f"Frontier maksimal: {st['max_frontier']:,} | koha: {elapsed:.3f}s")
    if verbose:
        print(f"Gjendje per nivel te pemes: {st['per_level']}")
    print()


def main():
    ap = argparse.ArgumentParser(description="Sudoku Solver me BFS + Backtracking")
    ap.add_argument("--level", choices=["easy", "medium", "hard", "all"], default="all")
    ap.add_argument("--puzzle", help="sudoku si string me 81 karaktere (0 ose . = bosh)")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="shfaq numrin e gjendjeve ne cdo nivel te pemes BFS")
    args = ap.parse_args()

    if args.puzzle:
        solve_and_print("Sudoku i dhene", parse(args.puzzle), args.verbose)
        return
    levels = ["easy", "medium", "hard"] if args.level == "all" else [args.level]
    for level in levels:
        for k, p in enumerate(PUZZLES[level], 1):
            solve_and_print(f"{level.capitalize()} #{k}", parse(p), args.verbose)


if __name__ == "__main__":
    main()
