"""Tranche tous les projets 3MF d'une version avec le moteur de Creality Print (macOS).

    python3 scripts/trancher_creality_print.py tardis_v8

Chaque projet est tranche tel quel, avec ses propres reglages (ceux poses par
exporter_projets_creality.py : K1 Max 0,4 mm, 0,20 mm Standard, Hyper PLA ou CR-TPU,
purge x 1,3, tour de purge du plateau). Mode ligne de commande de Creality Print
7.3 (--cli) ; contrairement a la 7.2.1, il ne plante plus sur les plateaux
multicolores. Le resultat est ecrit dans <version>/controle_tranchage.json.
"""
import glob, json, os, re, subprocess, sys, tempfile, time, zipfile
import xml.etree.ElementTree as ET

APP = '/Applications/Creality Print.app'
CP = APP + '/Contents/MacOS/CrealityPrint'
MOVE = re.compile(r'([XYE])(-?\d+\.?\d*)')


def project_info(src):
    with zipfile.ZipFile(src) as z:
        settings = json.loads(z.read('Metadata/project_settings.config'))
        config = ET.fromstring(z.read('Metadata/model_settings.config'))
    slots = set()
    meta = lambda n: {m.get('key'): m.get('value') for m in n.findall('metadata')}
    for obj in config.iter('object'):
        for part in obj.iter('part'):
            if part.get('subtype', 'normal_part') == 'normal_part':
                slots.add(int(meta(part).get('extruder', meta(obj).get('extruder', 1))))
    return dict(extruders=sorted(slots), printer=settings.get('printer_settings_id'),
                tower=[settings.get('wipe_tower_x'), settings.get('wipe_tower_y')])


def read_gcode(path):
    head, boxes, kind, x, y = {'tool_changes': -1}, {}, None, None, None
    for line in open(path, errors='replace'):
        if re.match(r'T\d', line):
            head['tool_changes'] += 1
        if line.startswith('; ') and ' = ' in line:
            k, v = line[2:].split(' = ', 1); head[k.strip()] = v.strip()
        elif line.startswith(';TYPE:'):
            kind = line[6:].strip()
        elif line.startswith(('G0', 'G1')):
            d = {k: float(v) for k, v in MOVE.findall(line)}
            nx, ny = d.get('X', x), d.get('Y', y)
            if d.get('E', 0) > 0 and kind not in (None, 'Custom') and nx is not None:
                b = boxes.setdefault('tower' if kind == 'Prime tower' else 'part', [1e9, 1e9, -1e9, -1e9])
                b[:] = min(b[0], nx), min(b[1], ny), max(b[2], nx), max(b[3], ny)
            x, y = nx, ny
    return head, boxes


def slice_version(version, work):
    plates = []
    for src in sorted(glob.glob(f'{version}/3mf/*.3mf')):
        name = os.path.basename(src)[:-4]
        out = f'{work}/{os.path.basename(version)}_{name}'; os.makedirs(out)
        info = project_info(src)
        start = time.time()
        run = subprocess.run([CP, '--cli', '--datadir', f'{work}/datadir', '--slice', '0',
                              '--need-gcode-file', '--outputdir', out, os.path.abspath(src)],
                             capture_output=True, text=True, timeout=1800)
        log = run.stdout + run.stderr
        r = dict(plate=name, rc=run.returncode, seconds=round(time.time() - start),
                 conflicts=sorted(set(re.findall(r'gcode path conflicts found between (.*)', log))),
                 printer=info['printer'], tower_setting=info['tower'])
        gcode = f'{out}/plate_1.gcode'
        if os.path.exists(gcode):
            head, boxes = read_gcode(gcode)
            grams = [float(v) for v in head['filament used [g]'].split(',')]
            used = [i + 1 for i, g in enumerate(grams) if g > 0]
            layers = re.search(r'^; total layer number: (\d+)', open(gcode).read(4000), re.M)
            r.update(layers=int(layers.group(1)) if layers else None,
                     time=head.get('estimated printing time (normal mode)'),
                     grams_per_filament=grams, grams=round(sum(grams), 1),
                     color_changes=int(head.get('total filament change', max(head['tool_changes'], 0))),
                     filament_colour=head.get('filament_colour'),
                     slots_assigned=info['extruders'], slots_used=used,
                     part_xy=[round(v, 1) for v in boxes.get('part', [])])
            r['ok'] = run.returncode == 0 and not r['conflicts'] and used == info['extruders']
        else:
            r['ok'] = False
        print(('OK ' if r['ok'] else 'KO ') + json.dumps(r, ensure_ascii=False), flush=True)
        plates.append(r)
    return plates


def main():
    version_line = subprocess.run(['defaults', 'read', APP + '/Contents/Info', 'CFBundleShortVersionString'],
                                  capture_output=True, text=True).stdout.strip()
    failed = False
    with tempfile.TemporaryDirectory() as work:
        for version in sys.argv[1:]:
            plates = slice_version(os.path.abspath(version), work)
            report = dict(outil=f'Creality Print {version_line} en ligne de commande (--cli), reglages du projet, '
                                'verification des conflits G-code activee',
                          plates=plates)
            json.dump(report, open(f'{version}/controle_tranchage.json', 'w'), indent=1, ensure_ascii=False)
            failed |= not all(p['ok'] for p in plates)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
