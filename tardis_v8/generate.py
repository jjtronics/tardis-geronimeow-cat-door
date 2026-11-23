"""TARDIS V8 : version unique, derivee de la V7 Lite.
Rappel par gravite avec cames rapportees reglables, verrou central unique, aimants
anti-vent reglables par cales, capteur de passage (ILS) et eclairage RGB pilotes par
un ESP32 loge sous le tunnel, gabarit de decoupe de la porte.
Blender 5 : blender --background --python tardis_v8/generate.py
Toutes les cotes de construction sont en millimetres.
"""
from pathlib import Path
import bpy, bmesh, math, json, struct, zipfile, sys
import xml.etree.ElementTree as ET
from mathutils import Vector, Matrix
from collections import defaultdict

ROOT=Path(__file__).resolve().parent
for d in ('stl','3mf'): (ROOT/d).mkdir(exist_ok=True)
P=dict(opening_width=190., opening_height=200., door_depth=40.,
       tunnel_wall=2.4, pivot_hole=3.4, center_gap=2.4,
       # Cames rapportees : le battant monte de cam_rise mm par quart de tour. Trois
       # pentes interchangeables ; le battant porte l'enveloppe des trois, qui touche
       # chaque came sur les lignes a ±cam_ref degres, a la meme hauteur cam_z_ref.
       cam_rise=4.5, cam_rises=(3.5,4.5,5.5), cam_ref=60., cam_z_ref=45., cam_gap=.3,
       leaf_top_cut=5.,
       # Verrou central unique : lame verticale qui monte dans les deux battants.
       lock_width=10., lock_thickness=4., lock_y=-5., lock_engage=4., lock_length=15.,
       # Aimants anti-vent Ø6 x 2 (seuil et bas des battants), ecart regle par cales de 1 mm.
       magnet_d=6., magnet_h=2., magnet_x=20., sill_pocket=6., shims_nominal=1,
       # Capteur de passage : aimant Ø6 x 3 en haut de chaque battant, ILS dans le linteau.
       sensor_magnet_h=3., reed_length=14., reed_d=2.2,
       # Eclairage RGB : rainures de cables au dos des facades et berceau d'ESP32-C3
       # SuperMini (22,5 x 18 mm) loge sous le tunnel, port USB-C cote interieur.
       groove_width=4.5, groove_depth=2.5, esp_box_width=34., esp_box_height=10.3,
       esp_board_width=18.4, usb_window=(13.,7.5),
       free_swing_angle=80., stop_angle=85.,
       preview_angle=62., fit_clearance=.25, glue_gap=.1, swing_clearance=.4,
       bed_width=300., bed_depth=295., bed_margin=8., part_gap=8.,
       # Tour de purge Creality Print (K1 Max 0,4 mm) : 35 mm de large, environ 28 mm de
       # profondeur a 4 couleurs, plus une bordure de 3 mm, donc jusqu'a y = 288 environ.
       tower_x=60., tower_y=257., tower_depth=28., tower_brim=3.,
       template_thickness=3., door_cut_clearance=.7, esp_notch=(36.,11.))
W,H,D=P['opening_width'],P['opening_height'],P['door_depth']
A=W/2-5
# Came en V rapportee : surface z = Z_REF + r*(|theta|-REF)/90, theta mesure autour de
# l'axe depuis la face avant. Tourne de phi, le battant monte de r*|phi|/90 : son poids
# le ramene au centre avec un couple constant, dans les deux sens. Le battant porte
# l'enveloppe L(u) = Z_REF + gap + (rmin si u<REF sinon rmax)*(u-REF)/90 : quelle que
# soit la came posee (rmin <= r <= rmax), le contact se fait sur les lignes u = ±REF.
CAM_BASE=30+8;Z_REF=P['cam_z_ref'];REF=P['cam_ref']
RMIN,RMAX=min(P['cam_rises']),max(P['cam_rises'])
CAM_PEAK=Z_REF+RMAX*(180-REF)/90
LEAF_CAM_TOP=CAM_PEAK+P['cam_gap']+1.
LIFT=RMAX*P['stop_angle']/90
def insert_profile(r):return lambda th:Z_REF+r*(abs(th)-REF)/90
def leaf_profile(th):
    u=abs(th);return Z_REF+P['cam_gap']+(RMIN if u<REF else RMAX)*(u-REF)/90
TOP=H-1-P['leaf_top_cut']
# Clips d'axes fixes : sous chaque noeud du cadre et au-dessus de chaque noeud du
# battant, avec la course de levee en plus.
CLIPS={'bas':(30-.65,LEAF_CAM_TOP+8+LIFT+.6),'haut':(H-46-.65,H-37.4+8+LIFT+.6)}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.001

# Quatre couleurs imprimables. Le metal des axes et des liaisons est une fourniture distincte.
COLORS=[('01_BLEU_TARDIS','#123A63'),('02_IVOIRE','#F4E6C8'),
        ('03_NOIR','#161B23'),('04_LAITON','#BD9452')]
def srgb(x): return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def material(name,hex_color,metal=0):
    rgb=[srgb(int(hex_color[i:i+2],16)/255) for i in (1,3,5)]
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    n=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if n is None:
        n=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
        out=m.node_tree.nodes.new('ShaderNodeOutputMaterial')
        m.node_tree.links.new(n.outputs['BSDF'],out.inputs['Surface'])
    n.inputs['Base Color'].default_value=(*rgb,1)
    n.inputs['Roughness'].default_value=.32
    n.inputs['Metallic'].default_value=metal
    return m
M=[material(n,c) for n,c in COLORS]
METAL=material('FOURNITURE acier','#8C98A0',.7)
GROUPS=defaultdict(list)
PRINT_INFO={}

def box(name,lo,hi,color=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=[(a+b)/2 for a,b in zip(lo,hi)])
    o=bpy.context.object;o.name=name;o.dimensions=[b-a for a,b in zip(lo,hi)]
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(M[color]);return o

def bevel(o,amount=.45):
    bpy.context.view_layer.objects.active=o
    mod=o.modifiers.new('Chanfreins reels','BEVEL');mod.width=amount;mod.segments=3
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return o

def block(name,lo,hi,color=0,r=.45): return bevel(box(name,lo,hi,color),r)

def cyl(name,center,radius,length,axis='Z',color=0,vertices=64,radius2=None):
    if radius2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=length,location=center)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=radius2,depth=length,location=center)
    o=bpy.context.object;o.name=name
    if axis=='X':o.rotation_euler.y=math.pi/2
    if axis=='Y':o.rotation_euler.x=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    o.data.materials.append(M[color]);return o

def boolean(a,b,op,solver='MANIFOLD'):
    bpy.context.view_layer.objects.active=a
    mod=a.modifiers.new(op,'BOOLEAN');mod.operation=op;mod.solver=solver;mod.object=b
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(b,do_unlink=True);return a

def merge(objects,name):
    a=objects[0]
    for b in objects[1:]:boolean(a,b,'UNION')
    a.name=name;return a

def came(name,s,lower,profile,z_base=CAM_BASE,z_top=LEAF_CAM_TOP,segments=288):
    # Solide annulaire troue a 1,75 mm (l'axe fait 3 mm) jusqu'au rayon des noeuds :
    # aucun percage ne traverse l'helice, ce qui garde un maillage propre. Pas de
    # 1,25 degre : les aretes a 0, ±REF et 180 degres tombent sur des sommets.
    ri,ro=1.75,4.2
    me=bpy.data.meshes.new(name);bm=bmesh.new();rings=[]
    for i in range(segments):
        th=-180+360*i/segments;f=profile(th)
        lo,hi=(z_base,f) if lower else (f,z_top)
        c,sn=math.cos(math.radians(th)),math.sin(math.radians(th))
        pts=[(ri,lo),(ro,lo),(ro,hi),(ri,hi)]
        rings.append([bm.verts.new((s*A+r*sn,-5-r*c,z)) for r,z in pts])
    for i in range(segments):
        a,b=rings[i],rings[(i+1)%segments]
        for k in range(4):
            bm.faces.new((a[k],a[(k+1)%4],b[(k+1)%4],b[k]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
    o.data.materials.append(M[0]);return o

def half_cam(s,front):
    # Moitie de came mobile pour une demi-coque, posee contre son noeud (z = LEAF_CAM_TOP).
    # Elle est ajoutee apres le partage (la demi-coque arriere vient du battant oppose
    # tourne de 180 degres) et jointe sans booleen : le trancheur reunit les volumes.
    y0,y1=(-40,-5-P['glue_gap']/2) if front else (-5+P['glue_gap']/2,30)
    cam=came('came mobile',s,lower=False,profile=leaf_profile)
    return boolean(cam,box('moitie came',(-200,y0,-10),(200,y1,H+10)),'INTERSECT')

# Cle en D sur le noeud fixe : la came rapportee ne peut ni tourner ni etre posee a
# l'envers. Meplat cote arriere, symetrique : la meme came sert a gauche et a droite.
KEY_R,KEY_FLAT,KEY_H=3.,1.7,1.5
def d_key(name,s,r,flat,z0,z1):
    k=cyl(name,(s*A,-5,(z0+z1)/2),r,z1-z0)
    return boolean(k,box('meplat',(s*A-10,-5+flat,z0-1),(s*A+10,10,z1+1)),'DIFFERENCE')

def came_rapportee(name,s,rise):
    # Came fixe interchangeable : enfilee sur l'axe, cle en D dessous, reperee par
    # 1 a 3 rainures verticales a l'arriere (3,5 / 4,5 / 5,5 mm par quart de tour).
    cam=came(name,s,lower=True,profile=insert_profile(rise))
    boolean(cam,d_key('logement cle',s,KEY_R+.2,KEY_FLAT+.2,CAM_BASE-.1,CAM_BASE+KEY_H+.2),'DIFFERENCE')
    n=P['cam_rises'].index(rise)+1
    for k in range(n):
        x=s*A+(k-(n-1)/2)*1.2
        boolean(cam,box('repere pente',(x-.3,-5+3.8,CAM_BASE+KEY_H+.6),(x+.3,-5+5,CAM_BASE+KEY_H+3.6)),'DIFFERENCE')
    cam['cam_rise']=rise;return cam

def join_mesh(objects,name):
    # Des volumes disjoints (lettres) restent valides dans une meme partie couleur.
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.join();o=bpy.context.object;o.name=name;return o

def register(o,group,color=0,moving=0,orientation='FACE'):
    o['print_group']=group;o['filament']=color+1;o['moving_side']=moving
    o.data.materials.clear();o.data.materials.append(M[color])
    GROUPS[group].append(o);PRINT_INFO[group]=orientation
    return o

def ring(name,x0,x1,z0,z1,width,front=-10,back=-6.5,r=.45):
    o=block(name,(x0,front,z0),(x1,back,z1),r=r)
    return boolean(o,block('vide moulure',(x0+width,front-3,z0+width),
                          (x1-width,back+3,z1-width),r=r),'DIFFERENCE')

font=bpy.data.fonts.load('/System/Library/Fonts/Supplemental/Arial Bold.ttf')
def lettering(name,body,x,z,size,front,color=1,max_width=None,depth=.6):
    bpy.ops.object.text_add(location=(x,front+depth/2,z))
    o=bpy.context.object;o.name=name;o.data.body=body;o.data.font=font
    o.data.align_x='CENTER';o.data.size=size;o.data.extrude=depth/2
    o.data.resolution_u=6;o.rotation_euler.x=math.pi/2
    bpy.context.view_layer.update()
    if max_width and o.dimensions.x>max_width:
        o.scale.x*=max_width/o.dimensions.x
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(M[color]);return o

# Cadre monobloc : dos plan pour l'impression, pilastres, corniches et seuil.
body=box('cadre structure',(-119,-8,-12),(119,0,H+12))
boolean(body,box('ouverture',(-W/2-P['swing_clearance'],-30,0),
                (W/2+P['swing_clearance'],2,H)),'DIFFERENCE')
items=[bevel(body,.7)]
for s in (-1,1):
    x=s*107
    items += [block('pilastre',(x-11,-15,-9),(x+11,-7,H+9),r=.8),
              block('filet central',(x-6,-17,4),(x+6,-14,H-4),r=.5)]
    for z in (-10,H-1):
        items.append(block('collier',(x-13,-18,z),(x+13,-7,z+10),r=.65))
    for z in (30,H-46):
        items += [box('patte fixe',(min(x,s*A)-2,-7,z),(max(x,s*A)+2,-3,z+8)),
                  cyl('noeud fixe',(s*A,-5,z+4),4.2,8)]
    items.append(d_key('cle came rapportee',s,KEY_R,KEY_FLAT,CAM_BASE-.5,CAM_BASE+KEY_H))
items += [block('socle',(-122,-19,-16),(122,0,-6),r=.9),
          block('seuil biseaute',(-W/2,-11,-7),(W/2,0,0),r=.6),
          block('traverse haute',(-W/2,-15,H),(W/2,0,H+13),r=.7),
          block('bandeau enseigne',(-122,-20,H+12),(122,0,H+46),r=.8),
          block('corniche basse',(-122,-21,H+44),(122,0,H+49),r=.7),
          block('corniche milieu',(-115,-18,H+48),(115,0,H+55),r=.7),
          block('corniche haute',(-106,-15,H+54),(106,0,H+61),r=.7)]
frame=merge(items,'cadre_monobloc_moulure')
for s in (-1,1):
    for z in (30,H-46):
        boolean(frame,cyl('passage axe',(s*A,-5,z+4),P['pivot_hole']/2,12),'DIFFERENCE')
    for z in (30,H-24):
        boolean(frame,cyl('fixation M4',(s*107,-8,z),2.3,38,'Y'),'DIFFERENCE')
        boolean(frame,cyl('lamage vis',(s*107,-16.5,z),4.3,6,'Y'),'DIFFERENCE')
# Fourreaux d'axe (Ø8,4 x 8 mm) : cadre a plat, leur dessous arrondi flotte a 0,8 mm du
# plateau. Volume de support (x0,y0,z0,x1,y1,z1) sous chacun, arrete avant le trou d'axe.
frame['support_boxes']=[c for s in (-1,1) for z in (30,H-46)
                        for c in (s*A-4.6,-3.,z,s*A+4.6,0.,z+8+KEY_H if z==30 else z+8)]
boolean(frame,block('logement enseigne',(-112,-24,H+16),(112,-17.7,H+42),r=.5),'DIFFERENCE')
# Verrou central unique : une lame (10 x 4 mm) coulisse verticalement dans le seuil, au
# milieu, et monte de 4 mm dans les poches des deux battants. Un bouton visse (M3) sort
# par une fente verticale du socle. La lame, guidee a 0,2 mm, ne bouge que verticalement :
# on monte le bouton et on tourne dessous un tourniquet (loquet pivotant d'un quart de
# tour, vis M3 x 12) qui le tient en haut. Tourniquet releve, la lame retombe sous le seuil.
LW,LT,LKY=P['lock_width'],P['lock_thickness'],P['lock_y']
LOCK_DOWN=-.5-P['lock_length']          # bas de la lame, position LIBRE
LOCK_UP=1+P['lock_engage']-P['lock_length']  # bas de la lame, position FERME (sur le tourniquet)
SCREW=4.                                # vis du bouton a 4 mm du bas de la lame
KNOB_R=4.5;TX,TZ=8.,LOCK_UP+SCREW-KNOB_R-1.5  # pivot du tourniquet (bras de 3 mm sous le bouton)
def front_features(o):
    # Propres a la facade avant : creuses apres la copie de la facade arriere.
    # Jeu de 0,2 mm, porte a 0,4 mm sur la face avant : facade imprimee dos au plateau,
    # cette face est un pont de 10,4 mm qui peut flechir.
    boolean(o,box('canal verrou central',(-LW/2-.2,LKY-LT/2-.4,-17),(LW/2+.2,LKY+LT/2+.2,.5)),'DIFFERENCE')
    # Fente verticale : 1 mm de surcourse au-dessus de FERME pour passer le tourniquet.
    zl,zu=LOCK_DOWN+SCREW,LOCK_UP+SCREW+1
    boolean(o,box('fente bouton',(-1.7,-25,zl-1.7),(1.7,LKY,zu+1.7)),'DIFFERENCE')
    boolean(o,cyl('avant-trou pivot tourniquet',(TX,-15,TZ),1.25,8,'Y'),'DIFFERENCE')
    # Aimants anti-vent du seuil : logement profond de 6 mm, l'aimant pose sur 0 a 4
    # cales de 1 mm. Plus de cales, aimant plus proche du battant : maintien plus fort.
    for s in (-1,1):
        boolean(o,cyl('logement aimant seuil',(s*P['magnet_x'],-5,(.5-P['sill_pocket'])/2),
                      P['magnet_d']/2+.15,P['sill_pocket']+.5),'DIFFERENCE')
    # Capteur de passage : rainure de 2 fils sous le linteau (z 201-205), reliee a la
    # rainure du jambage, et deux poches d'ILS (verre Ø2,2 x 14) au-dessus des aimants
    # des battants, a 1 mm sous l'ouverture : le plastique laisse passer le champ.
    boolean(o,box('rainure capteur',(-(P['magnet_x']+18),-GD,H+1),(GX+GW/2,1,H+5)),'DIFFERENCE')
    for s in (-1,1):
        x0,x1=sorted((s*(P['magnet_x']-2),s*(P['magnet_x']+18)))
        boolean(o,box('poche ILS',(x0,-6,H+1),(x1,1,H+5)),'DIFFERENCE')
# Eclairage pilote : rainure de cables (4,5 x 2,5 mm) sur le dos de la facade, contre la
# porte, invisible une fois posee. Elle descend de la lanterne, longe la traverse
# haute, descend le jambage x>0 entre le tunnel et les vis M4, puis revient sous le
# tunnel jusqu'au berceau de l'ESP. La facade arriere (tournee de 180 degres) recoit
# la meme rainure, cote x<0.
GW,GD,GX,GZ_TOP,GZ_BOT=P['groove_width'],P['groove_depth'],101.,H+40,-9.
ESP_TOP=-P['tunnel_wall']-.3;ESP_FLOOR=ESP_TOP-P['esp_box_height']+1.6
def cable_groove(o):
    w=GW/2
    for lo,hi in [((-w,-GD,GZ_TOP-w),(w,1,H+62)),
                  ((-w,-GD,GZ_TOP-w),(GX+w,1,GZ_TOP+w)),
                  ((GX-w,-GD,GZ_BOT-w),(GX+w,1,GZ_TOP+w)),
                  ((P['esp_box_width']/2-7.5,-GD,GZ_BOT-w),(GX+w,1,GZ_BOT+w))]:
        boolean(o,box('rainure cable',lo,hi),'DIFFERENCE')
cable_groove(frame)
register(frame,'01_Cadre')

# Caches-vis amovibles : logement et couvercle separes, sans chevauchement.
for s in (-1,1):
    for z in (30,H-24):
        cap=merge([cyl('tete cache',(s*107,-17.5,z),4.7,1,'Y'),
                   cyl('tenon cache',(s*107,-16.45,z),4.15,1.3,'Y')],'cache_vis_'+str(s)+'_'+str(z))
        bevel(cap,.18)
        # Imprime tete sur le plateau : face visible lisse, tenon au-dessus, sans surplomb.
        register(cap,'07_Caches_vis',orientation='REAR')

# Enseigne rapportee : trois tailles de lettres, toutes presentes en maillage.
# L'enseigne remplit exactement son logement et s'imprime dans la facade
# (noir + ivoire), sans piece a coller. Plaque affleurante a 0,1 mm sous le bandeau.
sign=block('enseigne_noire',(-112,-20.1,H+16),(112,-17.7,H+42),2,r=.5)
register(sign,'01_Cadre',2)
letters=[lettering('POLICE','POLICE',-59,H+22,17.5,-20.7,1,83),
         lettering('BOX','BOX',78,H+22,17.5,-20.7,1,48),
         lettering('PUBLIC','PUBLIC',14,H+30,6.8,-20.7,1,35),
         lettering('CALL','CALL',14,H+22.5,6.8,-20.7,1,35)]
sign_letters=register(join_mesh(letters,'lettrage_enseigne_ivoire'),'01_Cadre',1)

# Portes : vrais panneaux moulures, fenetres ivoire et petits bois bleus.
for s,side in [(-1,'gauche'),(1,'droit')]:
    group='02_Battant_gauche' if s<0 else '03_Battant_droit'
    lo,hi=sorted((s*(A+1),s*(P['center_gap']/2)));cx=(lo+hi)/2
    # Raccourci en haut : le battant monte de LIFT a l'ouverture maximale.
    objects=[block('ame battant',(lo,-7,1),(hi,-3,TOP),r=.5),
             ring('cadre peripherique',lo,hi,1,TOP,5,-10,-6.6,.45),
             block('traverse basse pleine',(lo,-9.5,1),(hi,-.5,20),r=.45),
             # Bossage plein en haut, pour l'aimant du capteur de passage.
             block('bossage aimant capteur',(s*P['magnet_x']-5,-10,TOP-6),(s*P['magnet_x']+5,-.5,TOP),r=.45)]
    for z0,z1 in [(23,55),(61,93),(99,130)]:
        objects.append(ring('panneau moulure',lo+7,hi-7,z0,z1,2.4,-9.3,-6.7,.45))
    # Encadrement de la fenetre et ses trois colonnes / deux rangees.
    x0,x1,z0,z1=lo+7,hi-7,137,TOP-7
    objects.append(ring('cadre fenetre',x0-1,x1+1,z0-1,z1+1,2.8,-10,-6.8,.4))
    for i in (1,2):
        x=x0+(x1-x0)*i/3
        objects.append(block('petit bois',(x-1,-10,z0),(x+1,-6.8,z1),r=.18))
    objects.append(block('petit bois horizontal',(x0,-10,(z0+z1)/2-1.1),
                         (x1,-6.8,(z0+z1)/2+1.1),r=.18))
    # Noeud mobile inferieur pose sur la came du battant (rappel par gravite).
    for z in (LEAF_CAM_TOP,H-37.4):
        objects += [cyl('noeud mobile',(s*A,-5,z+4),4.2,8),
                    box('patte mobile',(s*A-3,-7,z),(s*A+3,-3,z+8))]
    leaf=merge(objects,'battant_'+side)
    # Poche du verrou central au coin bas du bord libre, fermee devant et derriere
    # (2,7 mm de paroi) : la lame montee bloque le battant dans les deux sens.
    nx0,nx1=sorted((0,s*(LW/2+.3)))
    boolean(leaf,box('poche verrou central',(nx0,LKY-LT/2-.3,-1),(nx1,LKY+LT/2+.3,1+P['lock_engage']+1.6)),'DIFFERENCE')
    # Aimant anti-vent (Ø6 x 2, affleurant dessous) et aimant du capteur (Ø6 x 3, en haut).
    boolean(leaf,cyl('logement aimant bas',(s*P['magnet_x'],-5,.5+(P['magnet_h']+.25)/2),
                     P['magnet_d']/2+.15,P['magnet_h']+.75),'DIFFERENCE')
    boolean(leaf,cyl('logement aimant capteur',(s*P['magnet_x'],-5,TOP-(P['sensor_magnet_h']+.25)/2+.25),
                     P['magnet_d']/2+.15,P['sensor_magnet_h']+.75),'DIFFERENCE')
    for z in (30,H-46):
        e0,e1=sorted((s*(A-6.4),s*(A+7.4)))
        # Prolonge vers le bas de la levee : le battant monte autour du noeud fixe.
        top=CAM_PEAK+.6 if z==30 else z+8.6
        boolean(leaf,box('degagement fixe',(e0,-16,z-1.5-LIFT),(e1,4,top)),'DIFFERENCE')
    # Alesages coaxiaux et logements des clips hauts : ils couvrent toute la levee.
    for label,(c0,c1) in CLIPS.items():
        boolean(leaf,cyl('alesage axe '+label,(s*A,-5,(c0+c1)/2+.1),P['pivot_hole']/2,c1-c0+2.2),'DIFFERENCE')
        boolean(leaf,cyl('logement clip axe',(s*A,-5,c1-LIFT/2),2.7,LIFT+1.2),'DIFFERENCE')
    register(leaf,group,0,s)
    window=block('vitre_ivoire_'+side,(x0+1.8,-9.1,z0+1.8),(x1-1.8,-6.9,z1-1.8),1,r=.2)
    # Retrait du volume bleu pour des couleurs physiquement disjointes.
    cut=leaf.copy();cut.data=leaf.data.copy();bpy.context.collection.objects.link(cut)
    boolean(window,cut,'DIFFERENCE')
    register(window,group,1,s)
    # Petit bouton laiton : le pied s'evase en cone (24 degres de la verticale) jusqu'a la
    # face : imprime face en haut, il ne presente aucune corniche a plat.
    knob=merge([cyl('pied bouton',(s*10,-10.3,84),2.6,6.7,'Y',3),
                cyl('bouton conique',(s*10,-14.1,84),2.6,2,'Y',3,radius2=3.5),
                cyl('bouton facade',(s*10,-15.5,84),3.5,1,'Y',3)],'bouton_laiton_'+side)
    # Face arriere du bouton au contact du corps du battant.
    # Enlever le volume deja occupe par le bleu.
    cut=leaf.copy();cut.data=leaf.data.copy();bpy.context.collection.objects.link(cut)
    boolean(knob,cut,'DIFFERENCE')
    register(knob,group,3,s)
    if s<0:
        plaque=block('plaque_telephone',(cx-25,-10.2,102),(cx+25,-6.9,127.8),1,r=.45)
        cut=leaf.copy();cut.data=leaf.data.copy();bpy.context.collection.objects.link(cut)
        boolean(plaque,cut,'DIFFERENCE')
        register(plaque,group,1,s)
        texts=[]
        for line,z,size in [('POLICE',122,3.5),('TELEPHONE',117.5,3.5),
                            ('FREE FOR USE',113,3.2),('OF CATS',107.7,4.2)]:
            texts.append(lettering('texte plaque',line,cx,z,size,-10.8,2,46))
        register(join_mesh(texts,'texte_plaque_noir'),group,2,s)
    else:
        badge=bevel(cyl('medaillon_ivoire',(cx,-8.55,114),7.5,3.1,'Y',1),.2)
        cut=leaf.copy();cut.data=leaf.data.copy();bpy.context.collection.objects.link(cut)
        boolean(badge,cut,'DIFFERENCE')
        register(badge,group,1,s)
        cross=merge([box('croix verticale',(cx-.8,-10.7,109.5),(cx+.8,-10.1,118.5),2),
                     box('croix horizontale',(cx-4.5,-10.7,113.2),(cx+4.5,-10.1,114.8),2)],'croix_medallion')
        register(cross,group,2,s)

# Tunnel et contre-cadre monobloc : pas de jonctions a chant a coller.
t=P['tunnel_wall']
tunnel=box('tunnel_exterieur',(-W/2-t,0,-t),(W/2+t,D,H+t))
boolean(tunnel,box('tunnel_interieur',(-W/2,-1,0),(W/2,D+1,H)),'DIFFERENCE')
# Un filet ivoire encastre a fleur a mi-profondeur donne a la vue arriere un
# plan de reference entre la facade et les battants. Il ne depasse pas dans le
# passage et ne peut donc pas rencontrer les portes ouvertes.
RY=D/2
depth_marker=box('filet_recentreur_ivoire',(-W/2-t,RY-1.5,-t),(W/2+t,RY+1.5,H+t),1)
boolean(depth_marker,box('vide filet recentreur',(-W/2,RY-2,0),(W/2,RY+2,H)),'DIFFERENCE')
marker_cut=depth_marker.copy();marker_cut.data=depth_marker.data.copy();bpy.context.collection.objects.link(marker_cut)
boolean(tunnel,marker_cut,'DIFFERENCE')
register(tunnel,'05_Tunnel',orientation='TUNNEL')
register(depth_marker,'05_Tunnel',1,orientation='TUNNEL')

# Berceau ESP32 sous le tunnel, pris entre les deux facades (jeu 0,3 mm) : la porte
# est creusee de 36 x 11 mm sous l'ouverture du tunnel. Ouvert en haut (le sol du
# tunnel le ferme), une encoche par rainure de cable et une fente pour la fiche
# USB-C cote interieur. La carte se colle au double face sur le fond.
bw=P['esp_box_width'];wall=1.6
esp_box=block('berceau_ESP',(-bw/2,.3,ESP_TOP-P['esp_box_height']),(bw/2,D-.3,ESP_TOP),r=.4)
boolean(esp_box,box('cavite ESP',(-bw/2+wall,.3+wall,ESP_FLOOR),(bw/2-wall,D-.3-wall,ESP_TOP+1)),'DIFFERENCE')
uw,uh=P['usb_window']
boolean(esp_box,box('fente USB-C',(-uw/2,D-3,ESP_FLOOR),(uw/2,D+1,ESP_TOP+1)),'DIFFERENCE')
for y0,y1,sx in [(-1,3,1),(D-3,D+1,-1)]:
    x0,x1=sorted((sx*(bw/2-7.5),sx*(bw/2+1)))
    boolean(esp_box,box('encoche cable',(x0,y0,GZ_BOT-2),(x1,y1,ESP_TOP+1)),'DIFFERENCE')
# Deux taquets centrent la carte (18 mm) dans la largeur.
eb=P['esp_board_width']/2
for sx in (-1,1):
    x0,x1=sorted((sx*eb,sx*(bw/2-wall+.1)))
    boolean(esp_box,box('taquet carte',(x0,12,ESP_FLOOR-.1),(x1,30,ESP_FLOOR+2)),'UNION')
register(esp_box,'26_Berceau_ESP',orientation='UP')

# Quatre butees TPU remplaçables : deux cote facade et deux cote tunnel. Elles
# sont encastrees dans les volumes fixes et n'entrent en contact qu'en fin de
# course. Elles absorbent le claquement sans imposer l'effort d'ouverture.
for s,side in [(-1,'gauche'),(1,'droite')]:
    fx0,fx1=sorted((s*94.4,s*95.4))
    front_stop=block('butee_TPU_avant_'+side,(fx0,-14,60),(fx1,-9,68),r=.7)
    register(front_stop,'23_Butees_TPU',moving=0,orientation='AXIS_X')
    # Le battant décrit un arc plus intérieur côté tunnel : la butée arrière
    # avance de 1,6 mm vers le passage pour obtenir le même angle de contact.
    rx0,rx1=sorted((s*92.8,s*95.0))
    rear_stop=block('butee_TPU_arriere_'+side,(rx0,8,60),(rx1,13,68),r=.7)
    register(rear_stop,'23_Butees_TPU',moving=0,orientation='AXIS_X')
rear=block('contre_cadre',(-119,D,-12),(119,D+6,H+12),r=.7)
boolean(rear,box('ouverture arriere',(-W/2-t-.3,D-1,-t-.3),
                (W/2+t+.3,D+7,H+t+.3)),'DIFFERENCE')
for s in (-1,1):
    for z in (30,H-24):
        boolean(rear,cyl('vis traversante',(s*107,D+3,z),2.3,12,'Y'),'DIFFERENCE')
register(rear,'06_Contre_cadre',orientation='REAR')

# Lanterne a diffuseur creux. Passage pour LED 5 mm et cable a l'arriere.
LZ=H+61
base=merge([block('pied lanterne',(-14,-20,LZ),(14,0,LZ+4),r=.8),
            cyl('base circulaire',(0,-10,LZ+5),10,4),
            cyl('centrage diffuseur',(0,-10,LZ+8),6.6,3)],'base_lanterne')
boolean(base,cyl('logement LED',(0,-10,LZ+5),2.7,15),'DIFFERENCE')
boolean(base,cyl('cable LED',(0,-5,LZ+3),1.6,14,'Y'),'DIFFERENCE')
# Chambre de connexion sous la LED, ouverte dessous (posee sur la corniche) et reliee a
# la rainure arriere : pattes coudees, soudures gainees et condensateur de 100 nF (CMS
# 0805 ou petit traversant). 9 mm de large, 13,5 mm de long, 5,1 mm sous le faite. Le
# toit en pointe a 45 degres s'imprime sans pont ni support.
ch=box('chambre de connexion',(-4.5,-15,LZ-1),(4.5,-1.5,LZ+.6))
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,(-15-1.5)/2,LZ+.6))
roof=bpy.context.object;roof.dimensions=(4.5*2**.5,13.5,4.5*2**.5);roof.rotation_euler.y=math.pi/4
bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
boolean(ch,roof,'UNION')
boolean(base,ch,'DIFFERENCE')
# Le cable sort au dos du pied et descend dans la rainure de la facade.
boolean(base,box('rainure pied lanterne',(-P['groove_width']/2,-P['groove_depth'],LZ-1),
                 (P['groove_width']/2,1,LZ+3)),'DIFFERENCE')
register(base,'08_Base_lanterne',orientation='UP')
diff=cyl('diffuseur_ivoire',(0,-10,LZ+18),8,22,color=1)
boolean(diff,cyl('creux diffuseur',(0,-10,LZ+18),6.8,24),'DIFFERENCE')
register(diff,'09_Diffuseur',1,orientation='UP')
cage_items=[]
for z in (LZ+7.8,LZ+28.2):
    r=cyl('bague cage',(0,-10,z),10.,1.6)
    boolean(r,cyl('vide cage',(0,-10,z),8.25,4),'DIFFERENCE')
    cage_items.append(r)
for deg in (0,90,180,270):
    a=math.radians(deg);x,y=9.25*math.cos(a),-10+9.25*math.sin(a)
    cage_items.append(cyl('montant cage',(x,y,LZ+18.25),.95,22.5))
# Le chapeau est fondu avec la cage (une seule piece bleue, montants
# prolonges de 0,5 mm dans le bord du toit pour une vraie fusion).
cage_items += [cyl('bord toit',(0,-10,LZ+30),10.5,2),
               cyl('toit conique',(0,-10,LZ+33),10,5,radius2=4),
               cyl('finial',(0,-10,LZ+36),2.8,3)]
cage=merge(cage_items,'cage_chapeau_lanterne')
# Dessous du toit en cone a 45 degres (pointe en haut) : pas de plafond plat de 16 mm a
# franchir en pont. Le bord du diffuseur reste en appui sur la couronne de 7,5 a 8,25 mm.
boolean(cage,cyl('creux toit',(0,-10,LZ+28.9+3.8),7.6,7.6,radius2=0),'DIFFERENCE')
register(cage,'10_Cage_lanterne',orientation='UP')

# V5 : seconde facade complete et battants finis sur leurs deux faces.
# RZ(180) conserve le sens de lecture du texte lorsqu'on regarde depuis l'arriere.
def duplicate(o,transform,name):
    c=o.copy();c.data=o.data.copy();bpy.context.collection.objects.link(c)
    c.name=name;c.matrix_world=transform@o.matrix_world
    return c
TURN=Matrix(((-1,0,0,0),(0,-1,0,0),(0,0,1,0),(0,0,0,1)))
REAR_TRANSFORM=Matrix.Translation((0,D,0))@TURN
LEAF_TRANSFORM=Matrix.Translation((0,-10,0))@TURN

# Contre-facade sans charnieres superflues, avec logements pour les ecrous.
old_rear=GROUPS.pop('06_Contre_cadre')
for o in old_rear:bpy.data.objects.remove(o,do_unlink=True)
rear=duplicate(frame,Matrix.Identity(4),'cadre_arriere_tardis')
del rear['support_boxes']  # fourreaux propres au cadre avant
boolean(rear,box('supprimer charnieres arriere',(-95,-35,0),(95,2,H)),'DIFFERENCE')
for s in (-1,1):
    for z in (30,H-24):
        boolean(rear,cyl('logement ecrou',(s*107,-15,z),4.4,12,'Y'),'DIFFERENCE')
# Rainure de cables (heritee du cadre, recreusee par securite) et fenetre qui laisse
# entrer la fiche USB-C jusqu'a l'ESP, au ras du sol, cote interieur.
cable_groove(rear)
uw,uh=P['usb_window']
boolean(rear,box('fenetre USB-C',(-uw/2,-30,ESP_FLOOR),(uw/2,1,ESP_FLOOR+uh)),'DIFFERENCE')
rear.matrix_world=REAR_TRANSFORM@rear.matrix_world
front_features(frame)
register(rear,'06_Facade_arriere',orientation='REAR')

for o in (sign,sign_letters):
    c=duplicate(o,REAR_TRANSFORM,o.name+'_arriere')
    register(c,'06_Facade_arriere',o['filament']-1,orientation='REAR')
for old_group,new_group in [('08_Base_lanterne','18_Base_lanterne_AR'),
        ('09_Diffuseur','19_Diffuseur_AR'),('10_Cage_lanterne','20_Cage_lanterne_AR')]:
    for o in list(GROUPS[old_group]):
        c=duplicate(o,REAR_TRANSFORM,o.name+'_arriere')
        register(c,new_group,o['filament']-1,orientation='UP')
for o in list(GROUPS['07_Caches_vis']):
    c=duplicate(o,Matrix.Identity(4),o.name+'_arriere')
    x,z=o.location.x,o.location.z
    boolean(c,cyl('tenon cache arriere',(x,-16.45,z),4.25,1.3,'Y'),'UNION')
    # La cavite centrale recoit l'extremite de la vis M4x70.
    boolean(c,cyl('degagement bout de vis',(x,-16.4,z),2.3,2,'Y'),'DIFFERENCE')
    c.matrix_world=REAR_TRANSFORM@c.matrix_world
    # Tete sur le plateau, cavite ouverte vers le haut : ni pont ni surplomb.
    register(c,'16_Caches_vis_AR',orientation='FACE')

# Deux demi-coques imprimees a plat pour chaque battant. Plan de collage y=-5.
# Le decor arriere est tourne, pas simplement reflete : les lettres restent lisibles.
old_groups={-1:'02_Battant_gauche',1:'03_Battant_droit'}
old_parts={s:list(GROUPS[g]) for s,g in old_groups.items()}
cores={s:next(o for o in old_parts[s] if o.name.startswith('battant_')) for s in (-1,1)}
templates={s:duplicate(o,Matrix.Identity(4),'gabarit battant') for s,o in cores.items()}
for s,side in [(-1,'gauche'),(1,'droit')]:
    av=old_groups[s]+'_AV';ar='14_Battant_gauche_AR' if s<0 else '15_Battant_droit_AR'
    GROUPS[av]=GROUPS.pop(old_groups[s]);PRINT_INFO[av]='FACE'
    for o in GROUPS[av]:o['print_group']=av;o['half_face']='AV'
    full=cores[s]
    back=duplicate(templates[-s],LEAF_TRANSFORM,'battant_'+side+'_arriere')
    # Deux petits pions alignent les demi-coques et le canal du verrou au collage.
    for z in (74,182):
        boolean(full,cyl('alignement demi coques',(s*45,-5,z),1.1,3.2,'Y'),'DIFFERENCE')
        boolean(back,cyl('alignement dos',(s*45,-5,z),1.1,3.2,'Y'),'DIFFERENCE')
        peg=cyl('pion_'+side+'_'+str(z),(s*45,-5,z),1,3,'Y')
        register(peg,'22_Pions_battants',moving=s);peg['half_face']='PIN'
    boolean(full,box('moitie avant',(-200,-40,-10),(200,-5-P['glue_gap']/2,H+10)),'INTERSECT')
    boolean(back,box('moitie arriere',(-200,-5+P['glue_gap']/2,-10),(200,30,H+10)),'INTERSECT')

    # Prototype grandeur réelle limité aux 75 premiers millimètres : les deux
    # demi-coques bleues sont réunies dans un seul objet d'essai mécanique.
    proto_front=duplicate(full,Matrix.Identity(4),'prototype_battant_'+side+'_avant')
    proto_back=duplicate(back,Matrix.Identity(4),'prototype_battant_'+side+'_arriere')
    for proto,face in [(proto_front,'avant'),(proto_back,'arriere')]:
        proto.name='prototype_battant_'+side+'_'+face+'_75mm'
        boolean(proto,box('limite prototype battant',(-200,-40,-20),(200,40,75)),'INTERSECT')
        register(proto,'25_Prototype_battants_75mm',moving=s,orientation='FACE')
        proto['sample_only']=True;proto.hide_render=True
    join_mesh([proto_front,half_cam(s,True)],proto_front.name)
    join_mesh([proto_back,half_cam(s,False)],proto_back.name)
    # Demi-coque arriere posee comme le vrai battant arriere, decor vers le haut (sinon
    # ses panneaux en relief flottent a 0,8 mm du plateau).
    proto_back['print_orientation']='REAR'
    full.name='battant_'+side+'_avant'
    register(back,ar,moving=s,orientation='REAR');back['half_face']='AR'
    for o in old_parts[-s]:
        if o==cores[-s]:continue
        c=duplicate(o,LEAF_TRANSFORM,o.name+'_dos')
        if o.name in ('plaque_telephone','texte_plaque_noir','medaillon_ivoire','croix_medallion'):
            # Ces reliefs doivent rester dans y<=0 pour passer devant les jambages
            # lorsque le battant est ouvert a 90 degres vers l'arriere.
            c.matrix_world=Matrix.Translation((0,-1,0))@c.matrix_world
            if o.name in ('plaque_telephone','medaillon_ivoire'):
                boolean(back,duplicate(c,Matrix.Identity(4),'poche decor dos'),'DIFFERENCE')
        register(c,ar,o['filament']-1,s,orientation='REAR');c['half_face']='AR'
    join_mesh([full,half_cam(s,True)],full.name)
    join_mesh([back,half_cam(s,False)],back.name)
for o in templates.values():bpy.data.objects.remove(o,do_unlink=True)

# Verrou central : lame et bouton imprimes, vis M3 x 18. Position nominale LIBRE.
lock_blade=block('lame_verrou_central',(-LW/2,LKY-LT/2,LOCK_DOWN),(LW/2,LKY+LT/2,LOCK_DOWN+P['lock_length']),r=.6)
boolean(lock_blade,cyl('avant-trou M3',(0,LKY,LOCK_DOWN+SCREW),1.25,LT+2,'Y'),'DIFFERENCE')
lock_knob=bevel(cyl('bouton_verrou_central',(0,-20.5,LOCK_DOWN+SCREW),KNOB_R,3,'Y'),.5)
boolean(lock_knob,cyl('passage vis M3',(0,-20.5,LOCK_DOWN+SCREW),1.7,5,'Y'),'DIFFERENCE')
boolean(lock_knob,cyl('lamage tete M3',(0,-21.6,LOCK_DOWN+SCREW),2.9,1.6,'Y'),'DIFFERENCE')
# Tourniquet : bras de 3 x 3 mm pivotant sur une vis M3 x 12. Nominal : releve (vertical,
# LIBRE). Tourne d'un quart de tour vers le centre, il passe sous le bouton (FERME).
turn=block('tourniquet_verrou',(TX-1.5,-22,TZ-1.5),(TX+1.5,-19.1,TZ+TX+3),r=.5)
boolean(turn,cyl('pivot tourniquet',(TX,-20.5,TZ),1.7,5,'Y'),'DIFFERENCE')
# Lame imprimee a plat : couches dans sa longueur (l'effort des battants la cisaille
# en travers), avant-trou M3 vertical.
for o,orient in ((lock_blade,'FACE'),(lock_knob,'FACE'),(turn,'FACE')):
    o['removable_lock']=True;o['central_lock']=True;o['print_orientation']=orient
    register(o,'12_Verrou_central',orientation='UP')
lock_blade['lock_travel']=round(LOCK_UP-LOCK_DOWN,2)  # course de LIBRE a FERME
turn['turnstile_pivot']=(TX,-20.5,TZ);lock_knob['knob_bottom_locked']=round(LOCK_UP+SCREW-KNOB_R,2)

# Cames rapportees : la paire 4,5 mm est montee ; deux 3,5 et deux 5,5 de rechange.
cams=[]
for rise in P['cam_rises']:
    for s in (-1,1):
        c=came_rapportee('came_rapportee_'+f'{rise:g}'.replace('.',',')+('_gauche' if s<0 else '_droite'),s,rise)
        register(c,'29_Cames_rapportees',orientation='UP');cams.append(c)
        if rise!=P['cam_rise']:c['sample_only']=True;c.hide_render=True
        # Couches fines et pieces pleines : rampe lisse et cle en D solide.
        c['layer_height']='0.1';c['wall_loops']='4';c['sparse_infill_density']='100%'

# Fournitures : axes et clips, aimants, ILS, vis du verrou (non imprimes).
GLASS=material('FOURNITURE verre ILS','#B8D8E0')
MAGNET=material('FOURNITURE aimant','#5A5F66',.6)
hardware=[]
def metal(o,mat=None):
    o.data.materials.clear();o.data.materials.append(mat or METAL);o['hardware']=True
    hardware.append(o);return o
for s in (-1,1):
    side='gauche' if s<0 else 'droite'
    # Axes fixes au cadre par leurs clips ; le battant coulisse dessus en montant.
    for label,(c0,c1) in CLIPS.items():
        z,length=(c0+c1)/2,c1-c0+1.3
        pin=metal(cyl('METAL_axe_'+side+'_'+label,(s*A,-5,z),1.5,length))
        pin['axis_length']=round(length,1);pin['clip_spacing']=round(c1-c0,1)
        for cz in (c0,c1):
            clip=cyl('METAL_clip_axe_'+side+'_'+label,(s*A,-5,cz),2.5,.6)
            boolean(clip,cyl('passage clip',(s*A,-5,cz),1.58,1.2),'DIFFERENCE')
            metal(clip)
    mx,md,mh=s*P['magnet_x'],P['magnet_d']/2,P['magnet_h']
    # Aimant anti-vent du battant (affleurant dessous) et aimant du capteur (en haut).
    m=metal(cyl('METAL_aimant_battant_'+side,(mx,-5,1+mh/2),md,mh),MAGNET);m['moving_side']=s
    m=metal(cyl('METAL_aimant_capteur_'+side,(mx,-5,TOP-P['sensor_magnet_h']/2),md,P['sensor_magnet_h']),MAGNET)
    m['moving_side']=s
    # Aimant du seuil pose sur ses cales (nominal : 1 cale, 4 mm d'ecart avec le battant).
    z0=-P['sill_pocket']+P['shims_nominal']
    metal(cyl('METAL_aimant_seuil_'+side,(mx,-5,z0+mh/2),md,mh),MAGNET)
    for k in range(4):
        shim=cyl('cale_aimant_'+side+'_'+str(k+1),(mx,-5,-P['sill_pocket']+k+.5),md-.1,1)
        register(shim,'28_Cales_aimants',orientation='UP')
        if k>=P['shims_nominal']:shim['sample_only']=True;shim.hide_render=True
    # ILS (verre Ø2,2 x 14) dans sa poche du linteau, une extremite au-dessus de l'aimant.
    metal(cyl('METAL_ILS_'+side,(s*(P['magnet_x']+P['reed_length']/2),-3,H+3),P['reed_d']/2,P['reed_length'],'X'),GLASS)
screw=metal(cyl('METAL_vis_M3x18_verrou',(0,-12,LOCK_DOWN+SCREW),1.5,18,'Y'))
screw['threaded_into']=lock_blade.name;screw['central_lock']=True
pivot=metal(cyl('METAL_vis_M3x12_tourniquet',(TX,-17,TZ),1.5,12,'Y'))
pivot['threaded_into']='cadre_monobloc_moulure';pivot['turnstile_screw']=True

# Eprouvette independante pour valider les ajustements avant les grandes pieces.
coupon=block('eprouvette_jeux',(160,-12,0),(214,0,24),r=.5)
boolean(coupon,cyl('test pivot',(166,-6,12),P['pivot_hole']/2,28),'DIFFERENCE')
boolean(coupon,cyl('test vis',(193,-6,18),2.3,16,'Y'),'DIFFERENCE')
boolean(coupon,cyl('test cache',(193,-10,18),4.3,8,'Y'),'DIFFERENCE')
boolean(coupon,cyl('test pion collage',(180,-.75,18),1.1,1.7,'Y'),'DIFFERENCE')
# Logement d'aimant Ø6,3 : l'aimant Ø6 x 2 doit y entrer a la main, sans jeu.
boolean(coupon,cyl('test logement aimant',(178,-6,6.4),P['magnet_d']/2+.15,12),'DIFFERENCE')
# Avant-trou M3 de la lame et poche d'ILS.
boolean(coupon,cyl('test avant-trou M3',(205,-6,18),1.25,16,'Y'),'DIFFERENCE')
boolean(coupon,box('test poche ILS',(196,-7,2),(212,1,6)),'DIFFERENCE')
register(coupon,'00_Eprouvette_jeux');coupon['sample_only']=True;coupon.hide_render=True
# Canal du verrou (la lame du plateau 07 doit y coulisser) et cle en D (la came s'y emboite).
sample=block('eprouvette_verrou_et_cle',(220,-12,0),(250,0,24),r=.45)
boolean(sample,box('test canal verrou',(230-LW/2-.2,-6-LT/2-.4,-1),(230+LW/2+.2,-6+LT/2+.2,25)),'DIFFERENCE')
key=cyl('cle came',(244,-6,25.5),KEY_R,3)
boolean(key,box('meplat',(234,-6+KEY_FLAT,22),(254,10,30)),'DIFFERENCE')
boolean(sample,key,'UNION')
boolean(sample,cyl('passage axe',(244,-6,14),P['pivot_hole']/2,40),'DIFFERENCE')
register(sample,'00_Eprouvette_jeux');sample['sample_only']=True;sample.hide_render=True

# Gabarit de decoupe et de percage, a plat (x : largeur de la porte, y : hauteur).
# Fenetre = trait de scie (tunnel + 0,7 mm, encoche de l'ESP) ; avant-trous Ø3,2 des
# quatre vis M4 (percer ensuite a Ø5) ; encoches de reperage de l'axe vertical.
cl,tt=P['door_cut_clearance'],P['template_thickness']
cx,cz0,cz1=W/2+P['tunnel_wall']+cl,-P['tunnel_wall']-cl,H+P['tunnel_wall']+cl
nw,nh=P['esp_notch']
gab=block('gabarit_decoupe_porte',(-117,cz0-nh-13,0),(117,cz1+12,tt),r=.8)
boolean(gab,box('trait de scie tunnel',(-cx,cz0,-1),(cx,cz1,tt+1)),'DIFFERENCE')
boolean(gab,box('trait de scie ESP',(-nw/2,cz0-nh,-1),(nw/2,cz0+.5,tt+1)),'DIFFERENCE')
for s in (-1,1):
    for z in (30,H-24):
        boolean(gab,cyl('avant-trou M4',(s*107,z,tt/2),1.6,tt+2),'DIFFERENCE')
for y in (cz0-nh-13,cz1+12):
    v=cyl('repere axe',(0,y,tt/2),3,tt+2,vertices=3)
    boolean(gab,v,'DIFFERENCE')
def engrave(o,text,x,y,size):
    bpy.ops.object.text_add(location=(x,y,tt-.25));t=bpy.context.object
    t.data.body=text;t.data.font=font;t.data.align_x='CENTER';t.data.align_y='CENTER'
    t.data.size=size;t.data.extrude=.5;t.data.space_character=1.15;t.data.resolution_u=4;bpy.ops.object.convert(target='MESH')
    bm=bmesh.new();bm.from_mesh(t.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(t.data);bm.free()
    bpy.context.view_layer.objects.active=o
    mod=o.modifiers.new('gravure','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT'
    mod.object=t;mod.use_self=True;mod.use_hole_tolerant=True
    bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(t,do_unlink=True)
engrave(gab,'HAUT · TARDIS V8',0,cz1+6,6)
engrave(gab,'FACE EXTÉRIEURE',0,cz0-nh-6.5,5.5)
for s in (-1,1):
    for z in (30,H-24):engrave(gab,'Ø5',s*107,z+8,4.5)
register(gab,'27_Gabarit_porte',orientation='UP');gab['sample_only']=True;gab.hide_render=True
gab['template']=True

# Partie basse exacte du cadre, à imprimer seule avec les deux battants simplifiés
# pour régler la mécanique avant toute grande pièce multicolore.
proto_frame=duplicate(frame,Matrix.Identity(4),'prototype_cadre_bas_75mm')
boolean(proto_frame,box('limite prototype cadre',(-140,-40,-20),(140,40,75)),'INTERSECT')
register(proto_frame,'24_Prototype_cadre_bas',orientation='FACE')
proto_frame['sample_only']=True;proto_frame.hide_render=True

# Donnees de maillage et controles elementaires.
def mesh_data(o,transform=None):
    o.data.calc_loop_triangles()
    mat=o.matrix_world if transform is None else transform@o.matrix_world
    vs=[mat@v.co for v in o.data.vertices]
    ts=[tuple(t.vertices) for t in o.data.loop_triangles]
    return vs,ts

def mesh_stats(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    bad=sum(not e.is_manifold for e in bm.edges)
    volume=abs(bm.calc_volume());bm.free()
    return dict(name=o.name,group=o['print_group'],filament=o['filament'],
                non_manifold_edges=bad,volume_mm3=round(volume,3))

def write_stl(o,path):
    vs,ts=mesh_data(o)
    with path.open('wb') as f:
        f.write(b'TARDIS V8 mm'.ljust(80,b'\0'));f.write(struct.pack('<I',len(ts)))
        for t in ts:
            p=[vs[i] for i in t];n=(p[1]-p[0]).cross(p[2]-p[0]).normalized()
            f.write(struct.pack('<12fH',*n,*p[0],*p[1],*p[2],0))

# Plateaux K1 Max (surface utile avec CFS : 300 x 295 x 300 mm) : 12 fichiers 3MF. Chaque
# plateau regroupe les pieces qui s'impriment ensemble ; elles sont posees a plat, rangees
# a gauche pour laisser la place de la tour de purge du CFS sur les plateaux multicolores.
def orientation_matrix(group,o=None):
    orient=o.get('print_orientation',PRINT_INFO[group]) if o is not None else PRINT_INFO[group]
    if orient=='FACE':return Matrix.Rotation(-math.pi/2,4,'X')
    if orient=='AXIS_X':return Matrix.Rotation(math.pi/2,4,'Y')
    if orient in ('REAR','TUNNEL'):return Matrix.Rotation(math.pi/2,4,'X')
    return Matrix.Identity(4)

PLATES=[
 ('00_Eprouvette_jeux','Eprouvette de jeux (a imprimer en premier)',
  [('00_Eprouvette_jeux',None,False)],False),
 ('01_Prototype_mecanique_75mm','Prototype 1:1 : cadre bas et battants de 75 mm',
  [('24_Prototype_cadre_bas',None,False),('25_Prototype_battants_75mm',None,True)],False),
 ('02_Battant_gauche','Battant gauche : demi-coque avant, demi-coque arriere, 2 pions',
  [('02_Battant_gauche_AV',None,False),('14_Battant_gauche_AR',None,False),
   ('22_Pions_battants',-1,True)],False),
 ('03_Battant_droit','Battant droit : demi-coque avant, demi-coque arriere, 2 pions',
  [('03_Battant_droit_AV',None,False),('15_Battant_droit_AR',None,False),
   ('22_Pions_battants',1,True)],False),
 ('04_Facade_avant','Facade avant avec enseigne POLICE BOX',
  [('01_Cadre',None,False)],False,True),
 ('05_Facade_arriere','Facade arriere avec enseigne',
  [('06_Facade_arriere',None,False)],False,True),
 ('06_Tunnel','Tunnel',[('05_Tunnel',None,False)],False),
 ('07_Petites_pieces_bleu','Petites pieces bleues : 8 caches, verrou central, berceau ESP, 8 cales, 2 bases et 2 cages de lanterne',
  [('07_Caches_vis',None,True),('16_Caches_vis_AR',None,True),('12_Verrou_central',None,True),
   ('26_Berceau_ESP',None,True),('28_Cales_aimants',None,True),
   ('08_Base_lanterne',None,True),('18_Base_lanterne_AR',None,True),
   ('10_Cage_lanterne',None,True),('20_Cage_lanterne_AR',None,True)],False),
 ('08_Diffuseurs_ivoire','Deux diffuseurs de lanterne',
  [('09_Diffuseur',None,True),('19_Diffuseur_AR',None,True)],False),
 ('09_Butees_TPU','Quatre butees souples (TPU, bobine externe)',
  [('23_Butees_TPU',None,True)],True),
 ('10_Cames_reglables','Cames rapportees : 2 x 3,5 / 4,5 / 5,5 mm, couches de 0,1 mm',
  [('29_Cames_rapportees',None,True)],False),
 ('11_Gabarit_porte','Gabarit de decoupe et de percage de la porte',
  [('27_Gabarit_porte',None,False)],False),
]

def make_items(spec,turn=False):
    items=[]
    for group,side,split in spec:
        objects=[o for o in GROUPS[group] if side is None or o.get('moving_side')==side]
        for chunk in ([[o] for o in objects] if split else [objects]):
            rotation=orientation_matrix(group,chunk[0])
            if turn:rotation=Matrix.Rotation(math.pi/2,4,'Z')@rotation
            vs=[rotation@(o.matrix_world@v.co) for o in chunk for v in o.data.vertices]
            lo=Vector(tuple(min(v[k] for v in vs) for k in range(3)))
            hi=Vector(tuple(max(v[k] for v in vs) for k in range(3)))
            items.append(dict(label=chunk[0].name if split else group,objects=chunk,
                              rotation=rotation,lo=lo,size=hi-lo))
    return items

BRIM=5.
def has_brim(it):
    # Petites pieces ou pieces plus hautes que larges : bordure pour qu'elles ne se
    # decrochent pas du plateau (pions, cames, cales, verrou, diffuseurs, cages...).
    sx,sy,sz=it['size']
    return it.get('label')!='assemblage' and (min(sx,sy)<15 or sz>min(sx,sy))

def pack(items,x_limit):
    # Rangees successives a gauche, de la piece la plus haute a la plus basse. Chaque piece
    # garde une marge (demi-ecart, ou bordure + 1,5 mm) : deux bordures ne se touchent pas.
    margin=lambda it:BRIM+1.5 if has_brim(it) else P['part_gap']/2
    x0=P['bed_margin']-P['part_gap']/2;x=x0;y=x0;row=y
    for it in sorted(items,key=lambda i:-i['size'].y):
        m=margin(it)
        if x>x0 and x+m+it['size'].x>x_limit:
            x=x0;y=row
        it['place']=(x+m,y+m);x+=it['size'].x+2*m;row=max(row,y+it['size'].y+2*m)
    return row

CORE='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',CORE)
def tag(n):return '{'+CORE+'}'+n
def xml(e):return ET.tostring(e,encoding='utf-8',xml_declaration=True)
def meta(node,key,value):ET.SubElement(node,'metadata',key=key,value=str(value))

def support_boxes(o):
    # Volumes de support qui touchent la piece (le prototype de cadre est coupe a 65 mm).
    c=list(o.get('support_boxes',[]));z=[(o.matrix_world@v.co).z for v in o.data.vertices]
    return [c[i:i+6] for i in range(0,len(c),6) if c[i+2]<max(z) and c[i+5]>min(z)]

def box_mesh(b,transform):
    vs=[transform@Vector((x,y,z)) for x in (b[0],b[3]) for y in (b[1],b[4]) for z in (b[2],b[5])]
    if transform.to_3x3().determinant()<0:raise RuntimeError('transformation miroir')
    ts=[(0,1,3),(0,3,2),(4,6,7),(4,7,5),(0,4,5),(0,5,1),(2,3,7),(2,7,6),(0,2,6),(0,6,4),(1,5,7),(1,7,3)]
    return vs,ts

def write_3mf(name,title,items,path,tpu=False):
    model=ET.Element(tag('model'),unit='millimeter',attrib={
        '{http://www.w3.org/XML/1998/namespace}lang':'fr-FR',
        'xmlns:BambuStudio':'http://schemas.bambulab.com/package/2021'})
    ET.SubElement(model,tag('metadata'),name='Application').text='TARDIS Parametric Generator V8'
    ET.SubElement(model,tag('metadata'),name='Title').text=title
    ET.SubElement(model,tag('metadata'),name='BambuStudio:3mfVersion').text='1'
    resources=ET.SubElement(model,tag('resources'))
    bases=ET.SubElement(resources,tag('basematerials'),id='1')
    for cname,c in COLORS:ET.SubElement(bases,tag('base'),name=cname,displaycolor=c+'FF')
    config=ET.Element('config')
    total=sum(len(it['objects'])+sum(len(support_boxes(o)) for o in it['objects']) for it in items)
    next_mesh=2;next_parent=total+2;parents=[]
    xs=[];ys=[];zs=[];filaments=set()
    for it in items:
        px,py=it['place']
        transform=Matrix.Translation((px-it['lo'].x,py-it['lo'].y,-it['lo'].z))@it['rotation']
        ids=[]
        for o in it['objects']:
            vs,ts=mesh_data(o,transform);filaments.add(o['filament'])
            obj=ET.SubElement(resources,tag('object'),id=str(next_mesh),type='model',name=o.name,
                              pid='1',pindex=str(o['filament']-1))
            mesh=ET.SubElement(obj,tag('mesh'));vertices=ET.SubElement(mesh,tag('vertices'))
            for v in vs:ET.SubElement(vertices,tag('vertex'),x=f'{v.x:.6f}',y=f'{v.y:.6f}',z=f'{v.z:.6f}')
            triangles=ET.SubElement(mesh,tag('triangles'))
            for a,b,c in ts:ET.SubElement(triangles,tag('triangle'),v1=str(a),v2=str(b),v3=str(c))
            xs+= [v.x for v in vs];ys+= [v.y for v in vs];zs+= [v.z for v in vs]
            ids.append((next_mesh,o));next_mesh+=1
        enforcers=[]
        for o in it['objects']:
            for b in support_boxes(o):
                vs,ts=box_mesh(b,transform)
                obj=ET.SubElement(resources,tag('object'),id=str(next_mesh),type='model',name='support '+o.name)
                mesh=ET.SubElement(obj,tag('mesh'));vertices=ET.SubElement(mesh,tag('vertices'))
                for v in vs:ET.SubElement(vertices,tag('vertex'),x=f'{v.x:.6f}',y=f'{v.y:.6f}',z=f'{v.z:.6f}')
                triangles=ET.SubElement(mesh,tag('triangles'))
                for a,b2,c in ts:ET.SubElement(triangles,tag('triangle'),v1=str(a),v2=str(b2),v3=str(c))
                enforcers.append(next_mesh);next_mesh+=1
        pid=next_parent;next_parent+=1;parents.append(pid)
        parent=ET.SubElement(resources,tag('object'),id=str(pid),type='model',name=it['label'])
        comp=ET.SubElement(parent,tag('components'))
        for mid in [m for m,_ in ids]+enforcers:ET.SubElement(comp,tag('component'),objectid=str(mid))
        conf=ET.SubElement(config,'object',id=str(pid));meta(conf,'name',it['label'])
        slots={o['filament'] for _,o in ids}
        meta(conf,'extruder',next(iter(slots)) if len(slots)==1 else 1)
        for key in ('layer_height','wall_loops','sparse_infill_density'):
            if it['objects'][0].get(key):meta(conf,key,it['objects'][0][key])
        if has_brim(it):
            meta(conf,'brim_type','outer_only');meta(conf,'brim_width',f'{BRIM:g}')
        if enforcers:
            # Supports manuels : uniquement dans les volumes ci-dessous, rien ailleurs.
            meta(conf,'enable_support',1);meta(conf,'support_type','normal(manual)')
        for mid,o in ids:
            part=ET.SubElement(conf,'part',id=str(mid),subtype='normal_part')
            meta(part,'name',o.name);meta(part,'extruder',o['filament'])
            meta(part,'matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
        for mid in enforcers:
            part=ET.SubElement(conf,'part',id=str(mid),subtype='support_enforcer')
            meta(part,'name','support fourreau');meta(part,'matrix','1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1')
    build=ET.SubElement(model,tag('build'))
    plate=ET.SubElement(config,'plate');meta(plate,'plater_id',1);meta(plate,'plater_name',name)
    for pid in parents:
        ET.SubElement(build,tag('item'),objectid=str(pid))
        inst=ET.SubElement(plate,'model_instance');meta(inst,'object_id',pid)
        meta(inst,'instance_id',0);meta(inst,'identify_id',pid)
    content=b'''<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/><Default Extension="config" ContentType="application/octet-stream"/></Types>'''
    rels=b'''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'''
    # Pas de profil machine ou thermique invente : conserver celui de l'utilisateur.
    filament_types=['PLA']*4
    if tpu:filament_types[0]='TPU'
    settings={'filament_colour':[c for n,c in COLORS],
              'filament_type':filament_types,'filament_diameter':['1.75']*4,
              'filament_is_support':['0']*4}  # requis par Creality Print et OrcaSlicer en ligne de commande
    # Sans position, Creality Print centre la tour en haut du plateau, sur les facades.
    if len(filaments)>1:
        settings['wipe_tower_x']=[f"{P['tower_x']:g}"];settings['wipe_tower_y']=[f"{P['tower_y']:g}"]
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',content);z.writestr('_rels/.rels',rels)
        z.writestr('3D/3dmodel.model',xml(model))
        z.writestr('Metadata/model_settings.config',xml(config))
        z.writestr('Metadata/project_settings.config',json.dumps(settings))
    return dict(extent_xy=[round(max(xs),2),round(max(ys),2)],height=round(max(zs),2),
                min_xy=[round(min(xs),2),round(min(ys),2)],filaments=sorted(filaments),
                parts=total,items=len(items))

stats=[]
for group,objects in GROUPS.items():
    for o in objects:
        bm=bmesh.new();bm.from_mesh(o.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00005)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.00001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(o.data);bm.free();o.data.update()
        stats.append(mesh_stats(o));write_stl(o,ROOT/'stl'/(o.name+'.stl'))
used={g for _,_,spec,*_ in PLATES for g,_,_ in spec}
orphans=sorted(set(GROUPS)-used)
if orphans:raise RuntimeError('Groupes absents des plateaux : '+', '.join(orphans))
for old in (ROOT/'3mf').glob('*.3mf'):old.unlink()
plates=[]
for name,title,spec,tpu,*opt in PLATES:
    turn=bool(opt and opt[0])
    items=make_items(spec,turn)
    multicolor=len({o['filament'] for it in items for o in it['objects']})>1
    # Les plateaux multicolores laissent libre la bande de la tour de purge (haut du plateau).
    x_limit=P['bed_width']-P['bed_margin']
    y_limit=P['tower_y']-P['tower_brim']-1 if multicolor else P['bed_depth']-P['bed_margin']
    y_end=pack(items,x_limit)
    info=write_3mf(name,title,items,ROOT/'3mf'/(name+'.3mf'),tpu)
    fits=(info['extent_xy'][0]<=x_limit+1e-6 and info['extent_xy'][1]<=y_limit+1e-6
          and info['height']<=300.)
    plates.append(dict(file=name+'.3mf',title=title,multicolor=multicolor,tpu=tpu,
                       bed_fit=fits,x_limit=x_limit,y_limit=y_limit,rotated_90=turn,**info))
# Un fichier en coordonnees d'assemblage pour reference, hors mise en plateau.
assembly=[o for objects in GROUPS.values() for o in objects if not o.get('sample_only')]
write_3mf('assemblage_couleur_reference','Assemblage de reference V8',
          [dict(label='assemblage',objects=assembly,rotation=Matrix.Identity(4),
                lo=Vector((0,0,0)),size=Vector((0,0,0)),place=(0,0))],
          ROOT/'assemblage_couleur_reference.3mf')
# Controle de l'enveloppe : pour chaque came et chaque angle, le battant souleve de
# r*|phi|/90 reste au-dessus de la came (jeu >= cam_gap) et la touche (jeu = cam_gap).
def wrap(a):return (a+180)%360-180
envelope=[]
for r in P['cam_rises']:
    worst,contact=1e9,1e9
    for k in range(0,171):
        phi=k*.5;lift_r=r*phi/90
        gaps=[leaf_profile(wrap(th*.5-phi))+lift_r-insert_profile(r)(th*.5) for th in range(-360,361)]
        worst=min(worst,min(gaps));contact=min(contact,max(0,min(gaps)-P['cam_gap']))
    envelope.append(dict(rise_mm=r,min_gap_mm=round(worst,4),touches=abs(worst-P['cam_gap'])<1e-6,
                         lift_at_stop_mm=round(r*P['stop_angle']/90,2)))
if not all(e['touches'] for e in envelope):raise RuntimeError('Enveloppe de came incorrecte')
# Les 3MF deviennent tout de suite des projets Creality Print complets (imprimante,
# profil, tour de purge a sa place) : jamais de fichier « geometrie seule » sur le disque.
sys.path.insert(0,str(ROOT.parent/'scripts'))
import exporter_projets_creality as cp
for f in sorted((ROOT/'3mf').glob('*.3mf'))+[ROOT/'assemblage_couleur_reference.3mf']:
    cp.convert(str(f))
report=dict(parameters=P,palette=[dict(slot=i+1,name=n,hex=c) for i,(n,c) in enumerate(COLORS)],
            parts=stats,plates=plates,cam_envelope=envelope)
(ROOT/'verification.json').write_text(json.dumps(report,indent=2))
for o in [o for objects in GROUPS.values() for o in objects]:
    bm=bmesh.new();bm.from_mesh(o.data)
    for e in [e for e in bm.edges if not e.is_manifold][:6]:
        print('ARETE_OUVERTE',o.name,[tuple(round(c,2) for c in v.co) for v in e.verts],len(e.link_faces))
    bm.free()
if any(s['non_manifold_edges'] for s in stats):raise RuntimeError('Maillage ouvert dans verification.json')
if any(not p['bed_fit'] for p in plates):raise RuntimeError('Un plateau depasse la surface utile')

def render_preview():
    if '--no-render' not in sys.argv:
        bpy.ops.render.render(write_still=True)

# Mise en scene neutre : couleur reelle des maillages, sans texture peinte fictive.
scene.render.engine='CYCLES';scene.cycles.samples=48
scene.world.use_nodes=True
world_bg=next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND')
world_bg.inputs[0].default_value=(.13,.16,.21,1);world_bg.inputs[1].default_value=.35
for loc,power,size in [((-300,-450,480),3500000,330),((300,-180,350),2300000,250),
                       ((0,180,420),4000000,200)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object
    o.data.energy=power;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(Vector((0,0,135))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(300,-760,350));cam=bpy.context.object
cam.rotation_euler=(Vector((0,0,145))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=370;scene.camera=cam
scene.render.resolution_x=1500;scene.render.resolution_y=1600;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.render.filepath=str(ROOT/'01_vue_fermee.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'tardis_v8.blend'))
render_preview()
front_camera=cam.matrix_world.copy()
cam.location=(-300,D+760,350)
cam.rotation_euler=(Vector((0,D,145))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(ROOT/'03_vue_arriere_fermee.png');render_preview()
cam.matrix_world=front_camera
for side in (-1,1):
    for o in bpy.data.objects:
        if o.get('moving_side',0)!=side:continue
        pivot=Vector((side*A,-5,0))
        # Ouvert, le battant est souleve par sa came de rappel.
        o.matrix_world=Matrix.Translation((0,0,P['cam_rise']*P['preview_angle']/90))@Matrix.Translation(pivot)@Matrix.Rotation(math.radians(side*P['preview_angle']),4,'Z')@Matrix.Translation(-pivot)@o.matrix_world
scene.render.filepath=str(ROOT/'02_vue_ouverte.png');render_preview()
print('V8_GENEREE',len(stats),'volumes',len(plates),'plateaux 3MF')
