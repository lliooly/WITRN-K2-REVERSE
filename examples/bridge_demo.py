"""Cross-language process contract exercised without HID or vendor files."""
import json
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def call(operation, **fields):
    request = dict(id=str(uuid.uuid4()), operation=operation, simulation=True,
                   demo_delay_ms=0, **fields)
    run = subprocess.run([sys.executable, str(ROOT / 'k2_gui_backend.py')],
                         input=json.dumps(request) + '\n', text=True, capture_output=True,
                         cwd=ROOT, timeout=30)
    events = [json.loads(line) for line in run.stdout.splitlines()]
    assert run.returncode == 0, (run.stderr, events)
    assert all(e['id'] == request['id'] and e['schema'] == 1 for e in events)
    assert not any(e['event'] == 'error' for e in events)
    return next(e['value'] for e in events if e['event'] == 'result')


def main():
    device = call('devices')['devices'][0]
    assert bytes.fromhex(device['path_hex']) == b'K2-OFFLINE-DEMO'
    with tempfile.TemporaryDirectory(prefix='k2-bridge-demo-') as directory:
        probe = call('probe', data_directory=directory)
        assert probe['identity']['confirmed_k2']
        resource = call('resource-read', data_directory=directory, resource_kind='layout')
        assert resource['resource_valid']
        assert Path(resource['resource_path']).stat().st_size == 400
        assert resource['backup']['simulation_only']
    print('Offline bridge: NDJSON events, device enumeration, probe and resource read passed.')


if __name__ == '__main__':
    main()
