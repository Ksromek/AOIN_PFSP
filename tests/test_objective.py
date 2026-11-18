import itertools

import numpy as np
import pytest

from pfsp.instance import random_instance
from pfsp.objective import insertion_makespans, makespan, total_flow_time

# Mini-przykład z PDF-a: 3 zadania, 2 maszyny
P = np.array([[3, 1, 2], [2, 4, 1]], dtype=np.int64)


def naive_completion(perm, p):
    """Wprost z definicji: C[i][k] = max(C[i-1][k], C[i][k-1]) + p[k][perm[i]]."""
    m, n = p.shape
    C = np.zeros((len(perm), m), dtype=np.int64)
    for i, j in enumerate(perm):
        for k in range(m):
            prev_job = C[i - 1, k] if i > 0 else 0
            prev_mach = C[i, k - 1] if k > 0 else 0
            C[i, k] = max(prev_job, prev_mach) + p[k, j]
    return C


def test_pdf_example():
    assert makespan(np.array([0, 1, 2]), P) == 10   # kolejność (1, 2, 3)
    assert makespan(np.array([1, 0, 2]), P) == 8    # kolejność (2, 1, 3)


def test_pdf_example_optimum_by_brute_force():
    best = min(makespan(np.array(perm, dtype=np.int64), P) for perm in itertools.permutations(range(3)))
    assert best == 8


@pytest.mark.parametrize("n,m,seed", [(5, 3, 0), (20, 5, 1), (50, 10, 2), (13, 7, 3)])
def test_makespan_and_tft_match_naive(n, m, seed):
    inst = random_instance(n, m, seed=seed)
    rng = np.random.default_rng(seed)
    for _ in range(20):
        perm = rng.permutation(n).astype(np.int64)
        C = naive_completion(perm, inst.p)
        assert makespan(perm, inst.p) == C[-1, -1]
        assert total_flow_time(perm, inst.p) == C[:, -1].sum()


@pytest.mark.parametrize("n,m,seed", [(6, 3, 0), (20, 5, 1), (30, 10, 2)])
def test_insertion_makespans_match_naive(n, m, seed):
    inst = random_instance(n, m, seed=seed)
    rng = np.random.default_rng(seed)
    for k in [0, 1, 5, n - 1]:
        seq = rng.permutation(n)[:k].astype(np.int64)
        job = int(next(j for j in range(n) if j not in set(seq.tolist())))
        fast = insertion_makespans(seq, np.int64(job), inst.p)
        slow = [makespan(np.insert(seq, pos, job).astype(np.int64), inst.p) for pos in range(k + 1)]
        assert fast.tolist() == slow
