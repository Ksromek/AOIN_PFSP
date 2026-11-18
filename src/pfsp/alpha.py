"""Sterowanie zasięgiem α w mutacji przez wstawianie – WASZ WKŁAD, do napisania.

Interfejs (używany przez algorithms/rk_ga.py):
  * ``alpha()``            – bieżąca wartość α,
  * ``update(succ, tries)`` – po każdym pokoleniu: ile mutacji było udanych.

Co to „udana mutacja” – decyzja do opisania w raporcie. Szkielet rk_ga.py
liczy: dziecko po mutacji lepsze od lepszego z rodziców (koszt 0 dodatkowych FFE).
"""
from __future__ import annotations


class AlphaController:
    def alpha(self) -> float:
        raise NotImplementedError

    def update(self, successes: int, trials: int) -> None:
        pass


class ConstantAlpha(AlphaController):
    """Punkt odniesienia: stałe α."""

    def __init__(self, value: float = 2.0):
        self.value = value

    def alpha(self) -> float:
        return self.value


class DecreasingAlpha(AlphaController):
    """α maleje z czasem (np. liniowo od alpha_start do alpha_end wg zużytego budżetu)."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("TODO")


class SuccessRuleAlpha(AlphaController):
    """Reguła sukcesu: target=0.2 (1/5, Rechenberg) albo target≈0.37 (1/e).

    Po oknie prób: odsetek udanych > target -> α *= c, inaczej α /= c;
    α ograniczone do [alpha_min, alpha_max].
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("TODO")


def make_controller(name: str, **params) -> AlphaController:
    registry = {
        "constant": ConstantAlpha,
        "decreasing": DecreasingAlpha,
        "one_fifth": lambda **kw: SuccessRuleAlpha(target=0.2, **kw),
        "one_e": lambda **kw: SuccessRuleAlpha(target=0.3679, **kw),
    }
    if name not in registry:
        raise ValueError(f"Nieznany sterownik α: {name!r}")
    return registry[name](**params)
