"""Assemble les deux rendus de la came de rappel avec leurs legendes.

    .venv/bin/python scripts/planche_came.py tardis_v8

Lit <version>/images/came_rappel_ferme.png et _ouvert.png (scripts/render_came.py)
et ecrit <version>/images/came_rappel.jpg.
"""
import json, sys
from PIL import Image, ImageDraw, ImageFont

BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
for version in sys.argv[1:]:
    P = json.load(open(f'{version}/verification.json'))['parameters']
    lift60 = P['cam_rise'] * 60 / 90
    shots = [Image.open(f'{version}/images/came_rappel_{n}.png').convert('RGB') for n in ('ferme', 'ouvert')]
    w, h = shots[0].size
    sheet = Image.new('RGB', (2 * w, h + 150), (250, 248, 244)); d = ImageDraw.Draw(sheet)
    big, small = ImageFont.truetype(BOLD, 26), ImageFont.truetype(FONT, 19)
    came = 'de la came rapportée (bleu), clée en D.' if 'cam_rises' in P else 'de la came du cadre (bleu).'
    texts = [('Fermé · 0°', 'La dent du battant (ivoire) repose au creux', came),
             (f'Ouvert · 60° · + {lift60:.1f} mm'.replace('.', ','), 'La dent monte sur la rampe : le battant se soulève.',
              'Lâché, son poids le fait redescendre au centre.')]
    for i, (img, (title, l1, l2)) in enumerate(zip(shots, texts)):
        sheet.paste(img, (i * w, 0))
        d.text((i * w + 24, h + 18), title, font=big, fill=(18, 58, 99))
        d.text((i * w + 24, h + 62), l1, font=small, fill=(40, 40, 40))
        d.text((i * w + 24, h + 90), l2, font=small, fill=(40, 40, 40))
    d.line((w, 20, w, h - 20), fill=(205, 200, 190), width=2)
    sheet.save(f'{version}/images/came_rappel.jpg', quality=88)
    print(version, '->', f'{version}/images/came_rappel.jpg')
