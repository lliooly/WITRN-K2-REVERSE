"""Check developer documentation against explicit Python entries and bridge operations."""
import ast
import json
from pathlib import Path
import re
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def signature(name, node):
    args = ast.unparse(node.args)
    for prefix in ('self', 'cls'):
        if args == prefix:
            args = ''
        elif args.startswith(prefix + ', '):
            args = args[len(prefix) + 2:]
    if any(isinstance(d, ast.Name) and d.id == 'property' for d in node.decorator_list):
        return name
    caller_name = name.split('.')[0] if name.endswith('.__init__') else name
    return caller_name + '(' + args + ')'


def main():
    expected = {}
    for path in (ROOT / 'k2up').glob('*.py'):
        for node in ast.parse(path.read_text()).body:
            entries = []
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                entries.append((node.name, node))
            if isinstance(node, ast.ClassDef):
                entries.extend((node.name + '.' + fn.name, fn) for fn in node.body
                               if isinstance(fn, ast.FunctionDef) and
                               (not fn.name.startswith('_') or fn.name == '__init__'))
            for name, fn in entries:
                expected[(path.stem, name)] = (signature(name, fn), fn.lineno)
    index = json.loads((ROOT / 'api/python-functions.json').read_text())
    entries = index['functions']
    documented = {(e['module'], e['name']): (e['signature'], e['line']) for e in entries}
    assert len(entries) == len(documented) == index['count']
    assert expected == documented, 'Python API signature or coverage differs from documentation'
    rendered = (ROOT / 'api/python-reference.md').read_text()
    for entry in entries:
        assert entry['purpose'] and entry['returns'] and entry['effects']
        assert '`' + entry['signature'] + '`' in rendered
        assert f"../k2up/{entry['module']}.py#L{entry['line']}" in rendered
    from k2up.gui_bridge import OPERATIONS
    bridge = (ROOT / 'api/bridge.md').read_text()
    operations = set(re.findall(r'^\| `([a-z-]+)` \|', bridge, re.MULTILINE)) & OPERATIONS
    assert operations == OPERATIONS, 'JSON operations are missing documentation'
    assert 'mailto:1604047731@qq.com' in (ROOT / 'TAKEDOWN.md').read_text()
    for path in ROOT.rglob('*.md'):
        if '.git' in path.parts:
            continue
        for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', path.read_text()):
            if ':' in link or link.startswith('#'):
                continue
            target = path.parent / link.split('#')[0]
            assert target.exists(), f'Broken relative link: {path.relative_to(ROOT)} -> {link}'
    print(f'{len(entries)} Python entries, {len(OPERATIONS)} JSON operations and relative links verified.')


if __name__ == '__main__':
    main()
