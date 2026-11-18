"""Klasyczny GA na permutacjach (baseline): turniej, OX albo PMX, mutacja insertion, elityzm.

To baseline – wolno go zastąpić gotową implementacją (np. DEAP), jeśli
chcecie porównać się dokładnie z czyjąś konfiguracją.
"""
from __future__ import annotations

import numpy as np

from ..evaluator import Evaluator


def order_crossover(a: np.ndarray, b: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """OX: odcinek z rodzica a na swoim miejscu, reszta w kolejności z rodzica b."""
    n = a.shape[0]
    i, j = sorted(rng.choice(n + 1, size=2, replace=False))
    child = np.full(n, -1, dtype=np.int64)
    child[i:j] = a[i:j]
    taken = np.zeros(n, dtype=bool)
    taken[a[i:j]] = True
    fill = [g for g in np.concatenate([b[j:], b[:j]]) if not taken[g]]
    positions = list(range(j, n)) + list(range(0, i))
    child[positions] = fill
    return child


def pmx_crossover(a: np.ndarray, b: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """PMX: odcinek z a, reszta z b z naprawą przez mapowanie odcinka."""
    n = a.shape[0]
    i, j = sorted(rng.choice(n + 1, size=2, replace=False))
    child = b.copy()
    child[i:j] = a[i:j]
    pos_in_a = np.empty(n, dtype=np.int64)
    pos_in_a[a] = np.arange(n)
    segment = set(a[i:j].tolist())
    for idx in list(range(0, i)) + list(range(j, n)):
        g = b[idx]
        while g in segment:
            g = b[pos_in_a[g]]
        child[idx] = g
    return child


def insertion_mutation(perm: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    n = perm.shape[0]
    i, j = rng.choice(n, size=2, replace=False)
    job = perm[i]
    rest = np.delete(perm, i)
    return np.insert(rest, j, job)


def run(evaluator: Evaluator, rng: np.random.Generator, pop_size: int = 50,
        crossover: str = "ox", p_cross: float = 0.9, p_mut: float = 0.2,
        elite: int = 1, tournament: int = 2) -> None:
    cx = {"ox": order_crossover, "pmx": pmx_crossover}[crossover]
    n = evaluator.instance.n_jobs
    pop = [rng.permutation(n).astype(np.int64) for _ in range(pop_size)]
    fit = np.array([evaluator.evaluate(x) for x in pop])

    def select() -> np.ndarray:
        idx = rng.choice(pop_size, size=tournament, replace=False)
        return pop[idx[np.argmin(fit[idx])]]

    while True:
        order = np.argsort(fit)
        new_pop = [pop[k].copy() for k in order[:elite]]
        new_fit = [fit[k] for k in order[:elite]]
        while len(new_pop) < pop_size:
            a, b = select(), select()
            child = cx(a, b, rng) if rng.random() < p_cross else a.copy()
            if rng.random() < p_mut:
                child = insertion_mutation(child, rng)
            new_pop.append(child)
            new_fit.append(evaluator.evaluate(child))
        pop, fit = new_pop, np.array(new_fit)
