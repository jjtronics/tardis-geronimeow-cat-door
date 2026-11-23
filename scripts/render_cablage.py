"""Figures du cablage de l'eclairage RGB (V7 Lite).

    /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_cablage.py -- tardis_v8

1. cablage_dos_facade.png : dos de la facade avant vu depuis la porte, rainure et
   cable (orange) de la lanterne jusqu'au berceau de l'ESP sous le tunnel.
2. cablage_berceau.png : gros plan du berceau, carte ESP32-C3, fils des deux
   lanternes et fiche USB-C cote interieur (tunnel et facade arriere masques).
La planche legendee est faite par scripts/planche_cablage.py.
"""
from pathlib import Path
import bpy, json, sys
from mathutils import Vector

version = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(next(version.glob('tardis_*.blend'))))
P = json.loads((version / 'verification.json').read_text())['parameters']
H, D = P['opening_height'], P['door_depth']
scene = bpy.context.scene
LZ = H + 61; V8 = 'cam_rises' in P
GX, GZT, GZB = (101., H + 40, -9.) if V8 else (101., H + 6, -7.)
ESP_TOP = -P['tunnel_wall'] - .3; FLOOR = ESP_TOP - P['esp_box_height'] + 1.6


def mat(name, rgb, metal=0., rough=.5, emit=0.):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value = (*rgb, 1); n.inputs['Metallic'].default_value = metal
    n.inputs['Roughness'].default_value = rough
    if emit:
        n.inputs['Emission Color'].default_value = (*rgb, 1); n.inputs['Emission Strength'].default_value = emit
    return m

ORANGE, RED = mat('fil', (1., .35, .02), emit=.6), mat('fil rouge', (.85, .05, .05), emit=.4)
PCB, STEEL, BLACK = mat('pcb', (.02, .18, .08)), mat('usb', (.7, .72, .75), .9, .25), mat('noir', (.02, .02, .02))


def wire(name, pts, m, r=.9):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 4
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts):
        p.co = (*c, 1)
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    o.data.materials.append(m); return o


def cube(name, lo, hi, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=[(a + b) / 2 for a, b in zip(lo, hi)])
    o = bpy.context.object; o.name = name; o.dimensions = [b - a for a, b in zip(lo, hi)]
    o.data.materials.append(m); return o


keep_front = ('cadre_monobloc_moulure', 'base_lanterne', 'berceau_ESP', 'tunnel_exterieur', 'filet_recentreur_ivoire',
              'METAL_ILS_gauche', 'METAL_ILS_droite')
# Fil avant : lanterne -> rainure -> berceau ; fil arriere : symetrique (x<0, y=D).
yf, yr = -1., D + 1.
front = [(0, -6, LZ + 3), (0, yf, LZ + 3), (0, yf, GZT), (GX, yf, GZT), (GX, yf, GZB), (13, yf, GZB),
         (13, 3, GZB), (8, 14, FLOOR + 2.6)]
rear = [(0, D + 6, LZ + 3), (0, yr, LZ + 3), (0, yr, GZT), (-GX, yr, GZT), (-GX, yr, GZB), (-13, yr, GZB),
        (-13, D - 3, GZB), (-8, 16, FLOOR + 2.6)]
wires = [wire('fil lanterne avant', front, ORANGE), wire('fil lanterne arriere', rear, RED)]
GREEN = mat('fil capteur', (.1, .7, .25), emit=.5)
if V8:
    # Boucle des deux ILS (V8) : sous le linteau, puis avec le cable avant.
    rx = P['magnet_x'] + P['reed_length']
    wires.append(wire('fil capteur', [(-rx, -1.6, H + 3), (GX - 1.2, -1.6, H + 3), (GX - 1.2, -1.6, GZB + 1.2),
                                     (11, -1.6, GZB + 1.2), (11, 3, GZB + 1.2), (5, 14, FLOOR + 2.6)], GREEN, .6))
board = cube('carte ESP32-C3', (-9, 17, FLOOR + 1), (9, 39.4 - 1.6 - .8, FLOOR + 2.6), PCB)
usb = cube('prise USB-C', (-4.5, 39.4 - 1.6 - 7.5, FLOOR + 2.6), (4.5, 39.4 - 1.6 + .2, FLOOR + 5.8), STEEL)
plug = cube('fiche USB-C', (-4.1, D - 1.4, FLOOR + 2.8), (4.1, D + 12, FLOOR + 5.6), STEEL)
boot = cube('cable USB', (-6, D + 12, FLOOR + 1.2), (6, D + 40, FLOOR + 7.2), BLACK)
extras = wires + [board, usb, plug, boot]

for o in list(bpy.data.objects):
    if o.type == 'LIGHT':
        bpy.data.objects.remove(o, do_unlink=True)
world = scene.world; world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs[0].default_value = (.93, .92, .89, 1); bg.inputs[1].default_value = 1.
for loc, power in (((150, 500, 300), 900000), ((-250, 300, -100), 400000), ((0, -300, 200), 300000)):
    bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object
    l.data.energy = power; l.data.size = 300
    l.rotation_euler = (Vector((0, 20, 100)) - l.location).to_track_quat('-Z', 'Y').to_euler()
cam = scene.camera
scene.render.engine = 'BLENDER_EEVEE'; scene.render.film_transparent = False
out = version / 'images'; out.mkdir(exist_ok=True)


def show(names, extra):
    for o in bpy.data.objects:
        if o.type in ('MESH', 'CURVE'):
            o.hide_render = not (o.name in names or o in extra)


# 1. Dos de la facade avant, vu depuis la porte (orthographique).
show(keep_front, [w for w in wires if w is not wires[1]])
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 300
cam.location = (0, 600, 125); cam.rotation_euler = (Vector((0, 0, 125)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.resolution_x, scene.render.resolution_y = 900, 1050
scene.render.filepath = str(out / 'cablage_dos_facade.png'); bpy.ops.render.render(write_still=True)

# 2. Gros plan du berceau sous le tunnel, tunnel et facade arriere masques.
show(('cadre_monobloc_moulure', 'berceau_ESP'), extras)
cam.data.type = 'PERSP'; cam.data.lens = 50
target = Vector((0, 22, -8))
cam.location = target + Vector((-80, 120, 95))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.resolution_x, scene.render.resolution_y = 1000, 760
scene.render.filepath = str(out / 'cablage_berceau.png'); bpy.ops.render.render(write_still=True)
print('CABLAGE_RENDU', version.name)
