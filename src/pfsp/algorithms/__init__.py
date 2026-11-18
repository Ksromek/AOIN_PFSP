"""Rejestr algorytmów: nazwa -> (funkcja run, domyślne parametry).

Każde ``run(evaluator, rng, **params)`` ocenia rozwiązania tylko przez Evaluator
i może działać w nieskończoność – runner przerywa je po wyczerpaniu budżetu
(BudgetExhausted). Wyjątek: NEH kończy się sam.
"""
from . import cmaes_rk, ga_permutation, neh, random_search, rk_ga

REGISTRY = {
    "random_search": (random_search.run, {}),
    "neh": (neh.run, {}),
    "ga_ox": (ga_permutation.run, {"crossover": "ox"}),
    "ga_pmx": (ga_permutation.run, {"crossover": "pmx"}),
    "cmaes_rk": (cmaes_rk.run, {}),
    "rk_ga_gauss": (rk_ga.run, {"crossover": "uniform", "mutation": "gaussian"}),
    # --- Wasze warianty (zadziałają po zaimplementowaniu zaślepek) ---
    "rk_ga_alpha_const": (rk_ga.run, {"mutation": "alpha_insert", "alpha": "constant"}),
    "rk_ga_alpha_1_5": (rk_ga.run, {"mutation": "alpha_insert", "alpha": "one_fifth"}),
    "rk_ga_alpha_1_e": (rk_ga.run, {"mutation": "alpha_insert", "alpha": "one_e"}),
    "rk_ga_alpha_decr": (rk_ga.run, {"mutation": "alpha_insert", "alpha": "decreasing"}),
    "plain_dsm": (rk_ga.run, {"crossover": "block_plain", "blocks": "dsm"}),
    "plain_random": (rk_ga.run, {"crossover": "block_plain", "blocks": "random"}),
    "coherent_dsm": (rk_ga.run, {"crossover": "block_coherent", "blocks": "dsm"}),
    "coherent_random": (rk_ga.run, {"crossover": "block_coherent", "blocks": "random"}),
}
