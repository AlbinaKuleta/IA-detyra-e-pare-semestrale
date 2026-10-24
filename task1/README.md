# Detyra e parë semestrale – Social Golfers Problem

**Teknikat e painformuara të kërkimit (Uninformed Search Techniques)**

## 1. Përshkrimi i problemit

32 lojtarë golfi luajnë një herë në javë, gjithmonë në grupe me nga 4. Për sa javë mund të luajnë ashtu që asnjë çift lojtarësh të mos jetë në të njëjtin grup më shumë se një herë?

Në formë të përgjithshme: a mund të planifikohen `n = g × p` lojtarë në `g` grupe me nga `p` lojtarë për `w` javë, ashtu që asnjë çift të mos takohet më shumë se një herë? Instanca e detyrës është **g = 8, p = 4, n = 32**.

## 2. Modelimi i problemit

Problemi modelohet si **Constraint Satisfaction Problem (CSP)**, i cili zgjidhet me kërkim në hapësirën e gjendjeve:

| Elementi | Në këtë problem |
|---|---|
| **Gjendja** | Orar i mbushur pjesërisht: disa slote kanë lojtarë, të tjerat janë bosh |
| **Gjendja fillestare** | Java 1 është e fiksuar `{0,1,2,3}, {4,5,6,7}, …`, ndërsa javët e tjera janë bosh |
| **Veprimi (operatori)** | Vendos një lojtar në slotin e radhës bosh |
| **Testi i qëllimit** | Të gjitha `w × g × p` slotet janë mbushur dhe asnjë kufizim nuk shkelet |
| **Kostoja** | Nuk ka rëndësi, sepse kërkohet vetëm një zgjidhje valide |

### Kufizimet

1. Brenda një jave, çdo lojtar paraqitet **saktësisht një herë**.
2. Çdo grup ka **saktësisht p** lojtarë.
3. Çdo çift lojtarësh `(i, j)` takohet në të njëjtin grup **të shumtën një herë** gjatë gjithë javëve.

## 3. Reprezentimi

```
schedule[week][group] = [x1, x2, ..., xp]      xi ∈ {0, ..., n-1}
```

- **Variablat:** çdo slot `X[w][g][k]`, pra lojtari në javën `w`, grupin `g` dhe pozitën `k`. Gjithsej ka `w · g · p` variabla (për w = 10 janë 320).
- **Domain-i:** `D = {0, 1, …, n-1}` = `{0, …, 31}`.
- **Struktura ndihmëse:** për çdo lojtar `i` mbahet bitmask-u `met[i]` me lojtarët që i ka takuar deri tani. Kështu kontrolli i kufizimit 3 bëhet me një operacion `AND`.

Shembull (java 1 nga detyra):

| | Group 1 | Group 2 | Group 3 | Group 4 | Group 5 | Group 6 | Group 7 | Group 8 |
|---|---|---|---|---|---|---|---|---|
| Week 1 | 0,1,2,3 | 4,5,22,23 | 6,7,20,21 | 8,25,26,27 | 9,10,11,24 | 12,13,15,30 | 14,28,29,31 | … |

## 4. Objective function

Funksioni objektiv numëron **takimet e përsëritura**:

```
f(S) = Σ_{i<j} max(0, takime(i, j) − 1)
```

ku `takime(i, j)` është numri i javëve në të cilat `i` dhe `j` janë në të njëjtin grup.

- `f(S) = 0` vlen atëherë dhe vetëm atëherë kur orari `S` është zgjidhje valide.
- Qëllimi i problemit të optimizimit është të **maksimizohet w** për të cilin ekziston një orar me `f(S) = 0`.

Implementimi gjendet te `objective()` në [social_golfers.py](social_golfers.py).

### Kufiri i sipërm

Çdo javë, lojtari takon `p − 1 = 3` lojtarë të rinj, dhe ka vetëm `n − 1 = 31` lojtarë të tjerë. Prandaj:

```
w ≤ ⌊(n − 1) / (p − 1)⌋ = ⌊31 / 3⌋ = 10
```

Edhe numërimi i çifteve jep të njëjtin kufi: ka `C(32,2) = 496` çifte, dhe çdo javë konsumon `8 · C(4,2) = 48` prej tyre, prandaj `w ≤ 10.33`. Në literaturë dihet që për 8-4 përgjigja është **w = 10** (gjetur me metoda konstruktive në vitin 2004).

## 5. Landscape

Rezultatet merren me `python landscape.py` (g=8, p=4, w=10):

### Madhësia e hapësirës së kërkimit

| Reprezentimi | Numri i gjendjeve |
|---|---|
| Naive: çdo slot merr cilindo lojtar, `n^(n·w)` | ~10^481.7 |
| Çdo javë është një permutacion, `(n!)^w` | ~10^354.2 |
| Çdo javë është një ndarje në grupe, `P^w`, ku `P = n!/((p!)^g · g!) ≈ 5.93·10^19` | ~10^197.7 |
| Me thyerje simetrish (java 1 fikse, javët pa renditje), `P^(w−1)/(w−1)!` | ~10^172.4 |

Edhe pas thyerjes së simetrive, hapësira është shumë e madhe për t'u kërkuar plotësisht. Për këtë arsye janë thelbësore **prunimi** dhe **thyerja e simetrive**.

### Fitness landscape (orare të rastësishme, w = 10)

- Mbi 2000 orare të rastësishme, `f(S)` del në intervalin 141–187, me mesatare ≈ 163. Asnjë orar i rastësishëm nuk është valid.
- Shpërndarja ka formë "kambane" të ngushtë, larg nga 0. Zgjidhjet valide janë "gjilpëra" të izoluara në një landscape shumë të gjerë.
- Fqinjësia (swap i dy lojtarëve në të njëjtën javë) jep 4480 fqinj për gjendje. Rreth 38% prej tyre janë më të mirë, ≈22% të barabartë (**plateau**) dhe ≈40% më të këqij. Larg zgjidhjes ka shumë drejtime përmirësimi, por pjesa e madhe e plateau-ve tregon se afër `f = 0` kërkimi lokal ngec lehtë.
- Me `w = 10` përdoren 480 nga 496 çiftet (96.8%), pra problemi është jashtëzakonisht i kufizuar.

## 6. Depth First Search (DFS) me Backtracking

Implementimi gjendet te klasa `SocialGolfersDFS` në [social_golfers.py](social_golfers.py).

**Algoritmi:** sloti mbushen me radhë, `java → grupi → pozita`. Për çdo slot provohen kandidatët e vlefshëm një nga një. Nëse një degë nuk ka më kandidatë, bëhet **backtrack**: hiqet lojtari i fundit, rikthehet `met[]` dhe provohet kandidati tjetër.

```
DFS(java, grupi, pozita):
    nëse të gjitha javët janë mbushur → kthe SUKSES
    kandidatët = lojtarë të lirë këtë javë
                 ∩ më të mëdhenj se i fundit në grup
                 ∩ që nuk e kanë takuar asnjë anëtar të grupit
    nëse |kandidatët| < slotet e mbetura në grup → BACKTRACK (prunim)
    për çdo kandidat c:
        vendos c, përditëso met[]
        nëse DFS(sloti i radhës) → SUKSES
        hiq c, rikthe met[]          ← backtracking
    kthe DËSHTIM
```

**Thyerja e simetrive** eliminon vetëm kopjet ekuivalente, prandaj asnjë zgjidhje nuk humbet:
- lojtarët brenda grupit renditen në rend rritës;
- çdo grup fillon me lojtarin më të vogël të lirë, kështu grupet janë të renditura;
- java 1 është e fiksuar;
- javët renditen sipas partnerit të dytë të lojtarit 0.

**Dy variante:**
1. **DFS klasik** (default): kandidatët provohen në rend leksikografik. Kërkimi është i plotë, pra nëse mbaron pa zgjidhje, kjo vërteton që zgjidhja nuk ekziston.
2. **DFS me restart** (`--restarts`): kandidatët provohen në rend të rastësishëm. Çdo provë ndërpritet pas `node_limit` nyjeve dhe fillon një provë e re. Ky variant shmang "kurthet" ku DFS klasik ngec në një degë të keqe herët në pemë.

## 7. Rezultatet

| Instanca | Varianti | w maksimal i gjetur | Koha |
|---|---|---|---|
| 3-3 (9 lojtarë) | DFS klasik | **4** (= kufiri i sipërm) | < 0.01 s |
| 4-4 (16 lojtarë) | DFS klasik | **5** (= kufiri i sipërm) | < 0.01 s |
| 8-4 (32 lojtarë) | DFS klasik | **5** (w=6 nuk mbaron brenda 60 s) | < 0.01 s |
| 8-4 (32 lojtarë) | DFS me restart | **7** | ~22 s |

DFS klasik për 8-4 i ndërton javët 2–5 duke i mbajtur dy gjysmat `{0..15}` dhe `{16..31}` të ndara. Kjo degë nuk mund të vazhdojë më tej, por DFS-ja duhet ta eksplorojë të gjithë nën-pemën e saj para se të kthehet aq lart. Me rend të rastësishëm dhe restart, gjenden orare deri në **7 javë**. Optimumi i njohur prej 10 javësh kërkon teknika më të avancuara (propagim kufizimesh, konstruksione algjebrike), që dalin jashtë kërkimit të painformuar.

Shembull i një orari me 7 javë (valid, `f(S) = 0`):

```
Week 1   0,1,2,3     | 4,5,6,7     | 8,9,10,11   | 12,13,14,15 | 16,17,18,19 | 20,21,22,23 | 24,25,26,27 | 28,29,30,31
Week 2   0,4,13,29   | 1,14,23,30  | 2,8,22,27   | 3,20,24,28  | 5,12,18,21  | 6,9,17,25   | 7,11,19,26  | 10,15,16,31
Week 3   0,5,24,30   | 1,9,20,29   | 2,7,25,31   | 3,10,18,23  | 4,12,16,22  | 6,11,13,28  | 8,14,17,26  | 15,19,21,27
Week 4   0,10,26,28  | 1,4,21,25   | 2,17,20,30  | 3,13,22,31  | 5,9,23,27   | 6,12,19,29  | 7,8,15,18   | 11,14,16,24
Week 5   0,14,22,25  | 1,18,26,31  | 2,11,21,29  | 3,6,15,30   | 4,17,27,28  | 5,10,19,20  | 7,9,12,24   | 8,13,16,23
Week 6   0,16,20,27  | 1,8,12,28   | 2,19,23,24  | 3,5,25,29   | 4,9,15,26   | 6,14,21,31  | 7,10,13,17  | 11,18,22,30
Week 7   0,17,23,31  | 1,6,10,27   | 2,5,13,26   | 3,4,8,19    | 7,16,21,30  | 9,14,18,28  | 11,12,20,25 | 15,22,24,29
```

## 8. Ekzekutimi

Kërkohet Python 3.8+ dhe nuk ka nevojë për librari të jashtme.

```bash
cd task1

# 8 grupe x 4 lojtare: gjen w maksimal me DFS klasik
python social_golfers.py

# DFS me restart (gjen deri ne 7 jave)
python social_golfers.py --restarts -t 60

# Nje w konkret
python social_golfers.py -g 8 -p 4 -w 6 --restarts

# Instanca te vogla
python social_golfers.py -g 3 -p 3
python social_golfers.py -g 4 -p 4

# Landscape
python landscape.py
python landscape.py -w 7 --samples 5000
```

Opsionet: `-g` (grupe), `-p` (lojtarë për grup), `-w` (javë), `-t` (timeout për çdo w, në sekonda), `--restarts`, `--node-limit`, `--seed`.
