"""Vignettes couleur des plateaux (projets Creality Print) pour la documentation.

    /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/vignettes_plateaux.py -- tardis_v8

Chaque plateau est rendu sur le plateau K1 Max (300 x 300 mm) avec les couleurs des
emplacements CFS, la tour de purge a sa position (gris) et les volumes de support
(vert translucide). Sortie : <version>/images/plateaux/<plateau>.jpg.
La planche d'ensemble est faite ensuite par scripts/planche_plateaux.py.
"""
import bpy, glob, json, math, os, re, sys, zipfile
import xml.etree.ElementTree as ET
from mathutils import Matrix, Vector

CORE = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
PROD = '{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'


def matrix(s):
    if not s:
        return Matrix.Identity(4)
    v = [float(x) for x in s.split()]
    return Matrix(((v[0], v[3], v[6], v[9]), (v[1], v[4], v[7], v[10]), (v[2], v[5], v[8], v[11]), (0, 0, 0, 1)))


def read_plate(path):
    """Renvoie [(nom, sous-type, emplacement, sommets, triangles)] et les reglages du projet."""
    z = zipfile.ZipFile(path); trees = {}
    tree = lambda f: trees.setdefault(f, ET.fromstring(z.read(f)))
    settings = json.loads(z.read('Metadata/project_settings.config'))
    config = ET.fromstring(z.read('Metadata/model_settings.config'))
    parts_of = {}
    for o in config.iter('object'):
        meta = {m.get('key'): m.get('value') for m in o.findall('metadata')}
        parts_of[o.get('id')] = [(p.get('subtype'), {m.get('key'): m.get('value') for m in p.findall('metadata')},
                                  meta.get('extruder', '1')) for p in o.iter('part')]

    def meshes(f, oid, M):
        for o in tree(f).iter(CORE + 'object'):
            if o.get('id') != oid:
                continue
            m = o.find(CORE + 'mesh')
            if m is not None:
                vs = [M @ Vector((float(v.get('x')), float(v.get('y')), float(v.get('z')))) for v in m.iter(CORE + 'vertex')]
                ts = [(int(t.get('v1')), int(t.get('v2')), int(t.get('v3'))) for t in m.iter(CORE + 'triangle')]
                yield vs, ts
            else:
                for c in o.find(CORE + 'components'):
                    yield from meshes((c.get(PROD + 'path') or '/' + f).lstrip('/'), c.get('objectid'), M @ matrix(c.get('transform')))

    root = tree('3D/3dmodel.model'); out = []
    for item in root.find(CORE + 'build'):
        oid = item.get('objectid'); parts = parts_of.get(oid, [])
        for k, (vs, ts) in enumerate(meshes('3D/3dmodel.model', oid, matrix(item.get('transform')))):
            subtype, meta, default = parts[k] if k < len(parts) else ('normal_part', {}, '1')
            out.append((meta.get('name', oid), subtype, int(meta.get('extruder', default)), vs, ts))
    return out, settings


def material(name, rgba, alpha=1.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = rgba
    b.inputs['Roughness'].default_value = 0.55
    b.inputs['Alpha'].default_value = alpha
    if alpha < 1:
        m.surface_render_method = 'BLENDED'
    return m


def hex_rgba(h):
    h = h.lstrip('#')
    return tuple(((int(h[i:i + 2], 16) / 255) ** 2.2) for i in (0, 2, 4)) + (1.0,)


def add_mesh(name, vs, ts, mat):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in vs], [], ts); me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


def add_box(name, lo, hi, mat):
    vs = [Vector((x, y, z)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
    ts = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1), (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    return add_mesh(name, vs, ts, mat)


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x, scene.render.resolution_y = 900, 675
    scene.render.image_settings.file_format = 'JPEG'; scene.render.image_settings.quality = 88
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    world = bpy.data.worlds.new('fond'); scene.world = world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.93, 0.92, 0.89, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.9
    sun = bpy.data.objects.new('soleil', bpy.data.lights.new('soleil', 'SUN'))
    sun.data.energy = 3.2; sun.rotation_euler = (math.radians(40), math.radians(-15), math.radians(25))
    scene.collection.objects.link(sun)
    cam = bpy.data.objects.new('camera', bpy.data.cameras.new('camera'))
    cam.data.lens = 46; scene.collection.objects.link(cam); scene.camera = cam
    cam.location = (150, -235, 365)
    cam.rotation_euler = (Vector((150, 128, 0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    # Plateau K1 Max 300 x 300, quadrille tous les 50 mm.
    add_box('plateau', (0, 0, -3), (300, 300, 0), material('plateau', (0.06, 0.065, 0.075, 1)))
    grid = material('quadrillage', (0.16, 0.17, 0.19, 1))
    for i in range(1, 6):
        add_box('ligne', (i * 50 - 0.4, 0, -0.05), (i * 50 + 0.4, 300, 0.01), grid)
        add_box('ligne', (0, i * 50 - 0.4, -0.05), (300, i * 50 + 0.4, 0.01), grid)


def render(path, out):
    setup_scene()
    parts, settings = read_plate(path)
    colours = [hex_rgba(c) for c in settings['filament_colour']]
    mats = [material(f'emplacement{i + 1}', c) for i, c in enumerate(colours)]
    support = material('support', (0.15, 0.85, 0.3, 1), alpha=0.45)
    used = set()
    for name, subtype, slot, vs, ts in parts:
        if subtype == 'support_enforcer':
            add_mesh(name, vs, ts, support)
        elif subtype == 'normal_part':
            add_mesh(name, vs, ts, mats[slot - 1]); used.add(slot)
    if len(used) > 1 and settings.get('enable_prime_tower', '1') == '1':
        x, y = float(settings['wipe_tower_x'][0]), float(settings['wipe_tower_y'][0])
        w = float(settings.get('prime_tower_width', 35))
        add_box('tour de purge', (x, y, 0), (x + w, y + 28, 12), material('tour', (0.2, 0.21, 0.23, 1)))
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)


args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
for version in args:
    os.makedirs(f'{version}/images/plateaux', exist_ok=True)
    for src in sorted(glob.glob(f'{version}/3mf/*.3mf')):
        render(os.path.abspath(src), os.path.abspath(f'{version}/images/plateaux/{os.path.basename(src)[:-4]}.jpg'))
        print('vignette :', src, flush=True)
