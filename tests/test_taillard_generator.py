import importlib.util
from pathlib import Path

import numpy as np

from pfsp.instance import parse_taillard_text

_spec = importlib.util.spec_from_file_location(
    "generate_taillard", Path(__file__).resolve().parents[1] / "scripts" / "generate_taillard.py")
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)

# Macierz weryfikacyjna ta001 (ziarno 873654221) z OR-Library, flowshop2.txt
TA001 = [
    [54, 83, 15, 71, 77, 36, 53, 38, 27, 87, 76, 91, 14, 29, 12, 77, 32, 87, 68, 94],
    [79, 3, 11, 99, 56, 70, 99, 60, 5, 56, 3, 61, 73, 75, 47, 14, 21, 86, 5, 77],
    [16, 89, 49, 15, 89, 45, 60, 23, 57, 64, 7, 1, 63, 41, 63, 47, 26, 75, 77, 40],
    [66, 58, 31, 68, 78, 91, 13, 59, 49, 85, 85, 9, 39, 41, 56, 40, 54, 77, 51, 31],
    [58, 56, 20, 85, 53, 35, 53, 41, 69, 13, 86, 72, 8, 49, 47, 87, 58, 18, 68, 28],
]


def test_ta001_matches_reference():
    assert gen.generate(873654221, 20, 5).tolist() == TA001


def test_all_sizes_present_and_valid(tmp_path):
    gen.TAILLARD  # 12 rozmiarów × 10
    assert sum(len(r) for r in gen.TAILLARD.values()) == 120
    for (n, m), rows in gen.TAILLARD.items():
        path = tmp_path / f"tai{n}_{m}.txt"
        gen.write_file(path, n, m, rows[:2])
        insts = parse_taillard_text(path.read_text(), base_name=path.stem)
        assert len(insts) == 2
        for inst, (seed, ub, lb) in zip(insts, rows):
            assert inst.p.shape == (m, n) and inst.seed == seed and inst.upper_bound == ub
            assert inst.p.min() >= 1 and inst.p.max() <= 99
            # trywialne dolne ograniczenie nie może przekraczać LB ani UB z pracy
            assert max(inst.p.sum(axis=1).max(), inst.p.sum(axis=0).max()) <= lb <= ub
