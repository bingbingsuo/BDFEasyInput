import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bdfeasyinput.modules.scf import generate_scf_block


def _base_config(convergence=None):
    cfg = {
        "method": {"type": "dft", "functional": "b3lyp"},
        "molecule": {"charge": 0, "multiplicity": 1},
        "settings": {"scf": {}},
    }
    if convergence is not None:
        cfg["settings"]["scf"]["convergence"] = convergence
    return cfg


def test_scf_includes_molden_and_no_threne_by_default():
    lines = generate_scf_block(_base_config())
    joined = "\n".join(lines)
    assert "molden" in lines
    assert "THRENE" not in joined


@pytest.mark.parametrize("value", [1e-8, "1e-8", "1.0E-08"])
def test_convergence_default_value_does_not_emit_threne(value):
    lines = generate_scf_block(_base_config(convergence=value))
    joined = "\n".join(lines)
    assert "molden" in lines
    assert "THRENE" not in joined


def test_convergence_custom_emits_threne():
    lines = generate_scf_block(_base_config(convergence=1e-6))
    # THRENE should be present with formatted value
    assert "THRENE" in lines
    assert any(line.strip() == "1.0E-06" for line in lines)
    # molden should still be present
    assert "molden" in lines

