"""Assemble les deux figures du cablage RGB avec leurs legendes.

    .venv/bin/python scripts/planche_cablage.py tardis_v8

Lit <version>/images/cablage_dos_facade.png et cablage_berceau.png
(scripts/render_cablage.py) et ecrit <version>/images/cablage_rgb.jpg.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
for version in sys.argv[1:]:
    a = Image.open(f'{version}/images/cablage_dos_facade.png').convert('RGB')
    b = Image.open(f'{version}/images/cablage_berceau.png').convert('RGB')
    h = 760
    a = a.resize((int(a.width * h / a.height), h), Image.LANCZOS)
    sheet = Image.new('RGB', (a.width + b.width, h + 150), (250, 248, 244)); d = ImageDraw.Draw(sheet)
    sheet.paste(a, (0, 0)); sheet.paste(b, (a.width, 0))
    big, small = ImageFont.truetype(BOLD, 26), ImageFont.truetype(FONT, 19)
    import json
    v8 = 'cam_rises' in json.load(open(f'{version}/verification.json'))['parameters']
    texts = [(0, 'Dos de la façade, côté porte',
              'Rainure 4,5 × 2,5 mm : lanterne, haut, jambage, tunnel.' if v8 else
              'Rainure 3 × 2 mm : lanterne, traverse, jambage,',
              'Vert : boucle des deux ILS, sous le linteau.' if v8 else
              'puis sous le tunnel jusqu\'au berceau de l\'ESP.'),
             (a.width, 'Berceau ESP32 sous le tunnel',
              'Orange : lanterne avant · rouge : arrière · vert : ILS.' if v8 else
              'Orange : lanterne avant · rouge : lanterne arrière.',
              'Fiche USB-C côté maison (tunnel et façade arrière masqués).')]
    for x, title, l1, l2 in texts:
        d.text((x + 24, h + 18), title, font=big, fill=(18, 58, 99))
        d.text((x + 24, h + 62), l1, font=small, fill=(40, 40, 40))
        d.text((x + 24, h + 90), l2, font=small, fill=(40, 40, 40))
    d.line((a.width, 20, a.width, h - 20), fill=(205, 200, 190), width=2)
    sheet.save(f'{version}/images/cablage_rgb.jpg', quality=88)
    print(version, '->', f'{version}/images/cablage_rgb.jpg')
