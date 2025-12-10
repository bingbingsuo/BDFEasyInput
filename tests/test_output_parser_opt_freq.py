import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bdfeasyinput.analysis.parser.output_parser import BDFOutputParser


def _write_tmp(content: str, tmp_path):
    path = tmp_path / "mock.log"
    path.write_text(content)
    return path


def test_parse_optimize_and_frequency(tmp_path):
    content = """
    Congratulations! BDF normal termination

    Final scf result
    E_tot = -76.0267
    E_ele = -75.9000

    Atom Cartcoord(Bohr)  Charge Basis
     O   0.000000   0.000000   0.221665   8.00
     H   0.000000   1.430901  -0.886659   1.00
     H   0.000000  -1.430901  -0.886659   1.00

    Geometry Optimization step : 1
    Energy = -75.9000
    Gradient=
      O   0.0001  0.0002  0.0003
      H   0.0002  0.0001  0.0004
      H   0.0002  0.0001  0.0004

    Conv. tolerance : 1.0E-05 1.0E-04 1.0E-05 1.0E-04
    Geom. converge : Yes
    Current values : 5.0E-06 5.0E-05 5.0E-06 5.0E-05

    Vibrational frequencies
      1625.3 cm-1
      3650.1 cm-1
      3740.2 cm-1
    """
    log_path = _write_tmp(content, tmp_path)

    parser = BDFOutputParser()
    result = parser.parse(str(log_path))

    assert result["converged"] is True
    assert abs(result["energy"] + 76.0267) < 1e-4
    assert abs(result["scf_energy"] + 75.9) < 1e-3

    geom = result["geometry"]
    assert len(geom) == 3
    assert geom[0]["element"].lower() == "o"
    assert geom[0]["units"] == "bohr"

    # Optimization info captured
    assert result["optimization"]["steps"]
    assert result["optimization"]["converged"] is True

    # Frequencies captured
    assert len(result["frequencies"]) == 3
    assert abs(result["frequencies"][0] - 1625.3) < 1e-3

