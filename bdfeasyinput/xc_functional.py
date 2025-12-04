"""
XC functional conversion utilities for BDFEasyInput.

Design principles
-----------------

1. **Direct match to libxc / BDF**:
   - BDF matches XC functionals by **user-provided name**; we MUST NOT
     rename or remap user names internally.
   - Our job is to:
       * accept convenient YAML representations; and
       * normalize them to the exact string that should be written after
         ``dft functional`` in the BDF input.

2. **Supported input formats** (YAML side)
   - Single XC functional::

       method:
         type: dft
         functional: B3LYP

   - Exchange + correlation combination given as a single string::

       method:
         type: dft
         functional: "PBE LYP"   # X = PBE, C = LYP

   - Structured exchange + correlation form::

       method:
         type: dft
         functional:
           x: PBE
           c: LYP

3. **Optional validation against libxc list**:
   - We can optionally load ``research/mapping_tables/xc_functionals.yaml``
     and check whether given names appear as X / C / XC functionals.
   - Validation is **soft**: it returns warnings but should not prevent
     generation of BDF input.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, MutableMapping, Optional, Tuple, Union

import yaml


# Public types -----------------------------------------------------------------

FunctionalInput = Union[str, Mapping[str, Any]]


@dataclass
class FunctionalValidationResult:
    """Result of optional functional validation."""

    ok: bool
    warnings: Tuple[str, ...] = ()


# Core conversion --------------------------------------------------------------

def process_functional_input(functional: FunctionalInput) -> str:
    """
    Normalize a YAML-side XC functional specification into a BDF string.

    Parameters
    ----------
    functional
        - ``str``:
            * single XC functional name, e.g. ``"B3LYP"``; or
            * combined functional, e.g. ``"PBE LYP"``.
        - ``Mapping``:
            structured form, e.g.::

                {"x": "PBE", "c": "LYP"}

    Returns
    -------
    str
        The exact string that should follow ``dft functional`` in BDF input,
        e.g. ``"B3LYP"`` or ``"PBE LYP"``.

    Notes
    -----
    - This function does **not** perform any remapping or case normalisation.
      The caller is responsible for using names that BDF/libxc understands.
    """
    # Structured form: {'x': 'PBE', 'c': 'LYP'}
    if isinstance(functional, Mapping):
        # Accept case-insensitive keys like 'X', 'C', 'x', 'c'.
        x_name = None
        c_name = None
        for key, value in functional.items():
            k = str(key).lower()
            if k == "x":
                x_name = str(value).strip()
            elif k == "c":
                c_name = str(value).strip()

        if x_name and c_name:
            return f"{x_name} {c_name}"
        if x_name:
            return x_name
        if c_name:
            return c_name
        raise ValueError("Empty functional specification mapping: expected keys 'x' and/or 'c'.")

    # String form: either single functional or "X C" combination.
    if isinstance(functional, str):
        func_str = functional.strip()
        if not func_str:
            raise ValueError("Empty functional string is not allowed.")
        return func_str

    raise TypeError(f"Unsupported functional specification type: {type(functional)!r}")


def build_dft_functional_lines(method_section: Mapping[str, Any]) -> Optional[Tuple[str, str]]:
    """
    Build the two BDF lines corresponding to the ``dft functional`` keyword.

    Parameters
    ----------
    method_section
        Parsed ``method`` section from YAML, e.g.::

            {
              "type": "dft",
              "functional": "B3LYP",
            }

    Returns
    -------
    Optional[Tuple[str, str]]
        Either ``("dft functional", " B3LYP")`` or ``None`` if no
        DFT functional should be written (e.g. method type is not DFT or
        functional is missing).
    """
    method_type = str(method_section.get("type", "")).lower()
    if method_type != "dft":
        return None

    if "functional" not in method_section:
        # Caller can decide whether this is an error; here we silently skip.
        return None

    func_spec: FunctionalInput = method_section["functional"]
    func_str = process_functional_input(func_spec)

    # Important: we only prepend a single leading space, following existing
    # BDF examples.
    return "dft functional", f" {func_str}"


# Optional validation ----------------------------------------------------------

def load_xc_database(
    path: Union[str, Path, None] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Load the xc_functionals.yaml database as a plain dict.

    Parameters
    ----------
    path
        Path to ``xc_functionals.yaml``. If omitted, will look for
        ``research/mapping_tables/xc_functionals.yaml`` relative to the
        project root (two directories above this file).

    Returns
    -------
    Dict[str, Dict[str, Any]]
        Mapping ``macro_name -> functional_info``.
    """
    if path is None:
        # bdfeasyinput/xc_functional.py -> project_root/research/mapping_tables
        root = Path(__file__).resolve().parents[1]
        path = root / "research" / "mapping_tables" / "xc_functionals.yaml"

    yaml_path = Path(path)
    if not yaml_path.exists():
        raise FileNotFoundError(f"xc_functionals.yaml not found at: {yaml_path}")

    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    funcs = data.get("functionals")
    if not isinstance(funcs, MutableMapping):
        raise ValueError(f"Unexpected xc_functionals.yaml structure at {yaml_path}")
    return dict(funcs)


def _match_name_against_db(name: str, db: Mapping[str, Mapping[str, Any]], roles: Tuple[str, ...]) -> bool:
    """Return True if `name` matches any entry in `db` with role in `roles`."""
    target = name.strip()
    if not target:
        return False

    for macro, info in db.items():
        role = str(info.get("role", "")).upper()
        if role not in {r.upper() for r in roles}:
            continue

        short_name = str(info.get("short_name", ""))

        # Match by short_name (preferred) or macro suffix.
        if short_name == target:
            return True
        if macro.endswith(f"_{target}"):
            return True
    return False


def validate_functional(
    functional_str: str,
    xc_db: Mapping[str, Mapping[str, Any]],
) -> FunctionalValidationResult:
    """
    Soft-validate a functional string against libxc database.

    Parameters
    ----------
    functional_str
        Final functional string that will be written after ``dft functional``,
        e.g. ``"B3LYP"`` or ``"PBE LYP"``.
    xc_db
        Database loaded via :func:`load_xc_database`.

    Returns
    -------
    FunctionalValidationResult
        - ``ok`` 表示是否在库中找到合理的匹配；
        - ``warnings`` 给出人类可读的告警信息。

    Notes
    -----
    - 该验证是**可选的**，仅用于提前发现拼写错误或不常见泛函。
    - 即使 ``ok=False``，调用方仍然可以选择继续生成 BDF 输入。
    """
    warnings = []
    parts = functional_str.split()

    # 单一 XC 泛函
    if len(parts) == 1:
        name = parts[0]
        if not _match_name_against_db(name, xc_db, roles=("XC",)):
            warnings.append(
                f"XC functional '{name}' 未在 libxc 交换相关泛函列表 (role=XC) 中找到；"
                " 如果这是自定义或较新的泛函，可忽略此警告。"
            )
        return FunctionalValidationResult(ok=not warnings, warnings=tuple(warnings))

    # 组合：X C
    if len(parts) == 2:
        x_name, c_name = parts

        if not _match_name_against_db(x_name, xc_db, roles=("X", "XC")):
            warnings.append(
                f"交换泛函 '{x_name}' 未在 libxc 交换/交换相关泛函列表 (role=X/XC) 中找到。"
            )
        if not _match_name_against_db(c_name, xc_db, roles=("C", "XC")):
            warnings.append(
                f"相关泛函 '{c_name}' 未在 libxc 相关/交换相关泛函列表 (role=C/XC) 中找到。"
            )

        return FunctionalValidationResult(ok=not warnings, warnings=tuple(warnings))

    # 其他更复杂形式：目前仅给出温和告警
    warnings.append(
        f"无法解析的泛函形式 '{functional_str}'；目前仅支持 'F' 或 'X C' 形式做验证。"
    )
    return FunctionalValidationResult(ok=False, warnings=tuple(warnings))


__all__ = [
    "FunctionalInput",
    "FunctionalValidationResult",
    "process_functional_input",
    "build_dft_functional_lines",
    "load_xc_database",
    "validate_functional",
]


