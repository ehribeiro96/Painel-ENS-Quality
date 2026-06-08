#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

SENSITIVE = re.compile(r'(?i)(token|secret|password|senha|credential|api[_-]?key)')


def sanitize_line(line: str) -> str:
    if SENSITIVE.search(line):
        return SENSITIVE.sub('[REDACTED]', line)
    return line


def main(argv=None):
    parser = argparse.ArgumentParser(description='Sanitizador de logs de plugin')
    parser.add_argument('--input', required=False)
    parser.add_argument('--output', required=False)
    parser.add_argument('--dry-run', action='store_true')
    ns = parser.parse_args(argv)
    if ns.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    if not ns.input:
        print('Nenhum arquivo de entrada informado.')
        return 0
    src = Path(ns.input)
    text = src.read_text(encoding='utf-8') if src.exists() else ''
    sanitized = '\n'.join(sanitize_line(line) for line in text.splitlines())
    if ns.output:
        Path(ns.output).write_text(sanitized + '\n', encoding='utf-8')
    else:
        print(sanitized)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
