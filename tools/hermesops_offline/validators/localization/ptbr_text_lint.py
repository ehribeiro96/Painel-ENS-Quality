#!/usr/bin/env python3
from __future__ import annotations
import argparse, re
from pathlib import Path
ALLOWED_EXTS={'.md', '.json', '.yaml', '.yml', '.ps1', '.py'}
AVOID=['ticket','workaround','fix final']
PLACEHOLDER_RE=re.compile(r'\{\{.*?\}\}|\{[A-Za-z0-9_]+\}')

def iter_files(path):
    if path.is_file():
        yield path
        return
    yield from (p for p in sorted(path.rglob('*')) if p.is_file() and p.suffix.lower() in ALLOWED_EXTS)

def analyze(text):
    issues=[]
    low=text.lower()
    for term in AVOID:
        if term in low:
            issues.append(f'termo a evitar encontrado: {term}')
    if '{' in text and not PLACEHOLDER_RE.search(text):
        issues.append('possível placeholder malformado')
    if not any(ch in text for ch in 'áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ'):
        issues.append('nenhuma acentuação detectada; validar se o arquivo deveria conter português')
    return issues

def main():
    p=argparse.ArgumentParser(description='Linter simples de texto pt-BR')
    p.add_argument('--path', required=True)
    p.add_argument('--dry-run', action='store_true')
    a=p.parse_args(); path=Path(a.path)
    print('Iniciando lint pt-BR.')
    print(f'Caminho: {path}')
    if a.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    if not path.exists():
        print('Arquivo ou diretório ausente.')
        return 1
    issues=[]
    for f in iter_files(path):
        for i in analyze(f.read_text(encoding='utf-8')):
            issues.append(f'{f}: {i}')
    if issues:
        print("\n".join(issues))
        return 2
    print('Lint pt-BR concluído sem bloqueios.')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
