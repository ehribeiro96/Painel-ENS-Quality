from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICONS_FILE = ROOT / "frontend/itam-platform/src/components/icons/HermesIcons.tsx"


class HermesIconsSecurityTest(unittest.TestCase):
    def test_icons_do_not_use_dangerously_set_inner_html(self) -> None:
        source = ICONS_FILE.read_text(encoding="utf-8")
        self.assertNotIn("dangerouslySetInnerHTML", source)
        self.assertIn("DOMParser", source)
        self.assertIn("ALLOWED_SVG_TAGS", source)
        self.assertIn("renderSvgNode", source)
        self.assertIn("createElement", source)

    def test_icons_whitelist_expected_svg_tags(self) -> None:
        source = ICONS_FILE.read_text(encoding="utf-8")
        for tag in ("circle", "path", "rect", "ellipse", "g", "line", "polygon", "polyline"):
            self.assertIn(f'"{tag}"', source)


if __name__ == "__main__":
    unittest.main()
