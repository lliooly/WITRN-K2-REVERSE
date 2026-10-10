"""Offline recording, query and CSV round trip with generated samples."""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from k2up.telemetry import Sample
from k2up.recording import Recording, summary
from k2up.recording_files import export_record, import_record
from k2up.recording_stats import query_record


def main():
    with tempfile.TemporaryDirectory(prefix='k2-recording-demo-') as folder:
        root = Path(folder)
        record = Recording(root / 'source.sqlite', rate=1)
        try:
            for t in range(5):
                record.append(Sample(time=t, voltage=5, current=1, power=5, signed_power=5))
        finally:
            record.close()
        result = query_record(record.path, 1, 3)
        assert result['statistics']['count'] == 3
        assert result['statistics']['coverage'] == 2
        export_record(record.path, root / 'record.csv', 'csv')
        imported = import_record(root / 'record.csv', root / 'imported.sqlite')
        assert imported['count'] == summary(record.path)['count'] == 5
        print('Offline recording: write, query, integration and CSV round trip passed.')


if __name__ == '__main__':
    main()
