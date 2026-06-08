
#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / 'plugins' / 'plugin_registry.yaml'


def _scalar(value: str):
    value = value.strip()
    if value.lower() in {'true', 'false'}:
        return value.lower() == 'true'
    if value.lower() in {'null', 'none', '~'}:
        return None
    return value.strip('"').strip("'")


def load_registry(path: Path = REGISTRY):
    plugins = []
    current = None
    if not path.exists():
        return {'plugins': []}
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(' '))
        if stripped == 'plugins:':
            continue
        if indent == 2 and stripped.startswith('- '):
            if current:
                plugins.append(current)
            current = {}
            item = stripped[2:]
            if ':' in item:
                k, v = item.split(':', 1)
                current[k.strip()] = _scalar(v)
            continue
        if current is None:
            continue
        if indent == 4 and ':' in stripped and not stripped.endswith(':'):
            k, v = stripped.split(':', 1)
            current[k.strip()] = _scalar(v)
            continue
        if indent == 4 and stripped.endswith(':'):
            current[stripped[:-1].strip()] = {}
    if current:
        plugins.append(current)
    return {'plugins': plugins}


def list_plugins(registry=None):
    registry = registry or load_registry()
    return registry.get('plugins', [])


def get_plugin(name: str, registry=None):
    for plugin in list_plugins(registry):
        if plugin.get('id') == name:
            return plugin
    return None


def format_table(plugin):
    return f"{plugin.get('id','')}	{plugin.get('status','')}	{plugin.get('environment','')}	{plugin.get('risk_level','')}	{'yes' if plugin.get('cli_visible') else 'no'}	{plugin.get('default_mode','')}"


def main(argv=None):
    parser = argparse.ArgumentParser(description='Registry de plugins do HermesOps')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('command', nargs='*')
    args = parser.parse_args(argv)
    registry = load_registry()
    if args.json:
        print(json.dumps(registry, ensure_ascii=False, indent=2))
        return 0
    if args.dry_run:
        print('Modo dry-run ativo. Nenhuma alteração será aplicada.')
    cmd = args.command[:]
    if not cmd or cmd[:2] == ['plugins', 'list']:
        print('Plugin	Status	Env	Risk	CLI	Mode')
        for plugin in list_plugins(registry):
            print(format_table(plugin))
        return 0
    if cmd[:2] == ['plugins', 'status']:
        if len(cmd) == 2:
            for plugin in list_plugins(registry):
                print(format_table(plugin))
            return 0
        plugin = get_plugin(cmd[2], registry)
        if not plugin:
            print('Plugin não encontrado.')
            return 1
        print(plugin.get('name', 'Plugin'))
        print(f"Status: {plugin.get('status', 'desconhecido')}")
        print(f"Ambiente: {plugin.get('environment', 'desconhecido')}")
        print(f"Risco: {plugin.get('risk_level', 'desconhecido')}")
        return 0
    print('Comando não implementado nesta fase.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
