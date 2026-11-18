"""Budżety FFE z literatury.

LITERATURE_FFE – liczby z tabeli 1 w Bosman, Luong, Thierens (GECCO 2016),
które ci autorzy wzięli z GM-EDA (Ceberio i in. 2014). Te same liczby są
w Guijt i in. (2022), tabela 2 (tam dla makespanu). Sprawdzone w samych pracach
(Bosman 2016 – wszystkie 12; Guijt 2022 – co najmniej 20×5 i 500×20).
"""
from __future__ import annotations

LITERATURE_FFE: dict[str, int] = {
    "20x5": 182_224_100,
    "20x10": 224_784_800,
    "20x20": 256_896_400,
    "50x5": 220_712_150,
    "50x10": 256_208_100,
    "50x20": 275_954_150,
    "100x5": 235_879_800,
    "100x10": 266_211_000,
    "100x20": 283_040_000,
    "200x10": 272_515_500,
    "200x20": 287_728_850,
    "500x20": 260_316_750,
}


def budget_for(size: str, n_jobs: int, rule: str | int) -> int | None:
    """Budżet FFE dla instancji.

    rule:
      * "literature"  – LITERATURE_FFE (Bosman 2016 / Guijt 2022),
      * "1000n2"      – 1000·n² (Ayodele i in., RK-EDA, PPSN 2016),
      * "none"        – bez limitu (np. dla NEH),
      * liczba        – stały budżet.
    """
    if isinstance(rule, int):
        return rule
    if rule == "literature":
        if size not in LITERATURE_FFE:
            raise KeyError(f"Brak budżetu z literatury dla rozmiaru {size}")
        return LITERATURE_FFE[size]
    if rule == "1000n2":
        return 1000 * n_jobs * n_jobs
    if rule == "none":
        return None
    try:
        return int(rule)
    except ValueError as exc:
        raise ValueError(f"Nieznana reguła budżetu: {rule!r}") from exc
