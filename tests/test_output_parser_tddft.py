from pathlib import Path

import pytest

from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser


def test_tddft_blocks_parsed_with_spin_flip_and_ialda():
    fixture = Path(__file__).parent / "data" / "test044_tddft.out"
    parser = BDFOutputParser()

    result = parser.parse(str(fixture))
    tddft = result["tddft"]

    # 三段 TDDFT：isf=-1 (down), isf=1  ialda=0, isf=1  ialda=2
    assert [(c["isf"], c["ialda"], c["spin_flip_direction"]) for c in tddft] == [
        (-1, 0, "down"),
        (1, 0, "up"),
        (1, 2, "up"),
    ]

    # 校验激发能量首项
    energies_first = [c["states"][0]["energy_ev"] for c in tddft]
    assert energies_first == pytest.approx([0.0462, 10.7005, 10.6044], rel=1e-4)

    # 兼容旧字段：excited_states 等于首个 TDDFT 块
    assert result["excited_states"] == tddft[0]["states"]
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser


ROOT = Path(__file__).resolve().parents[1]
TDDFT_LOG = ROOT / "debug" / "test_tddft.log"
TDDFT_SF_LOG = ROOT / "debug" / "test044.out"


def test_parse_tddft_excited_states_summary():
    parser = BDFOutputParser()
    result = parser.parse(str(TDDFT_LOG))

    # Basic expectations
    assert result["converged"] is True or result["excited_states"], "TDDFT should produce excited states"
    states = result["excited_states"]
    assert len(states) >= 3

    first = states[0]
    # Known values from summary table
    assert abs(first["energy_ev"] - 7.5963) < 1e-3
    assert abs(first["wavelength_nm"] - 163.22) < 1e-2
    assert abs(first["oscillator_strength"] - 0.0233) < 1e-4
    assert first["symmetry"].lower() == "b2"


def test_parse_total_energy_and_geometry_present():
    parser = BDFOutputParser()
    result = parser.parse(str(TDDFT_LOG))

    assert result["energy"] is not None
    assert result["scf_energy"] is not None
    assert len(result["geometry"]) >= 3  # O + 2H


def test_parse_spin_flip_tddft_blocks():
    """
    验证 spin-flip TDDFT 能正确解析 isf/ialda 分块与激发能
    样例来源：debug/test044.out（CH2 三重态参考，isf=-1/-，ialda=0/2）
    """
    parser = BDFOutputParser()
    result = parser.parse(str(TDDFT_SF_LOG))

    tddft_blocks = result.get("tddft", [])
    assert len(tddft_blocks) >= 3  # down + two up blocks

    # Spin-flip down block (isf = -1)
    down_blocks = [b for b in tddft_blocks if b.get("isf") == -1]
    assert down_blocks, "should parse spin-flip down block"
    down_first = down_blocks[0]["states"][0]
    assert abs(down_first["energy_ev"] - 0.0462) < 1e-4

    # Spin-flip up block (isf = 1, ialda = 0)
    up_blocks = [b for b in tddft_blocks if b.get("isf") == 1]
    assert len(up_blocks) >= 2, "should parse two spin-flip up blocks"
    ialda0 = [b for b in up_blocks if b.get("ialda") in (None, 0)]
    assert ialda0, "ialda=0 block missing"
    assert abs(ialda0[0]["states"][0]["energy_ev"] - 10.7005) < 1e-3

    # Spin-flip up block (isf = 1, ialda = 2)
    ialda2 = [b for b in up_blocks if b.get("ialda") == 2]
    assert ialda2, "ialda=2 block missing"
    assert abs(ialda2[0]["states"][0]["energy_ev"] - 10.6044) < 1e-3

