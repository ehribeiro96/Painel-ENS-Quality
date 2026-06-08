#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
ALLOWED_EXTS={'.md', '.json', '.yaml', '.yml', '.ps1', '.py'}

def iter_files(path):
    if path.is_file():
        yield path
        return
    yield from (p for p in sorted(path.rglob('*')) if p.is_file() and p.suffix.lower() in ALLOWED_EXTS)

def main():
    p=argparse.ArgumentParser(description='Validador UTF-8 pt-BR')
    p.add_argument('--path', required=True)
    p.add_argument('--dry-run', action='store_true')
    a=p.parse_args(); path=Path(a.path)
    print('Iniciando verificação de encoding UTF-8.')
    print(f'Caminho: {path}')
    if a.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    if not path.exists():
        print('Arquivo ou diretório ausente.')
        return 1
    failures=[]
    for f in iter_files(path):
        try:
            f.read_text(encoding='utf-8')
        except UnicodeDecodeError as exc:
            failures.append(f'{f}: falha UTF-8 -> {exc}')
    if failures:
        print("\n".join(failures))
        return 2
    print('UTF-8 validado com sucesso.')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
