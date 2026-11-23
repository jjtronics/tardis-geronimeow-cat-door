"""Audit de tous les plateaux 3MF du depot : projet Creality Print natif, et tour de
purge (plateaux multicolores) hors des pieces et dans le plateau.

    python3 scripts/audit_tours.py
"""
import glob, json, re, zipfile

CORE = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
problems = 0
for f in sorted(glob.glob('*/3mf/*.3mf')):
    z = zipfile.ZipFile(f)
    model = z.read('3D/3dmodel.model').decode()
    native = 'Creality_Print' in model
    s = json.loads(z.read('Metadata/project_settings.config'))
    # Boites des objets (sommets deja en coordonnees plateau dans ces fichiers).
    boxes, slots = [], set()
    for obj in re.finditer(r'<object id="\d+"[^>]*?(?:pindex="(\d+)")?[^>]*>(.*?)</object>', model, re.S):
        if obj.group(1) is not None:
            slots.add(obj.group(1))
        xs = [float(v) for v in re.findall(r' x="([-\d.]+)"', obj.group(2))]
        ys = [float(v) for v in re.findall(r' y="([-\d.]+)"', obj.group(2))]
        if xs:
            boxes.append((min(xs), min(ys), max(xs), max(ys)))
    issue = []
    if not native:
        issue.append('pas un projet Creality Print')
    if len(slots) > 1:
        tx, ty = float(s['wipe_tower_x'][0]), float(s['wipe_tower_y'][0])
        w = float(s.get('prime_tower_width', ['35'])[0] if isinstance(s.get('prime_tower_width'), list) else s.get('prime_tower_width', 35))
        tower = (tx - 3, ty - 3, tx + w + 3, ty + 30 + 3)
        hit = [b for b in boxes if b[0] < tower[2] and b[2] > tower[0] and b[1] < tower[3] and b[3] > tower[1]]
        if hit:
            issue.append(f'tour ({tx:g}, {ty:g}) sur {len(hit)} objet(s)')
        if tower[3] > 300 or tower[2] > 300:
            issue.append('tour hors plateau')
    if issue:
        problems += 1
        print('PROBLEME', f, '·', ' ; '.join(issue))
print('plateaux avec probleme :', problems)
