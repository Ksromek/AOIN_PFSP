"""GA na random keys – szkielet Waszego algorytmu.

Działa od razu w wersji bazowej:
  crossover="uniform", mutation="gaussian"  ->  baseline „GA na RK ze zwykłym szumem”.

Wasze warianty podpina się parametrami (rzucą NotImplementedError,
dopóki nie napiszecie funkcji w random_keys.py / linkage.py / alpha.py):
  crossover = "block_plain"     – zwykłe kopiowanie bloków z DSM (jak Permutation GOMEA)
            = "block_coherent"  – spójne kopiowanie (Wasz pomysł)
  blocks    = "dsm" | "random"  – bloki z linkage tree albo losowe (kontrola 2×2)
  mutation  = "alpha_insert"    – wstawianie z zasięgiem α
  alpha     = "constant" | "decreasing" | "one_fifth" | "one_e"

Pętla pokolenia:
  elita -> selekcja turniejowa -> krzyżowanie -> mutacja -> ocena
  -> aktualizacja sterownika α -> przenumerowanie kluczy całej populacji.

Akceptacja w stylu GOMEA (optimal mixing: zostaw zmianę, jeśli nie pogorszyła)
to inna pętla niż GA – dopiszcie ją jako osobną funkcję, gdy do niej dojdziecie.
"""
from __future__ import annotations

import numpy as np

from .. import linkage
from ..alpha import make_controller
from ..evaluator import Evaluator
from ..random_keys import (coherent_block_copy, insert_with_alpha, plain_block_copy,
                           random_keys, reencode)


def _uniform_crossover(a, b, rng, **_):
    mask = rng.random(a.shape[0]) < 0.5
    return np.where(mask, a, b)


def _block_crossover(a, b, rng, blocks, coherent: bool, **_):
    """Biorca = a, dawca = b; przenosimy jeden losowy blok z listy."""
    block = blocks[rng.integers(len(blocks))]
    if coherent:
        return coherent_block_copy(a, b, block)
    return plain_block_copy(a, b, block)


def _gaussian_mutation(x, rng, sigma: float = 0.1, p_gene: float | None = None, **_):
    n = x.shape[0]
    p_gene = 1.0 / n if p_gene is None else p_gene
    mask = rng.random(n) < p_gene
    y = x.copy()
    y[mask] += rng.normal(0.0, sigma, size=int(mask.sum()))
    return y


def _alpha_mutation(x, rng, alpha: float, **_):
    n = x.shape[0]
    job, anchor = rng.choice(n, size=2, replace=False)
    return insert_with_alpha(x, int(job), int(anchor), alpha)


def run(evaluator: Evaluator, rng: np.random.Generator, pop_size: int = 50,
        crossover: str = "uniform", blocks: str = "dsm", mutation: str = "gaussian",
        alpha: str = "constant", alpha_params: dict | None = None,
        p_cross: float = 0.9, p_mut: float = 0.5, elite: int = 1, tournament: int = 2,
        sigma: float = 0.1) -> None:
    n = evaluator.instance.n_jobs
    controller = make_controller(alpha, **(alpha_params or {}))

    pop = np.array([reencode(random_keys(n, rng)) for _ in range(pop_size)])
    fit = np.array([evaluator.evaluate_keys(x) for x in pop])

    def select() -> int:
        idx = rng.choice(pop_size, size=tournament, replace=False)
        return int(idx[np.argmin(fit[idx])])

    while True:
        # --- model zależności (tylko dla krzyżowania blokowego)
        block_list = None
        if crossover.startswith("block"):
            if blocks == "dsm":
                block_list = linkage.linkage_tree(linkage.dsm_bosman(pop))
            else:
                ref = linkage.linkage_tree(linkage.dsm_bosman(pop))
                block_list = linkage.random_blocks_like(ref, n, rng)

        order = np.argsort(fit)
        new_pop = [pop[k].copy() for k in order[:elite]]
        new_fit = [fit[k] for k in order[:elite]]
        successes = trials = 0
        while len(new_pop) < pop_size:
            ia, ib = select(), select()
            a, b = pop[ia], pop[ib]
            if rng.random() < p_cross:
                if crossover == "uniform":
                    child = _uniform_crossover(a, b, rng)
                else:
                    child = _block_crossover(a, b, rng, block_list,
                                             coherent=(crossover == "block_coherent"))
            else:
                child = a.copy()
            mutated = rng.random() < p_mut
            if mutated:
                if mutation == "gaussian":
                    child = _gaussian_mutation(child, rng, sigma=sigma)
                else:
                    child = _alpha_mutation(child, rng, alpha=controller.alpha())
            f_child = evaluator.evaluate_keys(child)
            if mutated:
                trials += 1
                successes += int(f_child < min(fit[ia], fit[ib]))
            new_pop.append(child)
            new_fit.append(f_child)
        controller.update(successes, trials)
        pop = np.array([reencode(x) for x in new_pop])
        fit = np.array(new_fit)
