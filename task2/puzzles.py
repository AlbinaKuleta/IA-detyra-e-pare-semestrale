"""
Sudoku per tri nivelet: Easy, Medium, Hard.

Cdo sudoku jepet si string me 81 karaktere (rresht pas rreshti),
ku "0" ose "." eshte qelize bosh.

Nivelet jane zgjedhur sipas veshtiresise per kerkimin:
  Easy   - zgjidhen pa asnje degezim (cdo qelize ka vetem nje kandidat ne rradhe)
  Medium - pak degezim, qindra/mijera gjendje
  Hard   - shume degezim, dhjetera mijera gjendje
"""

PUZZLES = {
    "easy": [
        "530070000600195000098000060800060003400803001700020006060000280000419005000080079",
        "003020600900305001001806400008102900700000008006708200002609500800203009005010300",
    ],
    "medium": [
        "000000907000420180000705026100904000050000040000507009920108000034059000507000000",
        "020608000580009700000040000370000500600000004008000013000020000009800036000306090",
    ],
    "hard": [
        # "Golden Nugget"
        "000000039000001005003050800008090006070002000100400000009080050020000600400700000",
        # "World's hardest sudoku" (Arto Inkala, 2012)
        "800000000003600000070090200050007000000045700000100030001000068008500010090000400",
    ],
}


def parse(puzzle):
    """String me 81 karaktere -> lista me 81 numra (0 = bosh)."""
    s = [c for c in puzzle if c in "0123456789."]
    if len(s) != 81:
        raise ValueError(f"Sudoku duhet te kete 81 qelize, jo {len(s)}")
    return [0 if c == "." else int(c) for c in s]
