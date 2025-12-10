import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser


ROOT = Path(__file__).resolve().parents[1]
TDDFT_LOG = ROOT / "debug" / "test_tddft.log"


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

