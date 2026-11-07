"""Independent random brute force for R4 Theorems 1-3 (review aid, not project evidence)."""
import itertools, random, sys
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
Q, D = 3, 3          # 3 keys, ternary keys and y
SUBSETS = [frozenset(s) for k in range(1, Q+1) for s in itertools.combinations(range(Q), k)]

def accepts(rows, F):
    for X in F:
        cnt = [1] + [0]*(D-1)            # target is all zero
        for r in rows:
            if all(r[j] == 0 for j in X): cnt[r[Q]] += 1
        if any(cnt[0] <= cnt[v] for v in range(1, D)): return False
    return True

def width(F):
    w = 0
    for j in range(Q):
        Fj = [X for X in F if j in X]
        for k in range(len(Fj), 0, -1):
            if any(all(not (a <= b or b <= a) for a, b in itertools.combinations(c, 2))
                   for c in itertools.combinations(Fj, k)):
                w = max(w, k); break
    return w

def radius(rows, F, cells, cap):
    init = accepts(rows, F)
    for k in range(1, cap+1):
        for cs in itertools.combinations(cells, k):
            for vals in itertools.product(*[[v for v in range(D) if v != rows[i][c]] for i, c in cs]):
                new = [list(r) for r in rows]
                for (i, c), v in zip(cs, vals): new[i][c] = v
                if accepts(new, F) != init: return k
    return None  # > cap

def reject_formula(rows, F, fixed):
    best = None
    for X in F:
        G = [r for r in rows if all(r[j] == 0 for j in X)]
        if G:
            a = 1 + sum(r[Q] == 0 for r in G)
            b = max(sum(r[Q] == v for r in G) for v in range(1, D))
            c = -(-(a-b)//2)
        elif fixed: continue
        else:
            c = min(sum(r[j] != 0 for j in X) + (r[Q] == 0) for r in rows)
        best = c if best is None else min(best, c)
    return best

MODE = sys.argv[4] if len(sys.argv) > 4 else 'any'
n_rows = int(sys.argv[2]) if len(sys.argv) > 2 else 4
stats = dict(rejected=0, accepted=0, gaps=0, laminar_rej=0)
for trial in range(int(sys.argv[3]) if len(sys.argv) > 3 else 600):
    while True:
        F = random.sample(SUBSETS, random.randint(1, 5))
        if MODE == 'any' or width(F) >= 2: break
    if MODE == 'gap':  # rows with y!=0 matching some X exactly, plus y=0 rows missing one key
        rows = []
        for _ in range(n_rows):
            if random.random() < 0.5:
                X = random.choice(F); rows.append(tuple(0 if j in X else random.choice([1, 2]) for j in range(Q)) + (random.choice([1, 2]),))
            else:
                k = random.randrange(Q); rows.append(tuple(random.choice([1, 2]) if j == k else 0 for j in range(Q)) + (0,))
    else:
        rows = [tuple(random.choice([0, 0, 1, 2]) for _ in range(Q)) + (random.randrange(D),) for _ in range(n_rows)]
    w = width(F)
    allc = [(i, c) for i in range(n_rows) for c in range(Q+1)]
    ycells = [(i, Q) for i in range(n_rows)]
    if not accepts(rows, F):
        stats['rejected'] += 1
        fix = radius(rows, F, ycells, n_rows)
        full = radius(rows, F, allc, fix)
        assert fix is not None and full is not None and full <= fix <= w*full, (F, rows, full, fix, w)
        if full < fix: stats['gaps'] += 1
        if w == 1: stats['laminar_rej'] += 1; assert full == fix
    else:
        stats['accepted'] += 1
        ff = reject_formula(rows, F, False); fx = reject_formula(rows, F, True)
        full = radius(rows, F, allc, ff)
        assert full == ff, ('full', F, rows, full, ff)
        if fx is not None:
            assert radius(rows, F, ycells, fx) == fx, ('fixed', F, rows, fx)
        else:
            assert radius(rows, F, ycells, n_rows) is None
print(stats)
