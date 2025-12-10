from typing import Any, Dict, Iterable, List, Tuple


def _format_keyword(key: str) -> str:
    key_lower = key.lower()
    if not key_lower:
        return key
    return key_lower[0].upper() + key_lower[1:]


def _format_value(val: Any) -> Tuple[bool, List[str]]:
    """
    Returns (should_output, lines) for a value.
    - For bool True: keyword-only (handled by caller), here return placeholder.
    - For bool False: skip.
    - For scalar: value line.
    - For list: value line with space-separated items.
    """
    if isinstance(val, bool):
        if val:
            return True, []  # keyword-only
        return False, []
    if isinstance(val, (int, float, str)):
        return True, [f" {val}"]
    if isinstance(val, list):
        items: List[str] = []
        for item in val:
            if item is False:
                continue
            if item is True:
                items.append("true")
            elif isinstance(item, (int, float, str)):
                items.append(str(item))
            # ignore unsupported item types silently
        if not items:
            return False, []
        return True, [f" {' '.join(items)}"]
    # unsupported type
    return False, []


def append_passthrough_lines(
    lines: List[str],
    data: Dict[str, Any],
    protected_keys: Iterable[str] = (),
) -> None:
    """
    Append user-provided keyword/value pairs to module lines.

    Rules:
    - Key case-insensitive; output with leading capital letter.
    - Key on its own line; value (if any) on the next line.
    - Bool true -> only keyword line; bool false -> skip.
    - List -> space-separated value line.
    - Unsupported types or protected keys -> skip.
    """
    protected = {k.lower() for k in protected_keys}

    for key, val in data.items():
        key_lower = str(key).lower()
        if key_lower in protected:
            continue

        should_output, value_lines = _format_value(val)
        if not should_output:
            continue

        keyword = _format_keyword(str(key))
        lines.append(keyword)
        # keyword-only for bool True
        for vline in value_lines:
            lines.append(vline)

