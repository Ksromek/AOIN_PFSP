import numpy as np
import pytest

from pfsp import BudgetExhausted, Evaluator, random_instance
from pfsp.algorithms import neh
from pfsp.instance import parse_taillard_text
from pfsp.objective import makespan

TAILLARD_STYLE = """number of jobs, number of machines, initial seed, upper bound and lower bound :
           3           2           0           8           8
processing times :
  3  1  2
  2  4  1
number of jobs, number of machines, initial seed, upper bound and lower bound :
           2           2           1           5           5
processing times :
  1  2
  3  1
"""


def test_parser_taillard_multi():
    insts = parse_taillard_text(TAILLARD_STYLE, base_name="tai_test")
    assert [i.name for i in insts] == ["tai_test_0", "tai_test_1"]
    assert insts[0].size == "3x2" and insts[0].upper_bound == 8
    assert insts[0].p.tolist() == [[3, 1, 2], [2, 4, 1]]
    assert insts[1].p.tolist() == [[1, 2], [3, 1]]


def test_parser_single():
    inst = parse_taillard_text("3 2 0 8 8\n3 1 2\n2 4 1\n", base_name="ex")[0]
    assert inst.n_jobs == 3 and inst.n_machines == 2 and inst.lower_bound == 8


def test_budget_and_best_tracking():
    inst = random_instance(10, 3, seed=0)
    ev = Evaluator(inst, max_ffe=5)
    rng = np.random.default_rng(0)
    vals = [ev.evaluate(rng.permutation(10)) for _ in range(5)]
    assert ev.ffe == 5 and ev.best_value == min(vals)
    assert makespan(ev.best_perm, inst.p) == ev.best_value
    with pytest.raises(BudgetExhausted):
        ev.evaluate(rng.permutation(10))
    assert ev.ffe == 5


def test_insertion_counts_k_plus_1():
    inst = random_instance(10, 3, seed=0)
    ev = Evaluator(inst)
    ev.insertion_values(np.arange(4), 7)
    assert ev.ffe == 5


def naive_neh(p):
    order = np.argsort(-p.sum(axis=0), kind="stable")
    seq = [int(order[0])]
    for j in order[1:]:
        vals = [makespan(np.array(seq[:i] + [int(j)] + seq[i:], dtype=np.int64), p) for i in range(len(seq) + 1)]
        i = int(np.argmin(vals))
        seq = seq[:i] + [int(j)] + seq[i:]
    return seq


@pytest.mark.parametrize("n,m,seed", [(8, 3, 0), (20, 5, 1), (50, 10, 2)])
def test_neh_matches_naive(n, m, seed):
    inst = random_instance(n, m, seed=seed)
    ev = Evaluator(inst)
    seq = neh.run(ev)
    assert seq.tolist() == naive_neh(inst.p)
    assert sorted(seq.tolist()) == list(range(n))
    assert ev.best_value == makespan(seq, inst.p)
