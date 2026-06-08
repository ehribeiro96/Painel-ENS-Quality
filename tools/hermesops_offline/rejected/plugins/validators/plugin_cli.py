#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.plugins.plugin_registry import load_registry, list_plugins, get_plugin, format_table


def main(argv=None):
    parser = argparse.ArgumentParser(description='CLI skeleton de plugins')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('args', nargs='*')
    ns = parser.parse_args(argv)
    if ns.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    args = ns.args
    registry = load_registry()
    if not args or args[:2] == ['plugins', 'list']:
        print('Plugin	Status	Env	Risk	CLI	Mode')
        for p in list_plugins(registry):
            print(format_table(p))
        return 0
    if args[:2] == ['plugins', 'status']:
        if len(args) == 2:
            for p in list_plugins(registry):
                print(format_table(p))
            return 0
        p = get_plugin(args[2], registry)
        if not p:
            print('Plugin não encontrado.')
            return 1
        print(p.get('name', 'Plugin'))
        print(f"Status: {p.get('status', 'desconhecido')}")
        print(f"Ambiente: {p.get('environment', 'desconhecido')}")
        print(f"Risco: {p.get('risk_level', 'desconhecido')}")
        return 0
    print('Comando de plugin não implementado.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
