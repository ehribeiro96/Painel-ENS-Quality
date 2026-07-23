from __future__ import annotations

import json
import re
import subprocess
import sys

LABELS = {
    "revision": "org.opencontainers.image.revision",
    "version": "org.opencontainers.image.version",
    "source": "org.opencontainers.image.source",
}
CANONICAL_SOURCE = "https://github.com/ehribeiro96/Painel-ENS-Quality"
REVISION_PATTERN = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")


def inspect_image(image: str) -> tuple[str, dict[str, str]]:
    result = subprocess.run(
        ["docker", "image", "inspect", image],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    if len(payload) != 1 or not isinstance(payload[0].get("Config", {}).get("Labels"), dict):
        raise ValueError("image inspect returned no label map")
    return payload[0]["Id"], payload[0]["Config"]["Labels"]


def assert_labels(image: str, revision: str, version: str, source: str) -> dict[str, str]:
    expected = {"revision": revision, "version": version, "source": source}
    if any(value != value.strip() or not value or value.lower() == "unknown" for value in expected.values()):
        raise ValueError("certified OCI expectations must be non-empty and not unknown")
    if REVISION_PATTERN.fullmatch(revision) is None or source != CANONICAL_SOURCE:
        raise ValueError("certified OCI revision or source is not canonical")
    image_id, labels = inspect_image(image)
    actual = {name: labels.get(label) for name, label in LABELS.items()}
    if any(
        value is None or value != value.strip() or not value or value.lower() == "unknown" for value in actual.values()
    ) or actual != expected:
        raise ValueError(f"OCI label mismatch: expected={expected!r} actual={actual!r}")
    verified = {name: labels[label] for name, label in LABELS.items()}
    return {"image_id": image_id, **verified}


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 4:
        print("usage: assert_oci_labels.py IMAGE EXPECTED_REVISION EXPECTED_VERSION EXPECTED_SOURCE", file=sys.stderr)
        return 2
    try:
        print(json.dumps(assert_labels(*args), sort_keys=True))
    except (json.JSONDecodeError, KeyError, OSError, subprocess.CalledProcessError, ValueError) as error:
        print(f"OCI assertion failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
