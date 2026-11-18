"""Random search – dolna granica: losowe permutacje aż do wyczerpania budżetu."""
from __future__ import annotations

import numpy as np

from ..evaluator import Evaluator


def run(evaluator: Evaluator, rng: np.random.Generator, max_iters: int | None = None) -> None:
    n = evaluator.instance.n_jobs
    it = 0
    while max_iters is None or it < max_iters:
        evaluator.evaluate(rng.permutation(n))
        it += 1
