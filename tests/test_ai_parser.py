import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bdfeasyinput.ai.parser.response_parser import (
    extract_yaml_from_response,
    parse_ai_response,
    AIResponseParseError,
)


def _valid_yaml_text() -> str:
    return (
        "task:\n"
        "  type: energy\n"
        "molecule:\n"
        "  charge: 0\n"
        "  multiplicity: 1\n"
        "  coordinates:\n"
        "    - O 0.0000 0.0000 0.0000\n"
        "  units: angstrom\n"
        "method:\n"
        "  type: dft\n"
        "  functional: pbe0\n"
        "  basis: cc-pvdz\n"
    )


def test_extract_from_code_block():
    resp = f"""```yaml\n{_valid_yaml_text()}\n```"""
    content = extract_yaml_from_response(resp)
    assert "task:" in content
    data = parse_ai_response(resp)
    assert data["task"]["type"] == "energy"


def test_extract_from_plain_yaml():
    resp = _valid_yaml_text()
    content = extract_yaml_from_response(resp)
    assert "method:" in content
    data = parse_ai_response(resp)
    assert data["method"]["functional"] == "pbe0"


def test_invalid_response_raises():
    with pytest.raises(AIResponseParseError):
        parse_ai_response("not yaml and no keys here")
