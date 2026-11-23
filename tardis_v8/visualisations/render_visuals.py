"""Video de montage de la V8 : un plan de camera par etape, gros plans, vues fantomes
(pieces translucides pour voir l'interieur) et etiquettes qui suivent les pieces.

    Blender --background --python tardis_v8/visualisations/render_visuals.py -- montage|test

Ecrit montage_frames/*.png et montage.json (etapes, textes, etiquettes projetees a
l'ecran pour chaque image). compose_montage.py ajoute titres, textes et etiquettes.
"""
from pathlib import Path
import bpy, bmesh, math, json, sys, colorsys
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'visualisations'
MODE = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else 'montage'
bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'tardis_v8.blend'))
scene = bpy.context.scene
for o in list(bpy.data.objects):
    if o.type in ('LIGHT', 'CAMERA'):
        bpy.data.objects.remove(o, do_unlink=True)
PP = json.loads((ROOT / 'verification.json').read_text())['parameters']
H, D = PP['opening_height'], PP['door_depth']
A = PP['opening_width'] / 2 - 5
FPS, DUR = 15, 78
RES = (1280, 720)


def smooth(t, a, b):
    v = max(0., min(1., (t - a) / (b - a)))
    return v * v * (3 - 2 * v)


def blend(a, b, k):
    return a + (b - a) * k


def srgb(x):
    return x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4


def new_mat(name, rgb, rough=.45, metal=0., lin=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    c = rgb if lin else tuple(srgb(v) for v in rgb)
    n.inputs['Base Color'].default_value = (*c, 1)
    n.inputs['Roughness'].default_value = rough; n.inputs['Metallic'].default_value = metal
    m.diffuse_color = (*c, 1)
    return m


# ---------------------------------------------------------------- objets du modele
PRODUCT = [o for o in bpy.data.objects if o.type == 'MESH' and
           (o.get('print_group') or o.get('hardware')) and not o.get('sample_only')]
for o in PRODUCT:
    o.hide_render = False
NODE = {}
for o in PRODUCT:
    # Un materiau propre a chaque objet : transparence (vue fantome) et surlignage.
    base = o.data.materials[0] if o.data.materials else new_mat('defaut', (.5, .5, .5))
    m = base.copy(); m.name = 'VID_' + o.name
    if hasattr(m, 'surface_render_method'):
        m.surface_render_method = 'DITHERED'
    if hasattr(m, 'use_transparent_shadow'):
        m.use_transparent_shadow = True
    o.data.materials.clear(); o.data.materials.append(m)
    NODE[o.name] = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    if o.get('hardware') and 'aimant' in o.name:
        NODE[o.name].inputs['Base Color'].default_value = (.32, .34, .38, 1)
        NODE[o.name].inputs['Metallic'].default_value = .8
    if o.get('hardware') and 'ILS' in o.name:
        NODE[o.name].inputs['Base Color'].default_value = (.55, .85, .95, 1)
        NODE[o.name].inputs['Roughness'].default_value = .05
BASE = {o.name: o.matrix_world.copy() for o in PRODUCT}
G = lambda o: o.get('print_group', '')


def cat(o):
    g = G(o); n = o.name
    if o.get('moving_side'):
        return 'battant'
    if g == '29_Cames_rapportees':
        return 'came'
    if n.startswith('METAL_axe') or n.startswith('METAL_clip'):
        return 'axe'
    if n.startswith('METAL_aimant_seuil') or g == '28_Cales_aimants':
        return 'aimant_seuil'
    if n.startswith('METAL_ILS'):
        return 'ils'
    if o.get('central_lock') or o.get('turnstile_screw'):
        return 'verrou'
    if g in ('08_Base_lanterne', '09_Diffuseur', '10_Cage_lanterne'):
        return 'lanterne_' + g[:2]
    if g == '26_Berceau_ESP':
        return 'esp'
    if g == '05_Tunnel':
        return 'tunnel'
    if g in ('06_Facade_arriere', '18_Base_lanterne_AR', '19_Diffuseur_AR', '20_Cage_lanterne_AR', '16_Caches_vis_AR'):
        return 'arriere'
    if g == '07_Caches_vis':
        return 'caches'
    if g == '23_Butees_TPU':
        return 'tpu'
    return 'cadre'


CAT = {o.name: cat(o) for o in PRODUCT}
BY = lambda c: [o for o in PRODUCT if CAT[o.name] == c]
FIND = lambda prefix: next(o for o in PRODUCT if o.name.startswith(prefix))


def box(name, lo, hi, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=[(a + b) / 2 for a, b in zip(lo, hi)])
    o = bpy.context.object; o.name = name; o.dimensions = [b - a for a, b in zip(lo, hi)]
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat); return o


def cyl(name, center, r, depth, axis='Y', mat=None, vertices=40):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=r, depth=depth, location=center)
    o = bpy.context.object; o.name = name
    if axis == 'Y': o.rotation_euler.x = math.pi / 2
    if axis == 'X': o.rotation_euler.y = math.pi / 2
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if mat: o.data.materials.append(mat)
    return o


def cut(a, b):
    m = a.modifiers.new('c', 'BOOLEAN'); m.operation = 'DIFFERENCE'; m.solver = 'MANIFOLD'; m.object = b
    bpy.context.view_layer.objects.active = a; bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(b, do_unlink=True); return a


# ---------------------------------------------------------------- decor et accessoires
STEEL = new_mat('VID_acier', (.66, .69, .72), .25, .85)
DOOR = new_mat('VID_porte', (.86, .84, .79), .5)
if hasattr(DOOR, 'surface_render_method'):
    DOOR.surface_render_method = 'DITHERED'
DOOR_NODE = next(n for n in DOOR.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
door = box('PORTE', (-190, 0, -40), (190, D, 330), DOOR)
cut(door, box('decoupe', (-98.1, -2, -3.1), (98.1, D + 2, 203.1), STEEL))
cut(door, box('encoche', (-18, -2, -14.1), (18, D + 2, -2), STEEL))
for s in (-1, 1):
    for z in (30, H - 24):
        cut(door, cyl('trou', (s * 107, D / 2, z), 2.5, D + 4))
floor = box('SOL', (-2000, -2000, -330), (2000, 2000, -320), new_mat('VID_sol', (.20, .22, .26), .8))
BOLTS, WASHERS, NUTS = [], [], []
for s in (-1, 1):
    for z in (30, H - 24):
        x = s * 107
        BOLTS.append(cyl('vis M4', (x, 21.5, z), 2, 70, mat=STEEL))
        BOLTS.append(cyl('tete M4', (x, -14.6, z), 3.8, 2.2, mat=STEEL))
        WASHERS.append(cyl('rondelle', (x, 49.5, z), 4, 1, mat=STEEL))
        NUTS.append(cyl('ecrou', (x, 51.6, z), 4.04, 3.2, mat=STEEL, vertices=6))
EXTRA = BOLTS + WASHERS + NUTS
# Cablage (memes cotes que generate.py) et carte ESP32.
GX, GZT, GZB = 101., H + 40, -9.
LZ = H + 61; FLOOR = -PP['tunnel_wall'] - .3 - PP['esp_box_height'] + 1.6


def wire(name, pts, rgb, r=.9):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 3
    sp = cu.splines.new('POLY'); sp.points.add(len(pts) - 1)
    for q, c in zip(sp.points, pts):
        q.co = (*c, 1)
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    m = new_mat('VID_' + name, rgb, .4)
    n = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    n.inputs['Emission Color'].default_value = (*[srgb(v) for v in rgb], 1); n.inputs['Emission Strength'].default_value = .6
    o.data.materials.append(m); return o


RX = PP['magnet_x'] + PP['reed_length']
WIRES = [wire('fil_lanterne_avant', [(0, -6, LZ + 3), (0, -1, LZ + 3), (0, -1, GZT), (GX, -1, GZT), (GX, -1, GZB),
                                     (13, -1, GZB), (13, 3, GZB), (8, 14, FLOOR + 2.6)], (1., .45, .05)),
         wire('fil_capteur', [(-RX, -1.6, H + 3), (GX - 1.2, -1.6, H + 3), (GX - 1.2, -1.6, GZB + 1.2),
                              (11, -1.6, GZB + 1.2), (11, 3, GZB + 1.2), (5, 14, FLOOR + 2.6)], (.15, .8, .3), .6),
         wire('fil_lanterne_arriere', [(0, D + 6, LZ + 3), (0, D + 1, LZ + 3), (0, D + 1, GZT), (-GX, D + 1, GZT),
                                       (-GX, D + 1, GZB), (-13, D + 1, GZB), (-13, D - 3, GZB), (-8, 16, FLOOR + 2.6)],
              (.9, .12, .1))]
PCB = new_mat('VID_pcb', (.08, .42, .2), .5)
ESPB = [box('carte ESP32-C3', (-9, 17, FLOOR + 1), (9, 37, FLOOR + 2.6), PCB),
        box('prise USB-C', (-4.5, 30.3, FLOOR + 2.6), (4.5, 38, FLOOR + 5.8), STEEL)]
for o in EXTRA + ESPB + WIRES + [door]:
    BASE[o.name] = o.matrix_world.copy()

# ---------------------------------------------------------------- lumiere, monde, camera
world = scene.world; world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs[0].default_value = (.055, .07, .095, 1); bg.inputs[1].default_value = 1.


def area(loc, target, power, size, color=(1, 1, 1)):
    bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object
    l.data.energy = power; l.data.size = size; l.data.color = color
    l.rotation_euler = (Vector(target) - l.location).to_track_quat('-Z', 'Y').to_euler()
    return l


area((-600, -900, 700), (0, 0, 120), 9e6, 700, (1, .96, .9))          # cle, chaude
area((800, -500, 300), (0, 0, 120), 4e6, 600, (.85, .9, 1))           # remplissage, froide
area((0, 900, 800), (0, 0, 120), 6e6, 700, (.9, .95, 1))              # contre-jour
area((0, -400, -250), (0, 0, 0), 1.5e6, 500)                          # debouchage bas
bpy.ops.object.camera_add(); cam = bpy.context.object; scene.camera = cam
cam.data.lens = 50; cam.data.clip_start = 1; cam.data.clip_end = 20000
scene.render.engine = 'BLENDER_EEVEE'
ee = scene.eevee
for attr, val in (('taa_render_samples', 32), ('use_shadows', True), ('use_raytracing', True)):
    if hasattr(ee, attr):
        try: setattr(ee, attr, val)
        except Exception: pass
scene.view_settings.view_transform = 'AgX'
try: scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
scene.render.resolution_x, scene.render.resolution_y = RES; scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGB'

# Lanternes : diffuseurs emissifs et lampes ponctuelles.
GLOW = {o.name: NODE[o.name] for o in PRODUCT if G(o) in ('09_Diffuseur', '19_Diffuseur_AR')}
LAMPS = {}
for o in PRODUCT:
    if o.name in GLOW:
        bpy.ops.object.light_add(type='POINT', location=o.matrix_world @ (sum((Vector(v) for v in o.bound_box), Vector()) / 8))
        LAMPS[o.name] = bpy.context.object; LAMPS[o.name].data.energy = 0; LAMPS[o.name].data.shadow_soft_size = 4


def glow(t, level, flash=False):
    for name, n in GLOW.items():
        rear = 'arriere' in name
        hue = (t * .3 + (.5 if rear else 0)) % 1
        rgb = colorsys.hsv_to_rgb(hue, 1, 1)
        on = 1. if not rear else (1. if int(t * 4) % 2 == 0 else .2)
        if flash:
            rgb, on, level = (1., 1., 1.), (1. if int(t * 8) % 2 == 0 else .15), 1.
        n.inputs['Emission Color'].default_value = (*rgb, 1)
        n.inputs['Emission Strength'].default_value = 2.2 * level * on
        ivory = (.91, .79, .58)
        n.inputs['Base Color'].default_value = (*[blend(i, c * .6, level) for i, c in zip(ivory, rgb)], 1)
        LAMPS[name].data.color = rgb; LAMPS[name].data.energy = 260 * level * on


# ---------------------------------------------------------------- scenario
# Chaque etape : debut, fin, titre, texte, plan de camera (cible, azimut, hauteur,
# distance), vue fantome (categories translucides), surlignage, etiquettes.
def P(*v): return Vector(v)


SCENES = [
    dict(t=0, title='TARDIS Geronimeow', text='Une chatière TARDIS double action à imprimer en 3D : rappel par gravité, verrou central, capteur et lanternes RGB.',
         cam=(P(0, 20, 135), 28, 14, 1050), intro=True),
    dict(t=5, title='Les pièces', text='Façade avant, battants, cames, verrou, aimants, capteur, électronique, tunnel et façade arrière.',
         cam=(P(0, 20, 110), 35, 22, 1500)),
    dict(t=8.5, title='Les cames réglables', text='Chaque came s’emboîte sur la clé en D du nœud de charnière. Trois pentes (3,5 · 4,5 · 5,5 mm) règlent la force de rappel.',
         cam=(P(-A, -5, 42), 38, 24, 120), hl=['came'],
         labels=[('cle', 'Clé en D : une seule position'), ('came', 'Came 4,5 mm (2 rainures)')]),
    dict(t=14, title='Les battants et leurs axes', text='Chaque battant se pose sur sa came ; les axes acier Ø3 montent par le bas et sont tenus par des clips.',
         cam=(P(0, -10, 105), 28, 14, 760), hl=['axe'],
         labels=[('axe', 'Axe Ø3 × 39,4 mm'), ('battant', 'Battant : deux demi-coques collées')]),
    dict(t=19, title='Aimants anti-vent', text='Un aimant sous le battant, un dans le seuil, posé sur des cales de 1 mm : plus de cales, maintien plus fort.',
         cam=(P(PP['magnet_x'], -5, -1), 62, 12, 105), ghost=['cadre', 'battant'], hl=['aimant_seuil', 'aimant_bat'],
         labels=[('aimant_bat', 'Aimant Ø6 × 2 du battant'), ('aimant_seuil', 'Aimant du seuil'), ('cale', 'Cale de 1 mm (réglage)')]),
    dict(t=24.5, title='Capteur de passage', text='Un aimant en haut du battant ferme un ILS caché dans le linteau. Le battant s’ouvre : le contact s’ouvre, le passage est compté.',
         cam=(P(PP['magnet_x'] + 7, -5, H - 2), 62, 10, 120), ghost=['cadre', 'battant'], hl=['ils', 'aimant_cap'],
         labels=[('ils', 'ILS (ampoule de verre) dans le linteau'), ('aimant_cap', 'Aimant Ø6 × 3 du battant')]),
    dict(t=30, title='Les lanternes', text='Socle, diffuseur ivoire, cage-chapeau : une LED RGB WS2812B se loge dans le socle.',
         cam=(P(0, -10, 278), 32, 20, 210)),
    dict(t=34, title='Câbles dans les façades', text='Au dos de la façade, une rainure invisible mène les câbles de la lanterne et du capteur jusque sous le tunnel.',
         cam=(P(0, 0, 105), 205, 12, 800), hl=['fils'],
         labels=[('fil_l', 'Câble de la lanterne'), ('fil_c', 'Câble du capteur')]),
    dict(t=36.6, title='Berceau de l’ESP32', text='L’ESP32 se cache sous le tunnel, dans une encoche de la porte ; la prise USB-C est côté maison.',
         cam=(P(0, 22, -6), 215, 34, 150), hl=['esp'],
         labels=[('esp', 'Berceau ESP32'), ('usb', 'Prise USB-C (côté maison)'), ('fil_l', 'Câbles des façades')]),
    dict(t=39.5, title='Tunnel, porte et façade arrière', text='Le tunnel traverse la porte découpée au gabarit ; la façade arrière vient en face.',
         cam=(P(0, 20, 110), 40, 20, 1150)),
    dict(t=45, title='Vis, caches et butées', text='Quatre vis M4 traversantes, huit caches, et quatre butées TPU qui amortissent les battants à 85°.',
         cam=(P(0, 20, 110), 25, 16, 1050)),
    dict(t=49, title='Verrou central : FERMÉ', text='On monte le bouton et on tourne le tourniquet dessous : la lame entre dans les deux battants, ils sont bloqués.',
         cam=(P(3, -18, -2), 12, 8, 135), ghost=['cadre', 'battant'], hl=['verrou'],
         labels=[('bouton', 'Bouton'), ('tourniquet', 'Tourniquet'), ('lame', 'Lame dans les deux battants')]),
    dict(t=54.3, title='Verrou central : LIBRE', text='Tourniquet relevé, la lame retombe sous le seuil : rien ne dépasse, les battants sont libres.',
         cam=(P(3, -18, -2), 12, 8, 135), ghost=['cadre', 'battant'], hl=['verrou'],
         labels=[('lame', 'Lame sous le seuil'), ('tourniquet', 'Tourniquet relevé')]),
    dict(t=57, title='Passage détecté', text='Le chat pousse le battant : l’ILS s’ouvre, l’ESP compte le passage et fait flasher les lanternes.',
         cam=(P(0, 10, 115), 32, 14, 820),
         labels=[('linteau', 'ILS : passage compté')]),
    dict(t=64, title='Retour par gravité', text='En s’ouvrant, le battant monte sur sa came (3 mm à 60°) ; lâché, son poids le ramène au centre.',
         cam=(P(A, -5, 50), 28, 16, 150), ghost=['cadre'], hl=['came'],
         labels=[('came_d', 'La dent monte sur la rampe')]),
    dict(t=69, title='Éclairage RGB', text='Les lanternes se pilotent depuis le téléphone (ESPHome ou WLED) : couleurs, gyrophare, minuterie.',
         cam=(P(0, 15, 190), 30, 14, 720), outro=True),
]
for i, s in enumerate(SCENES):
    s['end'] = SCENES[i + 1]['t'] if i + 1 < len(SCENES) else DUR
STEPS = [s for s in SCENES if not s.get('intro')]


def scene_at(t):
    return max((s for s in SCENES if s['t'] <= t), key=lambda s: s['t'])


def camera_at(t):
    # Interpolation douce entre plans (0,9 s), legere derive pendant chaque plan.
    cur = scene_at(t); i = SCENES.index(cur)
    tgt, az, el, dist = cur['cam']
    drift = (t - cur['t']) * (6 if cur.get('intro') or cur.get('outro') else 1.2)
    if cur.get('outro'):
        drift = -min(t - cur['t'], 6) * 18
    if i > 0:
        prev = SCENES[i - 1]; pt, pa, pe, pd = prev['cam']
        pdrift = (cur['t'] - prev['t']) * (6 if prev.get('intro') else 1.2)
        k = smooth(t, cur['t'], cur['t'] + .9)
        tgt = pt.lerp(tgt, k); az = blend(pa + pdrift, az, k); el = blend(pe, el, k)
        dist = math.exp(blend(math.log(pd), math.log(dist), k))
        drift *= k
    a, e = math.radians(az + drift), math.radians(el)
    loc = tgt + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.location = loc
    cam.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()


# Arrivee de chaque categorie apres l'eclatement : vecteur d'eclatement et fenetre.
ARRIVE = {
    'came': ((0, 0, 70), 9.2, 10.6), 'battant': (None, 14.3, 16.1), 'axe': ((0, 0, -90), 16.3, 17.6),
    'verrou': ((0, -70, 0), 17.6, 18.6), 'aimant_seuil': ((0, 0, 45), 19.8, 21.2), 'ils': ((0, 45, 0), 25.2, 26.6),
    'lanterne_08': ((0, 0, 85), 30.3, 31.1), 'lanterne_09': ((0, 0, 120), 31.1, 31.9), 'lanterne_10': ((0, 0, 165), 31.9, 33),
    'esp': ((0, 0, -80), 37.2, 38.4), 'tunnel': ((300, 260, 0), 39.8, 41), 'arriere': ((-320, 260, 0), 42.6, 44),
    'caches': ((0, -110, 0), 47, 48), 'tpu': ((0, -100, 0), 48, 49), 'cadre': ((0, 0, 0), 0, 1),
}
EXPLODE = (5., 8.4)


def arrive(c, t):
    vec, a0, a1 = ARRIVE[c]
    return smooth(t, *EXPLODE) * (1 - smooth(t, a0, a1)), vec


def leaf_angles(t):
    ang = {-1: 0., 1: 0.}
    # Tentative de poussee bloquee par le verrou (petit choc), puis passages et gravite.
    if 52.4 <= t < 53.6:
        ang[1] = math.radians(.6) * math.sin((t - 52.4) * math.pi / .3) * (1 - smooth(t, 53.2, 53.6))
    if 57.5 <= t < 60.5:
        ang[1] = math.radians(62) * (smooth(t, 57.5, 58.8) - smooth(t, 59.2, 60.5))
        ang[-1] = math.radians(58) * (smooth(t, 57.7, 59) - smooth(t, 59.4, 60.6))
    if 61 <= t < 64:
        ang[1] = -math.radians(58) * (smooth(t, 61, 62.3) - smooth(t, 62.7, 64))
        ang[-1] = -math.radians(55) * (smooth(t, 61.2, 62.5) - smooth(t, 62.9, 64))
    if 64.5 <= t < 68.8:
        ang[1] = math.radians(60) * (smooth(t, 64.5, 66.3) - smooth(t, 67, 68.8))
    return ang


def lock_state(t):
    # Lame et bouton : montent (49,6-50,6), redescendent (55-55,8). Tourniquet : 50,8-51,6 / 54,4-55.
    up = 5.5 * (smooth(t, 49.6, 50.6) - smooth(t, 55, 55.8)) + .8 * (smooth(t, 54.3, 54.6) - smooth(t, 54.9, 55.1))
    rot = -90 * (smooth(t, 50.8, 51.6) - smooth(t, 54.5, 55))
    return up, rot


def pose(t):
    ang = leaf_angles(t)
    lift = lambda a: PP['cam_rise'] * abs(a) / (math.pi / 2)
    up, rot = lock_state(t)
    for o in PRODUCT:
        c = CAT[o.name]
        if c == 'battant':
            s = o['moving_side']; k = smooth(t, *EXPLODE) * (1 - smooth(t, 14.3, 16.1))
            off = Vector((s * 200 * k, -70 * k, lift(ang[s])))
            p = Vector((s * A, -5, 0))
            m = Matrix.Translation(p) @ Matrix.Rotation(s * ang[s], 4, 'Z') @ Matrix.Translation(-p)
            o.matrix_world = Matrix.Translation(off) @ m @ BASE[o.name]
            continue
        k, vec = arrive(c, t)
        off = Vector(vec) * k if vec else Vector()
        if c == 'verrou':
            if o.get('turnstile_pivot'):
                pv = Vector(o['turnstile_pivot'])
                o.matrix_world = Matrix.Translation(off) @ Matrix.Translation(pv) @ Matrix.Rotation(math.radians(rot), 4, 'Y') @ Matrix.Translation(-pv) @ BASE[o.name]
                continue
            if not o.get('turnstile_screw'):
                off = off + Vector((0, 0, up))
        o.matrix_world = Matrix.Translation(off) @ BASE[o.name]
    # Porte, visserie, ESP, cables.
    kd = smooth(t, *EXPLODE) * (1 - smooth(t, 41, 42.3))
    door.matrix_world = Matrix.Translation((0, 520 * kd, 0)) @ BASE[door.name]
    for objs, a0, a1, dy in ((BOLTS, 45, 46, -170), (WASHERS, 46, 46.6, 130), (NUTS, 46.6, 47.2, 150)):
        k = smooth(t, *EXPLODE) * (1 - smooth(t, a0, a1))
        for o in objs:
            o.matrix_world = Matrix.Translation((0, dy * k, 0)) @ BASE[o.name]
    k, vec = arrive('esp', t)
    for o in ESPB:
        o.matrix_world = Matrix.Translation(Vector(vec) * k) @ BASE[o.name]
    ka, veca = arrive('arriere', t)
    for w in WIRES:
        w.hide_render = 5 <= t < 34.2
        if 'arriere' in w.name:
            w.matrix_world = Matrix.Translation(Vector(veca) * ka) @ BASE[w.name]
    sc = scene_at(t)
    # Vue fantome et surlignage, en fondu sur 0,5 s.
    fade = smooth(t, sc['t'], sc['t'] + .5) * (1 - smooth(t, sc['end'] - .4, sc['end']))
    ghost = sc.get('ghost', []); hl = sc.get('hl', [])
    for o in PRODUCT:
        n = NODE[o.name]; c = CAT[o.name]
        g = (c in ghost) or (c == 'tunnel' and ghost) or (c == 'arriere' and ghost)
        n.inputs['Alpha'].default_value = 1 - .78 * fade if g else 1.
        name = o.name
        tag = {'came': 'came', 'axe': 'axe', 'aimant_seuil': 'aimant_seuil', 'ils': 'ils', 'verrou': 'verrou', 'esp': 'esp'}.get(c)
        if c == 'battant' and 'aimant_battant' in name: tag = 'aimant_bat'
        if c == 'battant' and 'aimant_capteur' in name: tag = 'aimant_cap'
        if o.name not in GLOW:
            on = tag in hl
            n.inputs['Emission Color'].default_value = (1., .55, .1, 1)
            n.inputs['Emission Strength'].default_value = (.55 * fade) if on else 0.
    DOOR_NODE.inputs['Alpha'].default_value = 1 - .78 * fade if ghost else 1.
    # Lanternes : allumees a l'intro et a la fin, flash pendant les passages.
    flash = 57 <= t < 64 and max(abs(a) for a in leaf_angles(t).values()) > math.radians(8)
    level = 1 - smooth(t, 4.2, 5) if t < 6 else smooth(t, 69, 70)
    glow(t, level, flash)
    camera_at(t)


# ---------------------------------------------------------------- etiquettes a l'ecran
def center(o):
    return o.matrix_world @ (sum((Vector(v) for v in o.bound_box), Vector()) / 8)


ANCHORS = {
    'cle': lambda: Vector((-A + 1.5, -5 - 2.4, 38.8)),
    'came': lambda: center(next(o for o in BY('came') if o.name.endswith('gauche'))),
    'axe': lambda: center(next(o for o in BY('axe') if 'gauche_bas' in o.name and o.name.startswith('METAL_axe'))) + Vector((0, 0, -12)),
    'battant': lambda: center(next(o for o in PRODUCT if o.name == 'battant_droit_avant')) + Vector((20, 0, 40)),
    'aimant_bat': lambda: center(FIND('METAL_aimant_battant_droite')),
    'aimant_seuil': lambda: center(FIND('METAL_aimant_seuil_droite')),
    'cale': lambda: center(next(o for o in BY('aimant_seuil') if o.name.startswith('cale') and 'droite' in o.name)),
    'ils': lambda: center(FIND('METAL_ILS_droite')),
    'aimant_cap': lambda: center(FIND('METAL_aimant_capteur_droite')),
    'fil_l': lambda: WIRES[0].matrix_world @ Vector((GX, -1, 120)),
    'fil_c': lambda: WIRES[1].matrix_world @ Vector((40, -1.6, H + 3)),
    'esp': lambda: center(BY('esp')[0]) + Vector((-12, 0, 0)),
    'usb': lambda: center(ESPB[1]),
    'bouton': lambda: center(FIND('bouton_verrou')),
    'tourniquet': lambda: center(FIND('tourniquet')),
    'lame': lambda: center(FIND('lame_verrou')) + Vector((0, 0, 4)),
    'linteau': lambda: Vector((30, -10, H + 4)),
    'came_d': lambda: center(next(o for o in BY('came') if o.name.endswith('droite'))) + Vector((0, 0, 3)),
}


def project(p):
    v = world_to_camera_view(scene, cam, p)
    return [round(v.x * RES[0], 1), round((1 - v.y) * RES[1], 1), v.z > 0 and 0 <= v.x <= 1 and 0 <= v.y <= 1]


frames = OUT / 'montage_frames'; frames.mkdir(exist_ok=True)
total = int(DUR * FPS)
indices = [int(x * FPS) for x in (2, 10.5, 16.5, 22, 27.5, 32.5, 35.5, 38.5, 43, 52, 56, 59, 66, 74)] if MODE == 'test' else range(total)
per_frame = {}
for i in indices:
    t = i / FPS
    scene.frame_set(1)
    pose(t)
    bpy.context.view_layer.update()
    sc = scene_at(t)
    per_frame[i] = [dict(key=k, label=lab, xy=project(ANCHORS[k]())) for k, lab in sc.get('labels', [])]
    scene.render.filepath = str(frames / f'{i:04d}.png')
    bpy.ops.render.render(write_still=True)
    print('MONTAGE_FRAME', i, flush=True)

manifest = dict(fps=FPS, duration_seconds=DUR, frames=total, width=RES[0], height=RES[1],
                scenes=[dict(t=s['t'], end=s['end'], title=s['title'], text=s['text'],
                             step=(STEPS.index(s) + 1 if s in STEPS else 0), steps=len(STEPS),
                             intro=bool(s.get('intro')), outro=bool(s.get('outro'))) for s in SCENES],
                labels={str(k): v for k, v in per_frame.items()},
                note='Animation illustrative : frottements, force des aimants, collage et electronique non simules.')
(OUT / ('montage_test.json' if MODE == 'test' else 'montage.json')).write_text(json.dumps(manifest, ensure_ascii=False))
print('VISUELS_TERMINE', MODE, flush=True)
