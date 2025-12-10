import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bdfeasyinput.converter import BDFConverter


def _base_config():
    return {
        "task": {"type": "energy"},
        "molecule": {
            "charge": 0,
            "multiplicity": 1,
            "coordinates": ["H 0 0 0", "H 0 0 1.0"],
            "units": "angstrom",
        },
        "method": {"type": "dft", "functional": "b3lyp", "basis": "cc-pvdz"},
        "settings": {},
    }


def test_scf_passthrough_keyword_and_value_lines():
    cfg = _base_config()
    cfg["settings"]["scf"] = {"diis": 0.7, "damp": True, "charge": 99}

    text = BDFConverter(validate_input=False).convert(cfg)
    scf_block = []
    capture = False
    for line in text.splitlines():
        if line.strip().upper() == "$SCF":
            capture = True
        if capture:
            scf_block.append(line)
        if capture and line.strip().upper() == "$END":
            break

    joined = "\n".join(scf_block)
    assert "Diis" in scf_block
    assert any(l.strip() == "0.7" or l.strip() == "0.7" for l in scf_block)
    assert "Damp" in scf_block  # bool true -> keyword only
    # protected key charge should not be duplicated by passthrough
    assert "99" not in joined


def test_xuanyuan_passthrough_from_atomic_orbital_integral():
    cfg = _base_config()
    cfg["settings"]["atomic_orbital_integral"] = {"rs": 0.5}
    cfg["settings"]["scf"] = {"grid": "fine"}

    text = BDFConverter(validate_input=False).convert(cfg)
    xu_block = []
    capture = False
    for line in text.splitlines():
        if line.strip().upper() == "$XUANYUAN":
            capture = True
        if capture:
            xu_block.append(line)
        if capture and line.strip().upper() == "$END":
            break

    joined = "\n".join(xu_block).lower()
    assert "grid" not in joined  # grid handled by SCF, not XUANYUAN
    assert joined.count("rs") >= 1  # rs present once


def test_bdfopt_passthrough_from_geometry_optimization():
    cfg = _base_config()
    cfg["task"]["type"] = "optimize"
    cfg["settings"]["geometry_optimization"] = {
        "solver": 1,
        "customkey": "abc",
        "remove_imaginary_frequencies": True,
    }

    text = BDFConverter(validate_input=False).convert(cfg)
    opt_block = []
    capture = False
    for line in text.splitlines():
        if line.strip().upper() == "$BDFOPT":
            capture = True
        if capture:
            opt_block.append(line)
        if capture and line.strip().upper() == "$END":
            break

    joined = "\n".join(opt_block)
    assert "Customkey" in opt_block
    assert " abc" in joined
    # bool true -> keyword only
    assert "rmimag" in joined.lower()


def test_mp2_passthrough_block_present():
    cfg = _base_config()
    cfg["settings"]["mp2"] = {"frozen_core": True, "algo": "ri"}

    text = BDFConverter(validate_input=False).convert(cfg)
    mp2_block = []
    capture = False
    for line in text.splitlines():
        if line.strip().upper() == "$MP2":
            capture = True
        if capture:
            mp2_block.append(line)
        if capture and line.strip().upper() == "$END":
            break

    joined = "\n".join(mp2_block).lower()
    assert "frozen_core" in joined
    assert "algo" in joined


def test_resp_passthrough_in_frequency_task():
    cfg = _base_config()
    cfg["task"]["type"] = "frequency"
    cfg["settings"]["resp"] = {"customresp": "x", "print_level": 3}

    text = BDFConverter(validate_input=False).convert(cfg)
    resp_block = []
    capture = False
    for line in text.splitlines():
        if line.strip().upper() == "$RESP":
            capture = True
        if capture:
            resp_block.append(line)
        if capture and line.strip().upper() == "$END":
            break

    joined = "\n".join(resp_block)
    assert "Customresp" in resp_block
    assert " x" in joined
    # protected print_level still present once from core logic
    assert joined.count("iprt") >= 1


def test_hamiltonian_auto_heff_for_heavy_element():
    cfg = _base_config()
    cfg["molecule"]["coordinates"] = ["Au 0 0 0"]
    cfg["settings"]["scf"] = {"grid": "fine"}
    text = BDFConverter(validate_input=False).convert(cfg)
    xu_block = []
    capture = False
    for line in text.splitlines():
        if line.strip().upper() == "$XUANYUAN":
            capture = True
        if capture:
            xu_block.append(line)
        if capture and line.strip().upper() == "$END":
            break
    joined = "\n".join(xu_block).lower()
    assert "heff" in joined
    assert any(line.strip() == "3" for line in xu_block)
    # SOC only if user requests; default auto only adds heff
    assert "hso" not in joined
    # grid should be in SCF, not in XUANYUAN
    assert "grid" not in joined


def test_hamiltonian_user_spin_orbit():
    cfg = _base_config()
    cfg["hamiltonian"] = {"spin-orbit-coupling": True}
    text = BDFConverter(validate_input=False).convert(cfg)
    xu_block = []
    capture = False
    for line in text.splitlines():
        if line.strip().upper() == "$XUANYUAN":
            capture = True
        if capture:
            xu_block.append(line)
        if capture and line.strip().upper() == "$END":
            break
    assert "hso" in [l.strip().lower() for l in xu_block]
    assert any(l.strip() == "2" for l in xu_block)


def test_hamiltonian_user_spin_orbit_with_ecp_basis():
    cfg = _base_config()
    cfg["method"]["basis"] = "LanL2DZ-ECP"
    cfg["hamiltonian"] = {"spin-orbit-coupling": True}
    text = BDFConverter(validate_input=False).convert(cfg)
    xu_block = []
    capture = False
    for line in text.splitlines():
        if line.strip().upper() == "$XUANYUAN":
            capture = True
        if capture:
            xu_block.append(line)
        if capture and line.strip().upper() == "$END":
            break
    assert "hso" in [l.strip().lower() for l in xu_block]
    assert any(l.strip() == "10" for l in xu_block)


def test_hamiltonian_user_scalar_value():
    cfg = _base_config()
    cfg["hamiltonian"] = {"scalar_Hamiltonian": 22}
    cfg["settings"]["scf"] = {"grid": "fine"}
    text = BDFConverter(validate_input=False).convert(cfg)
    xu_block = []
    capture = False
    for line in text.splitlines():
        if line.strip().upper() == "$XUANYUAN":
            capture = True
        if capture:
            xu_block.append(line)
        if capture and line.strip().upper() == "$END":
            break
    assert "heff" in [l.strip().lower() for l in xu_block]
    assert any(line.strip() == "22" for line in xu_block)
    joined = "\n".join(xu_block).lower()
    assert "grid" not in joined

