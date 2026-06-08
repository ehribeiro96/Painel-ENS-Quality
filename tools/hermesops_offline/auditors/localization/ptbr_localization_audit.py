#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LOCAL=ROOT/'localization'
TOOLS=ROOT/'tools'/'localization'
SCRIPTS=[
    (TOOLS/'ptbr_encoding_check.py', ['--path', str(LOCAL), '--dry-run']),
    (TOOLS/'ptbr_message_catalog_validator.py', ['--path', str(LOCAL/'messages'), '--dry-run']),
    (TOOLS/'ptbr_prompt_audit.py', ['--path', str(LOCAL/'prompts'), '--dry-run']),
    (TOOLS/'ptbr_glossary_validator.py', ['--path', str(LOCAL/'glossary'), '--dry-run']),
]

def main():
    p=argparse.ArgumentParser(description='Auditoria consolidada pt-BR')
    p.add_argument('--dry-run', action='store_true')
    a=p.parse_args()
    print('Iniciando auditoria consolidada pt-BR.')
    if a.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    issues=[]
    for script, extra in SCRIPTS:
        proc=subprocess.run([sys.executable, str(script), *extra], capture_output=True, text=True)
        print(proc.stdout, end='')
        if proc.returncode != 0:
            issues.append(f'{script.name} retornou código {proc.returncode}')
            if proc.stderr:
                print(proc.stderr, end='')
    if issues:
        print('\n'.join(issues))
        return 2
    print('Auditoria consolidada pt-BR concluída com sucesso.')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
