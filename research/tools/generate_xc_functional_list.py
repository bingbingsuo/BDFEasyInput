#!/usr/bin/env python3
"""Generate BDF XC functional list from xc_funcs.h (libxc).

Usage:
    python generate_xc_functional_list.py [xc_funcs.h] [output_yaml]

Defaults:
    xc_funcs.h   = ~/bdf/BDFAutoTest/bdf-pkg-full/build/include/xc_funcs.h
    output_yaml  = ../mapping_tables/xc_functionals.yaml
"""

import sys
from pathlib import Path
from typing import Dict, Any
import re
import yaml


MACRO_RE = re.compile(r'^#define\s+XC_([A-Z0-9_]+)\s+([0-9]+)\s*/\*\s*(.*?)\s*\*/')


def classify_family(macro_rest: str) -> str:
    if macro_rest.startswith('LDA_'):
        return 'LDA'
    if macro_rest.startswith('GGA_'):
        return 'GGA'
    if macro_rest.startswith('MGGA_'):
        return 'MGGA'
    if macro_rest.startswith('HYB_GGA_'):
        return 'HYB_GGA'
    if macro_rest.startswith('HYB_MGGA_'):
        return 'HYB_MGGA'
    if macro_rest.startswith('HYB_LDA_'):
        return 'HYB_LDA'
    return 'OTHER'


def classify_role(macro_rest: str) -> str:
    """Return role: X, C, XC, K (kinetic), or OTHER.

    Rules (from your description):
      - name contains "_XC_" → XC (exchange-correlation)
      - name contains "_C_"  or endswith "_C"  → C (correlation)
      - name contains "_X_"  or endswith "_X"  → X (exchange)
      - kinetic functionals: *_K_* or family *_K_* prefix → K
    We check XC first, then C, then X, then K.
    """
    if '_XC_' in macro_rest or macro_rest.startswith('XC_') and '_XC_' in macro_rest:
        return 'XC'
    if '_C_' in macro_rest or macro_rest.endswith('_C'):
        return 'C'
    if '_X_' in macro_rest or macro_rest.endswith('_X'):
        return 'X'
    if '_K_' in macro_rest or macro_rest.startswith(('LDA_K_', 'GGA_K_', 'MGGA_K_')):
        return 'K'
    return 'OTHER'


def parse_xc_header(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding='utf-8', errors='ignore')
    functionals: Dict[str, Any] = {}

    for line in text.splitlines():
        m = MACRO_RE.match(line)
        if not m:
            continue
        macro_rest, id_str, desc = m.groups()
        macro = 'XC_' + macro_rest
        xc_id = int(id_str)

        family = classify_family(macro_rest)
        role = classify_role(macro_rest)

        # user-facing short name suggestion: strip leading family prefix
        short_name = macro_rest
        for prefix in ('LDA_', 'GGA_', 'MGGA_', 'HYB_GGA_', 'HYB_MGGA_', 'HYB_LDA_'):
            if short_name.startswith(prefix):
                short_name = short_name[len(prefix):]
                break

        functionals[macro] = {
            'id': xc_id,
            'macro': macro,
            'family': family,   # LDA/GGA/MGGA/HYB_*/OTHER
            'role': role,       # X/C/XC/K/OTHER
            'short_name': short_name,
            'description': desc,
        }

    return {
        'total_functionals': len(functionals),
        'functionals': functionals,
    }


def main(argv=None) -> None:
    if argv is None:
        argv = sys.argv[1:]

    default_in = Path.home() / 'bdf' / 'BDFAutoTest' / 'bdf-pkg-full' / 'build' / 'include' / 'xc_funcs.h'
    default_out = Path(__file__).parent.parent / 'mapping_tables' / 'xc_functionals.yaml'

    in_path = Path(argv[0]) if len(argv) >= 1 else default_in
    out_path = Path(argv[1]) if len(argv) >= 2 else default_out

    if not in_path.exists():
        print(f"错误：找不到 xc_funcs.h 文件: {in_path}")
        sys.exit(1)

    print(f"读取 xc_funcs.h: {in_path}")
    data = parse_xc_header(in_path)

    out_struct = {
        'source_file': str(in_path),
        'generated_by': 'generate_xc_functional_list.py',
        'total_functionals': data['total_functionals'],
        'functionals': data['functionals'],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml.dump(out_struct, allow_unicode=True, sort_keys=True))

    print(f"✅ 已生成泛函列表: {out_path}")
    print(f"   总泛函数: {data['total_functionals']}")


if __name__ == '__main__':
    main()
