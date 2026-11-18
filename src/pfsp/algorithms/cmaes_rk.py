"""CMA-ES na random keys (baseline) – gotowa implementacja z pycma (``pip install cma``).

Po zatrzymaniu się CMA-ES (jego własne kryteria) robimy restart z nowym
seedem, aż skończy się budżet FFE. Restart z rosnącą populacją (IPOP)
jest dostępny w pycma (cma.fmin2 z restarts) – jeśli porównujecie się
z konkretną pracą, ustawcie dokładnie to, czego użyli autorzy.

Uwaga na czas: pycma ma narzut w Pythonie na każdą generację; przy
budżetach rzędu 10^8 FFE to może być wolne – zmierzcie na małej instancji.
"""
from __future__ import annotations

import numpy as np

from ..evaluator import Evaluator


def run(evaluator: Evaluator, rng: np.random.Generator, sigma0: float = 0.3,
        popsize: int | None = None) -> None:
    import cma  # import tutaj, żeby reszta repo działała bez pycma

    n = evaluator.instance.n_jobs
    while True:
        opts = {"seed": int(rng.integers(1, 2**31 - 1)), "verbose": -9}
        if popsize is not None:
            opts["popsize"] = popsize
        es = cma.CMAEvolutionStrategy(rng.random(n), sigma0, opts)
        while not es.stop():
            xs = es.ask()
            es.tell(xs, [float(evaluator.evaluate_keys(np.asarray(x))) for x in xs])
