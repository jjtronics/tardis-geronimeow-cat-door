"""Régénérer docs/INVENTAIRE.json à partir des fichiers suivis ou à ajouter."""
from __future__ import annotations

from datetime import date
from hashlib import sha256
from pathlib import Path
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "INVENTAIRE.json"


def repository_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths = [ROOT / item.decode() for item in result.stdout.split(b"\0") if item]
    return sorted(path for path in paths if path != OUTPUT and path.is_file())


files = repository_files()
entries = []
for path in files:
    data = path.read_bytes()
    entries.append(
        {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": len(data),
            "sha256": sha256(data).hexdigest(),
        }
    )

inventory = {
    "date": date.today().isoformat(),
    "repository": "jjtronics/tardis-geronimeow-cat-door",
    "current_version": "V8",
    "file_count": len(entries),
    "total_bytes": sum(entry["bytes"] for entry in entries),
    "excluded_generated_directories": [
        "montage_frames",
        "montage_legende",
        "montage_v6_frames",
        "modes_frames",
        "modes_video_frames",
    ],
    "note": "Inventaire des fichiers utiles. Le fichier inventaire ne se recense pas lui-même.",
    "files": entries,
}
OUTPUT.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n")
print(f"{len(entries)} fichiers, {inventory['total_bytes']} octets")
