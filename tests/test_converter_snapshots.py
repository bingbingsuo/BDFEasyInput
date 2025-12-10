import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bdfeasyinput.converter import BDFConverter


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "h2o_tddft.yaml"
EXAMPLE_OPT = ROOT / "examples" / "h2o_opt_freq.yaml"
EXAMPLE_FREQ = ROOT / "examples" / "h2o_frequency.yaml"
EXAMPLE_GROUP = ROOT / "examples" / "h2o_with_group.yaml"
EXAMPLE_UKS = ROOT / "examples" / "h2co_uks.yaml"


def _lines_between(mark, lines):
    out = []
    capture = False
    for line in lines:
        if line.strip().upper() == mark:
            capture = True
        if capture:
            out.append(line)
            if line.strip().upper() == "$END":
                break
    return out


def test_tddft_blocks_order_and_keywords_default_convergence():
    cfg = BDFConverter(validate_input=False).load_yaml(str(EXAMPLE))
    # remove user-set convergence so we test default behavior (no THRENE)
    cfg.setdefault("settings", {}).setdefault("scf", {}).pop("convergence", None)

    text = BDFConverter(validate_input=False).convert(cfg)
    lines = text.splitlines()

    # Ensure module order: COMPASS -> XUANYUAN -> SCF -> TDDFT
    joined = "\n".join(lines)
    assert joined.index("$COMPASS") < joined.index("$XUANYUAN")
    assert joined.index("$XUANYUAN") < joined.index("$SCF")
    assert joined.index("$SCF") < joined.index("$TDDFT")

    # SCF block should contain molden and no THRENE at default
    scf_block = _lines_between("$SCF", lines)
    scf_join = "\n".join(scf_block).lower()
    assert "molden" in scf_join
    assert "threne" not in scf_join

    # TDDFT block exists and is non-empty
    tddft_block = _lines_between("$TDDFT", lines)
    assert len(tddft_block) >= 2


def test_tddft_with_custom_convergence_emits_threne():
    cfg = BDFConverter(validate_input=False).load_yaml(str(EXAMPLE))
    cfg.setdefault("settings", {}).setdefault("scf", {})["convergence"] = 1e-6

    text = BDFConverter(validate_input=False).convert(cfg)
    lines = text.splitlines()

    scf_block = _lines_between("$SCF", lines)
    scf_join = "\n".join(scf_block).lower()
    assert "molden" in scf_join
    assert "threne" in scf_join
    assert any(line.strip() == "1.0E-06" or line.strip() == "1.0e-06" for line in scf_block)


def test_optimize_block_order_and_keywords():
    cfg = BDFConverter(validate_input=False).load_yaml(str(EXAMPLE_OPT))
    text = BDFConverter(validate_input=False).convert(cfg)
    lines = text.splitlines()
    joined = "\n".join(lines)

    # Order: COMPASS -> BDFOPT -> XUANYUAN -> SCF -> RESP
    assert joined.index("$COMPASS") < joined.index("$BDFOPT")
    assert joined.index("$BDFOPT") < joined.index("$XUANYUAN")
    assert joined.index("$XUANYUAN") < joined.index("$SCF")
    assert joined.index("$SCF") < joined.index("$RESP")

    scf_block = _lines_between("$SCF", lines)
    scf_join = "\n".join(scf_block).lower()
    assert "molden" in scf_join
    assert "threne" in scf_join  # convergence=1e-6 in example


def test_frequency_block_order_and_keywords():
    cfg = BDFConverter(validate_input=False).load_yaml(str(EXAMPLE_FREQ))
    text = BDFConverter(validate_input=False).convert(cfg)
    lines = text.splitlines()
    joined = "\n".join(lines)

    # Order: COMPASS -> BDFOPT(hess only) -> XUANYUAN -> SCF -> RESP
    assert joined.index("$COMPASS") < joined.index("$BDFOPT")
    assert joined.index("$BDFOPT") < joined.index("$XUANYUAN")
    assert joined.index("$XUANYUAN") < joined.index("$SCF")
    assert joined.index("$SCF") < joined.index("$RESP")

    scf_block = _lines_between("$SCF", lines)
    scf_join = "\n".join(scf_block).lower()
    assert "molden" in scf_join
    assert "threne" in scf_join  # convergence=1e-6 in example


def test_energy_with_point_group():
    cfg = BDFConverter(validate_input=False).load_yaml(str(EXAMPLE_GROUP))
    text = BDFConverter(validate_input=False).convert(cfg)
    lines = text.splitlines()
    joined = "\n".join(lines).lower()

    # Order: COMPASS -> XUANYUAN -> SCF
    assert joined.index("$compass") < joined.index("$xuanyuan")
    assert joined.index("$xuanyuan") < joined.index("$scf")

    compass_block = _lines_between("$COMPASS", lines)
    compass_join = "\n".join(compass_block).lower()
    # point group should be present (normalized, e.g., c(2v))
    assert "group" in compass_join
    assert "c(2v)" in compass_join or "c2v" in compass_join

    scf_block = _lines_between("$SCF", lines)
    scf_join = "\n".join(scf_block)
    assert "RHF" in scf_join
    assert "molden" in scf_join.lower()
    assert "THRENE" in scf_join  # convergence=1e-6 in example


def test_uks_open_shell_energy():
    cfg = BDFConverter(validate_input=False).load_yaml(str(EXAMPLE_UKS))
    text = BDFConverter(validate_input=False).convert(cfg)
    lines = text.splitlines()
    joined = "\n".join(lines)

    # Order: COMPASS -> XUANYUAN -> SCF
    assert joined.index("$COMPASS") < joined.index("$XUANYUAN")
    assert joined.index("$XUANYUAN") < joined.index("$SCF")

    scf_block = _lines_between("$SCF", lines)
    scf_join = "\n".join(scf_block)
    # Open-shell DFT with multiplicity=3 should use UKS
    assert "UKS" in scf_join
    assert "Spin" in scf_join and "3" in scf_join
    assert "molden" in scf_join.lower()
    assert "THRENE" in scf_join  # convergence=1e-6 in example

