"""Planches legendees des details de la V8 (scripts/render_details_v8.py).

    .venv/bin/python scripts/planche_details_v8.py tardis_v8

Ecrit <version>/images/cames_reglables.jpg, verrou_central.jpg et aimants_capteur.jpg.
"""
import json, sys
from PIL import Image, ImageDraw, ImageFont

BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BG, BLUE, INK = (250, 248, 244), (18, 58, 99), (40, 40, 40)
big, small = ImageFont.truetype(BOLD, 26), ImageFont.truetype(FONT, 19)


def sheet(panels, out, h=520):
    ims = [Image.open(p).convert('RGB') for p, *_ in panels]
    ims = [i.resize((int(i.width * h / i.height), h), Image.LANCZOS) for i in ims]
    W = sum(i.width for i in ims)
    s = Image.new('RGB', (W, h + 150), BG); d = ImageDraw.Draw(s); x = 0
    for im, (_, title, l1, l2) in zip(ims, panels):
        s.paste(im, (x, 0))
        d.text((x + 22, h + 18), title, font=big, fill=BLUE)
        d.text((x + 22, h + 62), l1, font=small, fill=INK)
        d.text((x + 22, h + 90), l2, font=small, fill=INK)
        if x:
            d.line((x, 20, x, h - 20), fill=(205, 200, 190), width=2)
        x += im.width
    s.save(out, quality=88); print('->', out)


for v in sys.argv[1:]:
    P = json.loads(open(f'{v}/verification.json').read())['parameters']
    r = [f'{x:g}'.replace('.', ',') for x in P['cam_rises']]
    i = f'{v}/images/'
    sheet([(i + 'detail_cames.png', f'Cames {r[0]} · {r[1]} · {r[2]} mm',
            'Une rainure par pente à l\'arrière (1, 2 ou 3). Elles',
            'se posent sur la clé en D du nœud, sans outil.')], i + 'cames_reglables.jpg', 420)
    sheet([(i + 'detail_verrou_libre.png', 'LIBRE · lame en bas',
            'Coupe au milieu des battants : la lame',
            '(10 × 4 mm) reste sous le seuil.'),
           (i + 'detail_verrou_ferme.png', 'FERMÉ · lame montée',
            f'La lame entre de {P["lock_engage"]:g} mm dans les poches',
            'des deux battants : ils sont bloqués.'),
           (i + 'detail_verrou_tourniquet.png', 'Le tourniquet la tient',
            'Bouton monté, tourniquet tourné d\'un quart',
            'de tour dessous ; relevé, la lame retombe.')], i + 'verrou_central.jpg', 360)
    sheet([(i + 'detail_aimants_bas.png', 'Aimants anti-vent',
            'Battant (haut) et seuil (bas) : l\'aimant du seuil',
            'repose sur 0 à 4 cales (rouge) pour régler l\'écart.'),
           (i + 'detail_capteur_haut.png', 'Capteur de passage',
            'L\'aimant du battant ferme l\'ILS (verre) caché dans',
            'le linteau ; le battant s\'ouvre, le contact s\'ouvre.')], i + 'aimants_capteur.jpg', 460)
