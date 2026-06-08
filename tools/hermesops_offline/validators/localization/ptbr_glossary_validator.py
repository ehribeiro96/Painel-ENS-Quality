#!/usr/bin/env python3
from __future__ import annotations
import argparse, re
from pathlib import Path
REQ=['preferred_ptbr','allowed_synonyms','avoid','context','keep_english','notes']
TERM_RE=re.compile(r'^([^:#]+):\s*$')
FIELD_RE=re.compile(r'^\s{2}([a-z_]+):\s*(.*)$')

def validate(path):
    cur=None; fields={}; issues=[]
    for n,raw in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
        if not raw.strip():
            continue
        m=TERM_RE.match(raw)
        if m and not raw.startswith(' '):
            if cur is not None:
                miss=[f for f in REQ if f not in fields]
                if miss:
                    issues.append(f'{cur}: faltam campos {", ".join(miss)}')
            cur=m.group(1); fields={}; continue
        m=FIELD_RE.match(raw)
        if m and cur:
            fields[m.group(1)] = m.group(2); continue
        issues.append(f'linha {n}: formato YAML simples inválido')
    if cur is not None:
        miss=[f for f in REQ if f not in fields]
        if miss:
            issues.append(f'{cur}: faltam campos {", ".join(miss)}')
    return issues

def main():
    p=argparse.ArgumentParser(description='Validador simples de glossários pt-BR')
    p.add_argument('--path', required=True)
    p.add_argument('--dry-run', action='store_true')
    a=p.parse_args(); path=Path(a.path)
    print('Iniciando validação de glossários.')
    print(f'Caminho: {path}')
    if a.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    if not path.exists():
        print('Diretório ausente.')
        return 1
    issues=[]
    for f in sorted(path.glob('*.yaml')):
        issues.extend([f'{f}: {m}' for m in validate(f)])
    if issues:
        print('\n'.join(issues))
        return 2
    print('Glossários validados com sucesso.')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
