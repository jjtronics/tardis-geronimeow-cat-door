"""Archives a joindre a une release GitHub : plateaux 3MF, STL et configuration ESPHome.

    python3 scripts/archives_release.py [version]      # version par defaut : v8

Ecrit dist/tardis-geronimeow-<version>-{3mf,stl,esphome}.zip. Chaque archive contient un
dossier du meme nom et la licence qui s'applique (LICENSE.md ou LICENSE-CODE).
"""
from pathlib import Path
import sys, zipfile

ROOT = Path(__file__).resolve().parent.parent
VERSION = sys.argv[1] if len(sys.argv) > 1 else 'v8'
DIST = ROOT / 'dist'; DIST.mkdir(exist_ok=True)
CONTENTS = {
    '3mf': (sorted((ROOT / 'tardis_v8' / '3mf').glob('*.3mf')), ROOT / 'LICENSE.md'),
    'stl': (sorted((ROOT / 'tardis_v8' / 'stl').glob('*.stl')), ROOT / 'LICENSE.md'),
    'esphome': ([ROOT / 'tardis_v8' / 'esphome' / 'chatiere-tardis.yaml',
                 ROOT / 'tardis_v8' / 'esphome' / 'secrets.yaml.example'], ROOT / 'LICENSE-CODE'),
}
for kind, (files, licence) in CONTENTS.items():
    name = f'tardis-geronimeow-{VERSION}-{kind}'
    with zipfile.ZipFile(DIST / f'{name}.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for f in files + [licence]:
            z.write(f, f'{name}/{f.name}')
    print(DIST / f'{name}.zip', len(files), 'fichiers')
