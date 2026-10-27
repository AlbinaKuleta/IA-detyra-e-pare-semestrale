# Detyra 3 – Latin Square

**Teknikat e painformuara të kërkimit (Uninformed Search Techniques)**

## 1. Përshkrimi i problemit

Një katror latin është një rrjetë `n × n` e mbushur me `n` numra të ndryshëm, ku secili numër paraqitet **saktësisht një herë** në çdo rresht dhe në çdo kolonë. Për një hyrje `n`, programi printon një matricë `n × n` me numrat nga 1 deri në `n`.

**Shembull:** hyrja `5` jep daljen e mëposhtme, e njëjtë me shembullin e detyrës:

```
5 1 2 3 4
4 5 1 2 3
3 4 5 1 2
2 3 4 5 1
1 2 3 4 5
```

> Shembulli në tekstin e detyrës shfaq vetëm 4 rreshta. Për `n = 5` duhen 5 rreshta, dhe rreshti i fundit `1 2 3 4 5` vazhdon të njëjtin model ciklik.

## 2. Modelimi i problemit

Problemi modelohet si **Constraint Satisfaction Problem (CSP)**, i cili zgjidhet me kërkim në hapësirën e gjendjeve:

| Elementi | Në këtë problem |
|---|---|
| **Gjendja** | Rrjeta e mbushur pjesërisht: qelizat e para `d` (rresht pas rreshti) kanë vlerë dhe nuk ka asnjë konflikt |
| **Gjendja fillestare** | Rrjeta bosh (`d = 0`) |
| **Veprimi (operatori)** | Vendos një numër `1..n` në qelizën e radhës, nëse ai nuk është ende në rreshtin ose kolonën e saj |
| **Testi i qëllimit** | Të gjitha `n²` qelizat janë të mbushura |
| **Thellësia** | Numri i qelizave të mbushura. Çdo zgjidhje është saktësisht në thellësinë `n²` |

### Kufizimet

1. Çdo rresht ka numrat `1..n` pa përsëritje (`n` kufizime).
2. Çdo kolonë ka numrat `1..n` pa përsëritje (`n` kufizime).

Gjithsej janë `2n` kufizime **all-different**.

## 3. Reprezentimi

```
grid[r][c] ∈ {0, 1, ..., n}      0 = qelizë bosh
```

- **Variablat:** qelizat `X[r][c]`, për `r, c = 0..n−1`. Ka gjithsej `n²` variabla.
- **Domain-i:** `D = {1, 2, …, n}`.
- **Renditja e variablave:** qelizat mbushen rresht pas rreshti, pra qeliza në thellësinë `d` është `(d div n, d mod n)`.
- **Struktura ndihmëse:** për çdo rresht dhe kolonë mbahet një bitmask me numrat e përdorur (`row_used`, `col_used`). Kështu kontrolli i kufizimeve bëhet me një operacion `AND`.

## 4. Objective function

```
f(S) = Σ_r (n − |vlerat e ndryshme në rreshtin r|) + Σ_c (n − |vlerat e ndryshme në kolonën c|)
```

- `f(S)` numëron përsëritjet në rreshta dhe kolona.
- `f(S) = 0` vlen atëherë dhe vetëm atëherë kur rrjeta e plotë është katror latin.
- Qëllimi është **minimizimi** i `f(S)` deri në 0.

Implementimi gjendet te `objective()` në [latin_square.py](latin_square.py). Pas çdo zgjidhjeje, programi shtyp `f(S) = 0` dhe `valid = True` si verifikim.

## 5. Landscape

Rezultatet merren me `python landscape.py -n <n>`.

### Madhësia e hapësirës së kërkimit

| n | Naive `n^(n²)` | Permutacione rreshtash `(n!)^n` | Katrorë latin `L(n)` | Pjesa që janë zgjidhje |
|---|---|---|---|---|
| 4 | ~10^9.6 | ~10^5.5 | 576 | 1.7·10⁻³ |
| 5 | ~10^17.5 | ~10^10.4 | 161,280 | 6.5·10⁻⁶ |
| 7 | ~10^41.4 | ~10^25.9 | ~6.1·10¹³ | 7.4·10⁻¹³ |
| 10 | ~10^100 | ~10^65.6 | ~10^37 | 2.5·10⁻²⁹ |

Zgjidhje ka shumë (katrori ciklik ekziston për çdo `n`). Megjithatë, pjesa e gjendjeve që janë zgjidhje bie shumë shpejt me rritjen e `n`.

### Pema e kërkimit (n = 4)

Numri i gjendjeve të vlefshme në çdo thellësi:

```
d:      0  1   2   3   4   5    6    7    8    9   10   11   12   13   14   15   16
gjendje 1  4  12  24  24  72  168  264  216  432  720  864  576  576  576  576  576
```

Gjithsej ka 5,681 gjendje. Në thellësinë 16 janë të 576 katrorët latin.

### Fitness landscape

Kjo analizë përdor reprezentimin me permutacione rreshtash. Fqinj quhen dy gjendje që dallojnë vetëm nga një swap i dy qelizave në të njëjtin rresht.

| n | `f(S)` e gjendjeve të rastësishme | Fqinj më të mirë / plateau / më të këqij | Hill climbing arrin `f = 0` |
|---|---|---|---|
| 4 | 0–10, mesatarja 5.1 | 40% / 29% / 31% | 32 nga 50 |
| 5 | 3–14, mesatarja 8.2 | 39% / 32% / 29% | 22 nga 50 |
| 7 | 8–24, mesatarja 16.5 | 33% / 32% / 35% | 15 nga 50 |
| 10 | 23–45, mesatarja 34.9 | 32% / 37% / 31% | 3 nga 50 |

Landscape-i ka shumë **plateau** (rreth 30–37% e fqinjëve kanë të njëjtin `f`) dhe **minimume lokale** me `f = 2–7`. Sa më i madh `n`, aq më shpesh kërkimi lokal ngec. Kërkimi sistematik (IDDFS me backtracking) e gjen zgjidhjen gjithmonë.

## 6. Iterative Deepening DFS (IDDFS) me Backtracking

Implementimi gjendet te klasa `LatinSquareIDDFS` në [latin_square.py](latin_square.py).

**Algoritmi:**
- IDDFS ekzekuton **Depth-Limited Search (DLS)** me kufi `L = 0, 1, 2, …`. Në çdo iteracion, DFS nuk shkon më thellë se `L`.
- Nëse ndonjë degë ndalet për shkak të kufirit (**cutoff**), kufiri rritet dhe kërkimi fillon nga e para.
- **Backtracking:** brenda DLS, një vlerë provohet vetëm nëse nuk është ende në rreshtin dhe kolonën e qelizës. Nëse asnjë vlerë nuk përshtatet, hiqet vlera e fundit dhe provohet tjetra.

```
IDDFS(n):
    për L = 0, 1, 2, ...:
        rezultati ← DLS(rrjeta bosh, 0, L)
        nëse rezultati = zgjidhje → kthe zgjidhjen
        nëse rezultati = dështim (pa cutoff) → kthe "nuk ka zgjidhje"

DLS(rrjeta, d, L):
    nëse d = n² → kthe zgjidhje
    nëse d = L  → kthe cutoff
    (r, c) ← qeliza e d-të
    për çdo v që nuk është në rreshtin r dhe kolonën c:
        vendos v
        nëse DLS(rrjeta, d+1, L) = zgjidhje → kthe zgjidhje
        hiq v                                          ← backtracking
    kthe cutoff/dështim
```

### Ndërprerja e hershme (early stop)

`DLS(L)` ka vetëm tri përgjigje të mundshme: **zgjidhje**, **cutoff** ose **dështim**. Te katrori latin, çdo zgjidhje është saktësisht në thellësinë `n²`, prandaj një iteracion me `L < n²` nuk mund të gjejë zgjidhje.

Sapo ndodh cutoff-i i parë, përgjigjja e iteracionit është tashmë e sigurt ("cutoff"), dhe pjesa tjetër e pemës nuk ka nevojë të eksplorohet. Rezultati është **identik** me IDDFS klasik, por pa punën eksponenciale të iteracioneve të panevojshme. IDDFS klasik mund të ekzekutohet me opsionin `--classic`.

| n | IDDFS klasik (`--classic`) | IDDFS me ndërprerje të hershme |
|---|---|---|
| 3 | 325 nyje | 55 nyje |
| 4 | 24,861 nyje | 153 nyje |
| 5 | 13,505,911 nyje, ~20 s | 351 nyje, ~0.001 s |
| 6+ | nuk përfundon në kohë të arsyeshme | p.sh. n = 30: 406,351 nyje, ~2 s |

IDDFS klasik në iteracionin `L` i viziton **të gjitha** gjendjet e vlefshme me thellësi `≤ L`. Për `n = 4` kjo do të thotë 24,844 gjendje para iteracionit të fundit, ndërsa vetë pema ka vetëm 5,681 gjendje.

### Renditja e vlerave

- `cyclic` (default): për qelizën `(r, c)` provohet së pari vlera `((c − r − 1) mod n) + 1`, pastaj vlerat e tjera me radhë. Kjo jep katrorin ciklik të shembullit të detyrës pa asnjë backtrack.
- `asc`: vlerat provohen `1, 2, …, n`. Kjo është renditja naive dhe tregon backtracking-un në veprim:

| n | Nyje në iteracionin e fundit | Backtracks | Nyje gjithsej | Koha |
|---|---|---|---|---|
| 5 | 38 | 12 | 453 | < 0.01 s |
| 7 | 132 | 82 | 2,966 | < 0.01 s |
| 10 | 1,465 | 1,364 | 52,360 | ~0.1 s |
| 12 | 9,491 | 9,346 | 739,006 | ~1.6 s |

## 7. Ekzekutimi

Kërkohet Python 3.8+ dhe nuk ka nevojë për librari të jashtme.

```bash
cd task3

# Hyrja n = 5 (si ne shembull)
python latin_square.py 5

# Renditje naive e vlerave (me backtracking)
python latin_square.py 7 --order asc

# Statistikat per cdo iteracion te IDDFS
python latin_square.py 4 --order asc -v

# IDDFS klasik pa nderprerje te hershme (vetem per n <= 5)
python latin_square.py 4 --classic

# Landscape
python landscape.py -n 5
python landscape.py -n 7 --tree-n 3
```

Opsionet: `n` (madhësia), `--order cyclic|asc`, `--classic`, `--step` (sa rritet kufiri në çdo iteracion), `-v`.
