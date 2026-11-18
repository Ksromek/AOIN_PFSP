"""Mikrobenchmark: ile trwa jedna ewaluacja i ile potrwa jedno uruchomienie z budżetem z literatury.

  python benchmarks/bench_eval.py            # domyślne rozmiary
  python benchmarks/bench_eval.py --repeat 200000

Mierzy (na losowych instancjach U[1,99] – czas zależy tylko od rozmiaru):
  * makespan(perm)            – sama funkcja celu w Numbie,
  * decode(keys) + makespan   – ocena osobnika random keys (argsort z NumPy + cel),
  * Evaluator.evaluate_keys   – to, co faktycznie wołają algorytmy (z narzutem Pythona).
Szacunek czasu = czas_na_ewaluację × budżet FFE (bez narzutu samego algorytmu!).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pfsp import Evaluator, random_instance  # noqa: E402
from pfsp.budgets import LITERATURE_FFE  # noqa: E402
from pfsp.objective import makespan  # noqa: E402
from pfsp.random_keys import decode  # noqa: E402

SIZES = [(20, 5), (50, 10), (100, 20), (200, 20), (500, 20)]


def timeit(fn, repeat: int) -> float:
    fn()  # rozgrzewka / kompilacja
    t0 = time.perf_counter()
    for _ in range(repeat):
        fn()
    return (time.perf_counter() - t0) / repeat


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeat", type=int, default=20000)
    args = ap.parse_args()
    rng = np.random.default_rng(0)
    print(f"{'rozmiar':>8} | {'makespan':>10} | {'decode+cel':>10} | {'Evaluator':>10} | {'budżet FFE':>12} | {'szac. 1 uruch.':>14}")
    print("-" * 80)
    for n, m in SIZES:
        inst = random_instance(n, m, seed=1)
        p = inst.p
        perm = rng.permutation(n).astype(np.int64)
        keys = rng.random(n)
        ev = Evaluator(inst)
        t_ms = timeit(lambda: makespan(perm, p), args.repeat)
        t_dec = timeit(lambda: makespan(decode(keys), p), args.repeat)
        t_ev = timeit(lambda: ev.evaluate_keys(keys), args.repeat)
        size = f"{n}x{m}"
        budget = LITERATURE_FFE.get(size)
        est = f"{t_ev * budget / 60:.1f} min" if budget else "-"
        print(f"{size:>8} | {t_ms * 1e6:8.2f}µs | {t_dec * 1e6:8.2f}µs | {t_ev * 1e6:8.2f}µs | "
              f"{budget or '-':>12} | {est:>14}")
    print("\nSzacunek nie obejmuje narzutu algorytmu (selekcja, DSM, przenumerowanie...).")


if __name__ == "__main__":
    main()
