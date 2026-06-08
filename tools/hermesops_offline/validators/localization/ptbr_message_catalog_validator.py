#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def iter_files(path):
    if path.is_file():
        yield path; return
    yield from sorted(path.glob('*.json'))

def main():
    p=argparse.ArgumentParser(description='Validador de catálogos JSON pt-BR')
    p.add_argument('--path', required=True)
    p.add_argument('--dry-run', action='store_true')
    a=p.parse_args(); path=Path(a.path)
    print('Iniciando validação de catálogos de mensagens.')
    print(f'Caminho: {path}')
    if a.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    if not path.exists():
        print('Diretório ausente.')
        return 1
    failures=[]
    for f in iter_files(path):
        try:
            data=json.loads(f.read_text(encoding='utf-8'))
        except Exception as exc:
            failures.append(f'{f}: JSON inválido -> {exc}')
            continue
        if not isinstance(data, dict) or not data:
            failures.append(f'{f}: catálogo vazio ou estrutura inválida')
    if failures:
        print('\n'.join(failures))
        return 2
    print('Catálogos de mensagens validados com sucesso.')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
