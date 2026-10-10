"""Generate or verify hashes for distributable files without including local outputs."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".venv", ".venv-app", "__pycache__", ".pytest_cache", "build", "dist", ".build", "inputs", "artifacts", "research-output", "k2_logs", "k2_backups", "k2_recordings"}
BLOCKED_DIRS = {"dotnet", "tables", "firmware", "validation", "decompiled", "native-decompiled", "focused"}
BLOCKED_SUFFIXES = {".dll", ".exe", ".pdb", ".k2", ".zip", ".i64", ".idb", ".id0", ".id1", ".id2", ".nam", ".til", ".cs", ".sqlite", ".sqlite3", ".db", ".jsonl", ".k2project", ".k2image", ".k2emark", ".k2emarkbin", ".wtemark"}


def entries():
    found = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED for part in relative.parts):
            continue
        if not path.is_file() or path.name in {"MANIFEST.json", ".DS_Store"}:
            continue
        name = relative.as_posix()
        if path.is_symlink():
            raise ValueError("Symlinks are not publication inputs: " + name)
        if (relative.parts[0] == "reverse" and any(part in BLOCKED_DIRS for part in relative.parts[1:])) or path.suffix in BLOCKED_SUFFIXES:
            raise ValueError("Local or vendor artifact found: " + name)
        if path.suffix == ".bin" and name != "k2up/data/firmware_decode.bin":
            raise ValueError("Unexpected binary data: " + name)
        data = path.read_bytes()
        found.append({"path": name, "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = ROOT / "MANIFEST.json"
    try:
        expected = {"schema": 1, "hash_algorithm": "SHA-256", "scope": "All distributable files except MANIFEST.json itself; caches and local outputs excluded.", "files": entries()}
        if args.check:
            if json.loads(manifest.read_text()) != expected:
                raise ValueError("Manifest differs; run python3 tools/manifest.py and review changes.")
        else:
            manifest.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n")
        print(str(len(expected["files"])) + " publication files " + ("verified" if args.check else "indexed"))
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
