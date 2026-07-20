from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def _counts(root: ET.Element) -> tuple[int, int, int, int]:
    suites = [suite for suite in root.iter("testsuite") if not suite.findall("testsuite")]
    values = [sum(int(suite.get(name, "0")) for suite in suites) for name in ("tests", "skipped", "failures", "errors")]
    return values[0], values[1], values[2], values[3]


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        if len(args) != 1:
            raise ValueError("report_path_required")
        counts = _counts(ET.parse(Path(args[0])).getroot())
    except (OSError, ET.ParseError, ValueError):
        counts = (0, 0, 0, 1)
    tests, skipped, failures, errors = counts
    print(f"tests={tests} skipped={skipped} failures={failures} errors={errors}")
    return 1 if tests == 0 or skipped > 0 or failures > 0 or errors > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
