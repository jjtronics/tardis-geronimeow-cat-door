"""Rendus de detail de la V8 : cames rapportees, verrou central, aimants et capteur.

    /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_details_v8.py -- tardis_v8

Ecrit dans <version>/images/ : detail_cames.png, detail_verrou_libre.png,
detail_verrou_ferme.png, detail_aimants_bas.png, detail_capteur_haut.png.
Les planches legendees sont faites par scripts/planche_details_v8.py.
"""
from pathlib import Path
import bpy, json, sys
from mathutils import Matrix, Vector

version = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(next(version.glob('tardis_*.blend'))))
P = json.loads((version / 'verification.json').read_text())['parameters']
H = P['opening_height']
scene = bpy.context.scene
out = version / 'images'; out.mkdir(exist_ok=True)


def mat(name, rgb, metal=0., rough=.45, alpha=1.):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value = (*rgb, 1); n.inputs['Metallic'].default_value = metal
    n.inputs['Roughness'].default_value = rough; n.inputs['Alpha'].default_value = alpha
    return m

BLUE, IVORY = mat('bleu', (.03, .09, .2)), mat('ivoire', (.86, .78, .6))
BRASS, STEEL = mat('laiton', (.62, .45, .2), .7, .3), mat('acier', (.6, .63, .66), .85, .25)
MAG, GLASS = mat('aimant', (.25, .27, .3), .6, .3), mat('verre', (.6, .85, .9), 0, .1)
RED = mat('cale', (.75, .2, .15))

for o in list(bpy.data.objects):
    if o.type == 'LIGHT':
        bpy.data.objects.remove(o, do_unlink=True)
world = scene.world; world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs[0].default_value = (.93, .92, .89, 1); bg.inputs[1].default_value = .55
for loc, power in (((-300, -400, 300), 900000), ((300, -200, 150), 500000), ((0, 400, 300), 500000)):
    bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object
    l.data.energy = power; l.data.size = 300
    l.rotation_euler = (Vector((0, 0, 50)) - l.location).to_track_quat('-Z', 'Y').to_euler()
cam = scene.camera
scene.render.engine = 'BLENDER_EEVEE'; scene.render.film_transparent = False
scene.view_settings.view_transform = 'Standard'
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
base = {o.name: o.matrix_world.copy() for o in meshes}


def paint(o):
    if o.get('hardware'):
        n = o.name
        m = MAG if 'aimant' in n else GLASS if 'ILS' in n else STEEL
    elif o.get('print_group') == '28_Cales_aimants':
        m = RED
    elif o.get('central_lock') and 'bouton' in o.name:
        m = BRASS
    else:
        m = IVORY if o.get('moving_side') else BLUE
    o.data.materials.clear(); o.data.materials.append(m)


def show(pred):
    for o in meshes:
        o.hide_render = not pred(o)


def look(target, offset, ortho, res=(900, 700)):
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = ortho
    cam.location = Vector(target) + Vector(offset)
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = res


def shot(name):
    scene.render.filepath = str(out / name); bpy.ops.render.render(write_still=True)


def section(o, lo, hi):
    # Copie coupee par une boite (vue en coupe), sans toucher l'original.
    c = o.copy(); c.data = o.data.copy(); bpy.context.collection.objects.link(c)
    bpy.ops.mesh.primitive_cube_add(size=1, location=[(a + b) / 2 for a, b in zip(lo, hi)])
    b = bpy.context.object; b.dimensions = [h - l for l, h in zip(lo, hi)]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    m = c.modifiers.new('coupe', 'BOOLEAN'); m.operation = 'INTERSECT'; m.solver = 'EXACT'; m.object = b
    bpy.context.view_layer.objects.active = c; bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(b, do_unlink=True); c.hide_render = False; paint(c); return c


for o in meshes:
    paint(o)

# 1. Les trois cames rapportees cote a cote (3,5 / 4,5 / 5,5 mm).
cams = sorted([o for o in meshes if o.get('print_group') == '29_Cames_rapportees' and o.name.endswith('_gauche')],
              key=lambda o: o['cam_rise'])
show(lambda o: o in cams)
for k, c in enumerate(cams):
    c.matrix_world = Matrix.Translation((k * 16, 0, 0)) @ base[c.name]
    c.hide_render = False
center = sum((c.matrix_world.translation for c in cams), Vector()) / 3
mid = Vector((-P['opening_width'] / 2 + 5 + 16, -5, 45))
look(mid, (-40, -100, 45), 52, (1000, 600)); shot('detail_cames.png')
for c in cams:
    c.matrix_world = base[c.name]

# 2. Verrou central, vu de face, facade coupee au plan y = -5 (milieu des battants).
lock = [o for o in meshes if o.get('central_lock') and o.name.startswith('lame')]
cut_lo, cut_hi = (-35, -5, -20), (35, 30, 14)
show(lambda o: False)
cuts = [section(o, cut_lo, cut_hi) for o in meshes
        if (o.get('print_group') in ('01_Cadre',) and o.name.startswith('cadre')) or
        (o.get('moving_side') and not o.get('sample_only') and o.name.startswith('battant'))]
for o in lock:
    o.hide_render = False
look((0, -5, -4), (0, -200, 0), 62)
shot('detail_verrou_libre.png')
for o in lock:
    o.matrix_world = Matrix.Translation((0, 0, 5.5)) @ base[o.name]
shot('detail_verrou_ferme.png')
for o in lock:
    o.matrix_world = base[o.name]
for c in cuts:
    bpy.data.objects.remove(c, do_unlink=True)

# 2 bis. Vue de face du bas : bouton monte, tourniquet tourne dessous (FERME).
allock = [o for o in meshes if o.get('central_lock')]
show(lambda o: (o.name.startswith('cadre_monobloc') or o in allock or
                (o.get('moving_side') and not o.get('sample_only') and o.name.startswith('battant'))))
turn = next(o for o in allock if o.get('turnstile_pivot'))
pv = Vector(turn['turnstile_pivot'])
for o in allock:
    if o is turn:
        o.matrix_world = Matrix.Translation(pv) @ Matrix.Rotation(-1.5708, 4, 'Y') @ Matrix.Translation(-pv) @ base[o.name]
    else:
        o.matrix_world = Matrix.Translation((0, 0, 5.5)) @ base[o.name]
look((3, -20, -7), (0, -200, 25), 46)
shot('detail_verrou_tourniquet.png')
for o in allock:
    o.matrix_world = base[o.name]

# 3. Aimants anti-vent (bas) et capteur (haut), coupe au plan x = 20 (axe des aimants).
x = P['magnet_x']
show(lambda o: False)
keep = [o for o in meshes if not o.get('sample_only') and not o.get('hardware') and
        (o.name.startswith('cadre_monobloc') or (o.get('moving_side') == 1 and o.name.startswith('battant')))]
cuts = [section(o, (x, -30, -20), (x + 40, 10, 215)) for o in keep]
for o in meshes:
    if (o.get('hardware') and ('aimant' in o.name or 'ILS' in o.name) and o.name.endswith('droite')) or \
            (o.get('print_group') == '28_Cales_aimants' and not o.get('sample_only') and o.name.endswith('droite_1')):
        o.hide_render = False
look((x, -5, -1), (-200, 0, 0), 26, (800, 700)); shot('detail_aimants_bas.png')
look((x, -5, H - 1), (-200, 0, 0), 26, (800, 700)); shot('detail_capteur_haut.png')
print('DETAILS_V8_RENDUS')
