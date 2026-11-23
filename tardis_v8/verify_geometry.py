"""V8 : débattement avec levée de la came (trois pentes), butées, verrou central,
aimants, capteur de passage et interférences."""
from pathlib import Path
import bpy,bmesh,json,math,itertools
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'tardis_v8.blend'))
printed=[o for o in bpy.data.objects if o.get('print_group') and not o.get('sample_only')]
hardware=[o for o in bpy.data.objects if o.get('hardware')]
params=json.loads((ROOT/'verification.json').read_text())['parameters']

def aabb(o):
    ps=[o.matrix_world@Vector(v) for v in o.bound_box]
    return [min(p[i] for p in ps) for i in range(3)],[max(p[i] for p in ps) for i in range(3)]

def intersect(a,b):
    al,ah=aabb(a);bl,bh=aabb(b)
    if any(min(ah[k],bh[k])-max(al[k],bl[k])<.0001 for k in range(3)):return 0.
    probe=a.copy();probe.data=a.data.copy();bpy.context.collection.objects.link(probe)
    bpy.context.view_layer.objects.active=probe
    mod=probe.modifiers.new('intersection verification','BOOLEAN')
    mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(probe.data);volume=abs(bm.calc_volume());bm.free()
    bpy.data.objects.remove(probe,do_unlink=True)
    return volume

def threaded(a,b):
    # La vis M3 se visse dans l'avant-trou de la lame : contact voulu.
    return a.get('threaded_into')==b.name or b.get('threaded_into')==a.name

closed=[]
for a,b in itertools.combinations(printed+hardware,2):
    if threaded(a,b):continue
    v=intersect(a,b)
    if v>.02:closed.append(dict(a=a.name,b=b.name,volume_mm3=round(v,4)))

# Copies des battants (pieces imprimees et aimants qu'ils portent).
leaves={}
for side in (-1,1):
    copies=[]
    for o in printed+hardware:
        if o.get('moving_side')==side:
            c=o.copy();c.data=o.data.copy();bpy.context.collection.objects.link(c)
            c.matrix_world=o.matrix_world.copy();copies.append(c)
    leaves[side]=copies
bpy.context.view_layer.update()
fixed=[o for o in printed+hardware if not o.get('moving_side')]
cams=[o for o in fixed if o.get('print_group')=='29_Cames_rapportees']
axis=params['opening_width']/2-5
original={o.name:o.matrix_world.copy() for objects in leaves.values() for o in objects}
free_angle=int(params['free_swing_angle']);stop_angle=int(params['stop_angle'])

def pose(side,deg,rise):
    for o in leaves[side]:
        pivot=Vector((side*axis,-5,0))
        o.matrix_world=(Matrix.Translation((0,0,rise*abs(deg)/90))@Matrix.Translation(pivot)
                        @Matrix.Rotation(math.radians(side*deg),4,'Z')@Matrix.Translation(-pivot)@original[o.name])
    bpy.context.view_layer.update()

# Debattement pour chaque came : la came montee (nominale) est verifiee contre le
# battant ; pour les autres pentes, elle est remplacee, donc ecartee du controle
# (l'enveloppe came/battant est verifiee numeriquement par generate.py).
angles=list(range(-free_angle,free_angle+1,5));collisions=[]
for rise in params['cam_rises']:
    others=fixed if rise==params['cam_rise'] else [o for o in fixed if o not in cams]
    for deg in angles:
        for side in leaves:pose(side,deg,rise)
        pairs=[(o,f) for objects in leaves.values() for o in objects for f in others]
        pairs += list(itertools.product(leaves[-1],leaves[1]))
        for a,b in pairs:
            v=intersect(a,b)
            if v>.02:collisions.append(dict(rise=rise,angle=deg,a=a.name,b=b.name,volume_mm3=round(v,4)))

# Verrou central : lame et bouton montes (FERME), tourniquet tourne dessous. Chaque
# battant pousse doit heurter la lame ; ferme et au repos, aucun contact.
lock=[o for o in printed+hardware if o.get('central_lock')]
blade=next(o for o in lock if o.get('lock_travel'))
turn=next(o for o in lock if o.get('turnstile_pivot'))
knob=next(o for o in lock if o.get('knob_bottom_locked') is not None)
rise_to_seat=blade['lock_travel']
lock_base={o.name:o.matrix_world.copy() for o in lock}
for o in lock:
    if o is not turn:o.matrix_world=Matrix.Translation((0,0,rise_to_seat))@lock_base[o.name]
pv=Vector(turn['turnstile_pivot'])
turn.matrix_world=Matrix.Translation(pv)@Matrix.Rotation(math.radians(-90),4,'Y')@Matrix.Translation(-pv)@lock_base[turn.name]
bpy.context.view_layer.update()
kl,kh=aabb(knob);tl,th=aabb(turn)
turnstile=dict(knob_bottom_z=round(kl[2],2),arm_top_z=round(th[2],2),gap_mm=round(kl[2]-th[2],2),
               overlap_mm3=round(intersect(knob,turn),4),
               supports_knob=abs(kl[2]-th[2])<.3 and tl[0]<0<th[0])
locked_rest=[]
for side in leaves:
    pose(side,0,params['cam_rise'])
    v=sum(intersect(o,b) for o in leaves[side] for b in lock)
    locked_rest.append(dict(side=side,overlap_mm3=round(v,4)))
# Balayage fin : la paroi de la poche ne doit pas pouvoir passer la lame entre 0 et
# ±5 degres (un seul angle de 5 degres la ferait sauter par-dessus).
engagement=[]
for sign in (-1,1):
    for side in leaves:
        hit=None
        for k in range(1,11):
            deg=sign*k*.5;pose(side,deg,params['cam_rise'])
            if sum(intersect(o,blade) for o in leaves[side])>.02:hit=deg;break
        engagement.append(dict(side=side,direction=sign,blocks_motion=hit is not None,blocked_at_deg=hit))
        pose(side,0,params['cam_rise'])
bl,bh=aabb(blade);locked_top=bh[2]
for o in lock:o.matrix_world=lock_base[o.name]
bpy.context.view_layer.update()
bl,bh=aabb(blade);free_top=bh[2]
tl,th=aabb(turn);kl,kh=aabb(knob)
turnstile['open_clears_knob']=tl[0]>kh[0]+.5
turnstile['open_top_z']=round(th[2],2)
central_lock=dict(free_top_z=round(free_top,2),locked_top_z=round(locked_top,2),
                  leaf_bottom_z=1.0,engagement_mm=round(locked_top-1,2),
                  free_clears_leaves=free_top<1.0)

# Butees : libres jusqu'a ±80 degres, au contact a ±85 degres (came nominale).
stops=[o for o in printed if o.get('print_group')=='23_Butees_TPU']
stop_contacts=[]
for deg in (-stop_angle,stop_angle):
    for side in leaves:
        pose(side,deg,params['cam_rise'])
        volume=sum(intersect(o,stop) for o in leaves[side] for stop in stops)
        stop_contacts.append(dict(side=side,angle=deg,contacts_tpu=volume>.02,volume_mm3=round(volume,4)))
    for side in leaves:pose(side,0,params['cam_rise'])

# Aimants : ecart nominal battant / seuil, et distance aimant / ILS.
def find(prefix,side):
    tag='gauche' if side<0 else 'droite'
    return next(o for o in hardware if o.name.startswith(prefix) and o.name.endswith(tag))
magnets=[]
for side in (-1,1):
    leaf=aabb(find('METAL_aimant_battant_',side));sill=aabb(find('METAL_aimant_seuil_',side))
    sensor=aabb(find('METAL_aimant_capteur_',side));reed=aabb(find('METAL_ILS_',side))
    magnets.append(dict(side=side,anti_vent_gap_mm=round(leaf[0][2]-sill[1][2],2),
                        anti_vent_gap_range_mm=[round(leaf[0][2]-sill[1][2]-k+params['shims_nominal'],2) for k in range(0,5)],
                        capteur_distance_mm=round((reed[0][2]+reed[1][2])/2-sensor[1][2],2)))

mode_truth_table=[
    dict(mode='LIBRE',entree=True,sortie=True,verrou_central=False),
    dict(mode='FERME',entree=False,sortie=False,verrou_central=True),
]
def lift(deg,rise):return rise*abs(deg)/90
report=dict(closed_assembly_overlaps=closed,angles_degrees=angles,cam_rises=params['cam_rises'],
            motion_collisions=collisions,central_lock=central_lock,locked_at_rest=locked_rest,
            central_lock_blocks_both_directions=engagement,turnstile=turnstile,soft_stop_contacts=stop_contacts,
            magnets=magnets,mode_truth_table=mode_truth_table,
            gravity_cam=dict(rises_mm=params['cam_rises'],nominal_mm=params['cam_rise'],gap_mm=params['cam_gap'],
                             lift_at_stop_mm={str(r):round(lift(stop_angle,r),2) for r in params['cam_rises']},
                             axes=[dict(name=o.name,length_mm=o['axis_length'],clip_spacing_mm=o['clip_spacing'])
                                   for o in hardware if o.get('axis_length')]),
            limitations='Positions discretes et volumes rigides nominaux. Couple de rappel, frottement de la came, force des aimants, seuil des ILS, TPU, fatigue et force du chat exigent un prototype physique.')
(ROOT/'controle_geometrie.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
if (closed or collisions
        or not all(x['blocks_motion'] for x in engagement)
        or any(x['overlap_mm3']>.02 for x in locked_rest)
        or not central_lock['free_clears_leaves']
        or not turnstile['supports_knob'] or turnstile['overlap_mm3']>.02 or not turnstile['open_clears_knob']
        or not all(x['contacts_tpu'] for x in stop_contacts)):
    raise RuntimeError('Interferences ou defaut de verrouillage detectes')
