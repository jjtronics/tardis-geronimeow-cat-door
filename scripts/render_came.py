"""Rendu explicatif de la came de rappel par gravite (charniere basse gauche).

    /Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_came.py -- tardis_v8

Isole la charniere basse (noeud et came du cadre en bleu, came et noeud du battant
en ivoire, axe et clips acier), puis la rend ferme et ouvert a 60 degres, battant
souleve par la came. Ecrit <version>/images/came_rappel_ferme.png et _ouvert.png ;
la composition legendee est faite par scripts/planche_came.py.
"""
from pathlib import Path
import bpy, json, math, sys
from mathutils import Matrix, Vector

version = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
blend = next(version.glob('tardis_*.blend'))
bpy.ops.wm.open_mainfile(filepath=str(blend))
P = json.loads((version / 'verification.json').read_text())['parameters']
A = P['opening_width'] / 2 - 5; s = -1; pivot = Vector((s * A, -5, 0))
scene = bpy.context.scene


def mat(name, rgb, metal=0., rough=.45):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value = (*rgb, 1); n.inputs['Metallic'].default_value = metal
    n.inputs['Roughness'].default_value = rough
    return m

BLUE, IVORY, STEEL = mat('cadre', (.02, .07, .16)), mat('battant', (.86, .78, .6)), mat('acier', (.6, .63, .66), .85, .25)

# Volume de travail : les noeuds et les cames seuls (rayon 4,5 mm autour de l'axe).
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=4.5, depth=36, location=(s * A, -5, 46))
zone = bpy.context.object
keep = []
for o in list(bpy.data.objects):
    if o.type != 'MESH' or o == zone:
        continue
    fixed_frame = ((o.get('print_group') == '01_Cadre' and o.name.startswith('cadre'))
                   or (o.get('print_group') == '29_Cames_rapportees' and not o.get('sample_only')))
    leaf = o.get('moving_side') == s and o.name.startswith('battant')
    metal = o.get('hardware') and ('gauche_bas' in o.name)
    if not (fixed_frame or leaf or metal):
        o.hide_render = True; continue
    if not metal:
        mod = o.modifiers.new('zone', 'BOOLEAN'); mod.operation = 'INTERSECT'; mod.object = zone; mod.solver = 'EXACT'
        bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=mod.name)
    o.data.materials.clear(); o.data.materials.append(STEEL if metal else IVORY if leaf else BLUE)
    o.hide_render = False; keep.append((o, leaf))
zone.hide_render = True
base = {o.name: o.matrix_world.copy() for o, _ in keep}

for o in list(bpy.data.objects):
    if o.type == 'LIGHT':
        bpy.data.objects.remove(o, do_unlink=True)
for loc, power in (((-160, -120, 140), 90000), ((60, -90, 60), 40000), ((-90, 120, 90), 50000)):
    bpy.ops.object.light_add(type='AREA', location=loc); l = bpy.context.object
    l.data.energy = power; l.data.size = 80
    l.rotation_euler = (Vector((s * A, -5, 44)) - l.location).to_track_quat('-Z', 'Y').to_euler()
world = scene.world; world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
bg.inputs[0].default_value = (.93, .92, .89, 1); bg.inputs[1].default_value = .6
cam = scene.camera
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 40
cam.location = Vector((s * A, -5, 44)) + Vector((-60, -100, 28))
cam.rotation_euler = (Vector((s * A, -5, 45)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x, scene.render.resolution_y = 560, 760
scene.render.film_transparent = False

out = version / 'images'; out.mkdir(exist_ok=True)
for label, deg in (('ferme', 0), ('ouvert', 60)):
    lift = P['cam_rise'] * deg / 90
    rot = Matrix.Translation((0, 0, lift)) @ Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(s * deg), 4, 'Z') @ Matrix.Translation(-pivot)
    for o, leaf in keep:
        o.matrix_world = (rot @ base[o.name]) if leaf else base[o.name]
    scene.render.filepath = str(out / f'came_rappel_{label}.png')
    bpy.ops.render.render(write_still=True)
print('CAME_RENDUE', version.name)
