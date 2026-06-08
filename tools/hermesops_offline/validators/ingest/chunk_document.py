#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

MAX_CHARS = 2500
OVERLAP = 300
FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
KV_RE = re.compile(r"^([A-Za-z0-9_]+):\s*(.*)$")


def iter_markdown_files(path: Path):
    if path.is_file() and path.suffix.lower() == ".md":
        yield path
        return
    for item in sorted(path.rglob("*.md")):
        if item.is_file():
            yield item


def parse_scalar(raw: str):
    value = raw.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip('"') for part in inner.split(",")]
    return value


def parse_front_matter(text: str):
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}, text
    front_matter, body = match.groups()
    meta = {}
    current_list_key = None
    for line in front_matter.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_list_key:
            meta.setdefault(current_list_key, []).append(line[4:].strip().strip('"'))
            continue
        kv = KV_RE.match(line)
        if not kv:
            current_list_key = None
            continue
        key, raw = kv.groups()
        parsed = parse_scalar(raw)
        if raw.strip() == "":
            meta[key] = []
            current_list_key = key
            continue
        meta[key] = parsed
        current_list_key = None
        if raw.strip() == "[]":
            meta[key] = []
    return meta, body.strip()


def split_chunks(text: str):
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + MAX_CHARS)
        if end < len(text):
            newline = text.rfind("\n", start, end)
            if newline > start + 500:
                end = newline
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(0, end - OVERLAP)
    return chunks


def main():
    parser = argparse.ArgumentParser(description="Chunk sanitized markdown corpus into JSONL")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    records = []
    doc_count = 0
    for source in iter_markdown_files(input_path):
        text = source.read_text(encoding="utf-8")
        meta, body = parse_front_matter(text)
        if not meta.get("id"):
            continue
        doc_count += 1
        document_id = meta.get("id", source.stem)
        chunks = split_chunks(body)
        for index, chunk_text in enumerate(chunks, start=1):
            records.append(
                {
                    "chunk_id": f"{document_id}::chunk-{index:03d}",
                    "document_id": document_id,
                    "source_path": str(source),
                    "title": meta.get("title", source.stem),
                    "document_type": meta.get("document_type", ""),
                    "domain": meta.get("domain", ""),
                    "risk_level": meta.get("risk_level", ""),
                    "sensitivity": meta.get("sensitivity", ""),
                    "external_model_allowed": meta.get("external_model_allowed", True),
                    "text": chunk_text,
                }
            )

    with output_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(json.dumps({"documents": doc_count, "chunks": len(records), "output": str(output_path)}))


if __name__ == "__main__":
    main()
