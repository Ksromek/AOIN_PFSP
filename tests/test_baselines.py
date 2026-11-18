import numpy as np
import pytest

from pfsp import BudgetExhausted, Evaluator, random_instance
from pfsp.algorithms import REGISTRY
from pfsp.algorithms.ga_permutation import insertion_mutation, order_crossover, pmx_crossover


@pytest.mark.parametrize("op", [order_crossover, pmx_crossover])
def test_crossovers_give_permutations(op):
    rng = np.random.default_rng(0)
    for n in [2, 5, 30]:
        for _ in range(200):
            a, b = rng.permutation(n), rng.permutation(n)
            child = op(a, b, rng)
            assert sorted(child.tolist()) == list(range(n))


def test_insertion_mutation_permutation():
    rng = np.random.default_rng(0)
    for _ in range(100):
        x = insertion_mutation(rng.permutation(10), rng)
        assert sorted(x.tolist()) == list(range(10))


@pytest.mark.parametrize("name", ["random_search", "ga_ox", "ga_pmx", "rk_ga_gauss", "cmaes_rk"])
def test_baseline_runs_until_budget(name):
    inst = random_instance(12, 4, seed=0)
    ev = Evaluator(inst, max_ffe=2000)
    fn, params = REGISTRY[name]
    with pytest.raises(BudgetExhausted):
        fn(ev, np.random.default_rng(1), **params)
    assert ev.ffe <= 2000 and ev.best_value is not None
