"""
MP2 Module Generator

This module generates the MP2 block for BDF input files.
It is intentionally light: all user-provided keywords in settings.mp2
are passed through verbatim (after basic formatting), enabling users to
control MP2 options directly.
"""

from typing import Dict, Any, List

from .passthrough import append_passthrough_lines


def generate_mp2_block(config: Dict[str, Any]) -> List[str]:
    """
    Generate MP2 module block with passthrough keywords.
    """
    lines = ["$MP2"]

    settings = config.get("settings", {})
    mp2_settings = settings.get("mp2", {})

    append_passthrough_lines(lines, mp2_settings, protected_keys=())

    lines.append("$END")
    return lines

