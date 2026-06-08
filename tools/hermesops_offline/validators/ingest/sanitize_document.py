#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from pathlib import Path

SECRET_PATTERNS = {
    "email": re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b"),
    "internal_ip": re.compile(r"\b(?:10\.(?:\d{1,3}\.){2}\d{1,3}|172\.(?:1[6-9]|2\d|3[0-1])\.(?:\d{1,3}\.)\d{1,3}|192\.168\.(?:\d{1,3}\.)\d{1,3})\b"),
    "hostname_rjm": re.compile(r"\bRJM\w{5,}\b", re.IGNORECASE),
    "cert_path": re.compile(r'\b[^\s"\']+\.(?:pfx|p12|pem|key)\b', re.IGNORECASE),
    "secret_keyword": re.compile(r"\b(password|token|secret|senha|chave|private_key)\b", re.IGNORECASE),
}

REPLACEMENTS = {
    "email": "[REDACTED_EMAIL]",
    "internal_ip": "[REDACTED_INTERNAL_IP]",
    "hostname_rjm": "[REDACTED_HOSTNAME]",
    "cert_path": "[REDACTED_CERT_PATH]",
    "secret_keyword": "[REDACTED_SECRET_KEYWORD]",
}


def iter_markdown_files(path: Path):
    if path.is_file() and path.suffix.lower() == ".md":
        yield path
        return
    for item in sorted(path.rglob("*.md")):
        if item.is_file():
            yield item


def sanitize_text(text: str):
    findings = []
    sanitized = text
    for label, pattern in SECRET_PATTERNS.items():
        matches = list(pattern.finditer(sanitized))
        if not matches:
            continue
        findings.append(
            {
                "type": label,
                "count": len(matches),
                "samples": [m.group(0)[:120] for m in matches[:5]],
            }
        )
        sanitized = pattern.sub(REPLACEMENTS[label], sanitized)
    return sanitized, findings


def main():
    parser = argparse.ArgumentParser(description="Dry-run sanitization for markdown corpus")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    report_path = Path(args.report)
    output_path.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    documents = []
    files_processed = 0
    findings_total = 0

    for source in iter_markdown_files(input_path):
        files_processed += 1
        rel = source.relative_to(input_path)
        target = output_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        original = source.read_text(encoding="utf-8")
        sanitized, findings = sanitize_text(original)
        findings_total += sum(item["count"] for item in findings)
        target.write_text(sanitized, encoding="utf-8")
        documents.append(
            {
                "source_path": str(source),
                "output_path": str(target),
                "sha256_original": hashlib.sha256(original.encode("utf-8")).hexdigest(),
                "sha256_sanitized": hashlib.sha256(sanitized.encode("utf-8")).hexdigest(),
                "changed": original != sanitized,
                "findings": findings,
                "dry_run": args.dry_run,
            }
        )

    report = {
        "input": str(input_path),
        "output": str(output_path),
        "files_processed": files_processed,
        "findings_total": findings_total,
        "dry_run": args.dry_run,
        "documents": documents,
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"files_processed": files_processed, "findings_total": findings_total, "report": str(report_path)}))


if __name__ == "__main__":
    main()
