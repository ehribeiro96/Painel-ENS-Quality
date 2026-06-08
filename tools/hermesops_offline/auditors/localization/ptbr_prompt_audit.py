#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
REQ=['papel','entrada','saída','regras','bloqueios','preservar comandos']

def main():
    p=argparse.ArgumentParser(description='Auditoria de prompts pt-BR')
    p.add_argument('--path', required=True)
    p.add_argument('--dry-run', action='store_true')
    a=p.parse_args(); path=Path(a.path)
    print('Iniciando auditoria de prompts pt-BR.')
    print(f'Caminho: {path}')
    if a.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    if not path.exists():
        print('Diretório ausente.')
        return 1
    issues=[]
    for f in sorted(path.glob('*.md')):
        txt=f.read_text(encoding='utf-8').lower()
        for req in REQ:
            if req not in txt:
                issues.append(f"{f}: falta requisito '{req}'")
    if issues:
        print("\n".join(issues))
        return 2
    print('Prompts pt-BR validados com sucesso.')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
