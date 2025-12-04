#!/usr/bin/env python3
"""Simple query tool for xc_functionals.yaml.

Usage examples:
    python query_xc_functionals.py list
    python query_xc_functionals.py family GGA
    python query_xc_functionals.py role XC
    python query_xc_functionals.py search PBE
"""

import sys
from pathlib import Path
import yaml


def load_db(path: Path):
    obj = yaml.safe_load(path.read_text())
    return obj['functionals']


def cmd_list(funcs):
    print(f"Total functionals: {len(funcs)}")
    for name, info in sorted(funcs.items(), key=lambda kv: kv[1]['id']):
        print(f"{info['id']:4d}  {name:30s}  {info['family']:7s}  {info['role']:3s}  {info['description']}")


def cmd_family(funcs, family: str):
    family = family.upper()
    for name, info in sorted(funcs.items(), key=lambda kv: kv[1]['id']):
        if info['family'].upper() == family:
            print(f"{info['id']:4d}  {name:30s}  {info['role']:3s}  {info['description']}")


def cmd_role(funcs, role: str):
    role = role.upper()
    for name, info in sorted(funcs.items(), key=lambda kv: kv[1]['id']):
        if info['role'].upper() == role:
            print(f"{info['id']:4d}  {name:30s}  {info['family']:7s}  {info['description']}")


def cmd_search(funcs, pattern: str):
    pattern = pattern.lower()
    for name, info in sorted(funcs.items(), key=lambda kv: kv[1]['id']):
        if pattern in name.lower() or pattern in info['description'].lower():
            print(f"{info['id']:4d}  {name:30s}  {info['family']:7s}  {info['role']:3s}  {info['description']}")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    db_path = Path(__file__).parent.parent / 'mapping_tables' / 'xc_functionals.yaml'
    if not db_path.exists():
        print(f"错误：找不到 {db_path}，请先运行 generate_xc_functional_list.py")
        sys.exit(1)

    funcs = load_db(db_path)

    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)

    cmd = argv[0]
    if cmd == 'list':
        cmd_list(funcs)
    elif cmd == 'family' and len(argv) >= 2:
        cmd_family(funcs, argv[1])
    elif cmd == 'role' and len(argv) >= 2:
        cmd_role(funcs, argv[1])
    elif cmd == 'search' and len(argv) >= 2:
        cmd_search(funcs, ' '.join(argv[1:]))
    else:
        print("未知命令或参数不完整。用法示例：")
        print("  python query_xc_functionals.py list")
        print("  python query_xc_functionals.py family GGA")
        print("  python query_xc_functionals.py role XC")
        print("  python query_xc_functionals.py search PBE")
        sys.exit(1)


if __name__ == '__main__':
    main()
