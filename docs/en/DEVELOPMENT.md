# Regenerating and maintaining the project — V8

**[Version française](../DEVELOPPEMENT.md)**

## Tools

| Tool | Version used |
| --- | --- |
| Blender | 5.0.1, macOS app |
| Creality Print | 7.3.1 (opening and slicing, GUI and command line) |
| lib3mf, Pillow | see `requirements-tools.txt` |
| FFmpeg | 8.1 |
| ESPHome | 2025.5 (configuration validation only) |

The Blender generators use `bpy`, `bmesh` and `mathutils`, which ship with Blender. The
other scripts use Python with the dependencies in `requirements-tools.txt`:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-tools.txt
```

FFmpeg must be on the `PATH`. On macOS, Blender is called as
`/Applications/Blender.app/Contents/MacOS/Blender`, and Creality Print is looked for in
`/Applications/Creality Print.app`. The scripts load Arial from the macOS system fonts.
Adapt these paths on another system.

Code comments and file names are in French.

## Model and plates

From the repository root:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python tardis_v8/generate.py
```

`generate.py` writes the STL files, the 12 3MF plates (already converted into Creality
Print projects), the reference assembly, `verification.json` (including the cam
envelope check), the Blender model and three renders. Add `-- --no-render` to skip the
renders. Parameters are at the top of the file: door thickness, cam slopes, lock,
magnets, sensor, grooves, template.

Conversion into Creality Print projects is done by `scripts/exporter_projets_creality.py`,
called by the generator. It takes the settings from the templates in
`scripts/modeles_creality/`, then adds the prime tower, colours and per-object settings
of the generated file.

## Checks

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python tardis_v8/verify_geometry.py
.venv/bin/python tardis_v8/verify_3mf.py
python3 scripts/trancher_creality_print.py tardis_v8
python3 scripts/audit_tours.py
```

- `verify_geometry.py`: closed assembly, swing for all three cams, stops, lock (fine
  sweep), turn latch, magnets. Results in `controle_geometrie.json`.
- `verify_3mf.py`: independent reading of the 3MF files with lib3mf
  (`controle_3mf.json`).
- `trancher_creality_print.py`: slices every plate with the Creality Print command line
  (`controle_tranchage.json`: time, weight, colours, conflicts).
- `audit_tours.py`: every 3MF in the repository, native project and prime tower away
  from the parts.

Blender may return a zero exit code even when its script raises an exception: also
read the JSON reports and the output. Opening and slicing in the Creality Print GUI is
checked by hand, plate by plate.

## Figures and video

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/vignettes_plateaux.py -- tardis_v8
.venv/bin/python scripts/planche_plateaux.py tardis_v8
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_came.py -- tardis_v8
.venv/bin/python scripts/planche_came.py tardis_v8
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_details_v8.py -- tardis_v8
.venv/bin/python scripts/planche_details_v8.py tardis_v8
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_cablage.py -- tardis_v8
.venv/bin/python scripts/planche_cablage.py tardis_v8
.venv/bin/python scripts/schema_eclairage.py tardis_v8
.venv/bin/python scripts/figure_gabarit.py tardis_v8
/Applications/Blender.app/Contents/MacOS/Blender --background --python tardis_v8/visualisations/render_visuals.py -- montage
python3 tardis_v8/visualisations/compose_montage.py        # French captions
python3 tardis_v8/visualisations/compose_montage.py en     # English captions
.venv/bin/python scripts/couverture.py                     # cover images
.venv/bin/python scripts/annoter_captures.py               # annotated Creality Print screenshots
```

The video (78 s, 1280 × 720) is rendered frame by frame in EEVEE. `render_visuals.py`
records, for each frame, the screen position of the labelled parts;
`compose_montage.py` adds titles, texts and labels, then encodes the MP4 and the GIF.
`-- test` renders fourteen check frames.

The Creality Print screenshots are taken by hand in the GUI (full screen, window
maximised) and stored in `docs/images/creality/brut/`; frames and captions are added by
`scripts/annoter_captures.py`, which writes the French and English versions. For a new
screenshot, adjust the frame coordinates in that script.

## ESPHome

```sh
pip install esphome
cp tardis_v8/esphome/secrets.yaml.example tardis_v8/esphome/secrets.yaml   # then fill it in
esphome config tardis_v8/esphome/chatiere-tardis.yaml
```

## Files

The repository only contains V8; earlier iterations are described (in French) in
[HISTORIQUE.md](../HISTORIQUE.md).

Git ignores intermediate images (`montage_frames/`, `montage_legende*/`), ESPHome
secrets (`secrets.yaml`), `.blend1` backups, logs and caches. Blender models, STL, 3MF,
renders, GIF and MP4 are versioned.

After regenerating, refresh the SHA-256 inventory:

```sh
python3 scripts/update_inventory.py
```
