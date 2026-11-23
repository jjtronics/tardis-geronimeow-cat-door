"""Planche d'ensemble des plateaux d'une version, a partir des vignettes Blender.

    .venv/bin/python scripts/planche_plateaux.py tardis_v8

Lit <version>/images/plateaux/*.jpg et <version>/controle_tranchage.json (temps,
masse, changements de couleur) et ecrit <version>/images/plateaux.jpg.
"""
import glob, json, os, re, sys
from PIL import Image, ImageDraw, ImageFont

FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
COLS, W, H, PAD, LABEL = 4, 420, 315, 18, 62

for version in sys.argv[1:]:
    shots = sorted(glob.glob(f'{version}/images/plateaux/*.jpg'))
    report = {p['plate']: p for p in json.load(open(f'{version}/controle_tranchage.json'))['plates']}
    rows = (len(shots) + COLS - 1) // COLS
    sheet = Image.new('RGB', (COLS * (W + PAD) + PAD, rows * (H + LABEL + PAD) + PAD), (250, 248, 244))
    draw = ImageDraw.Draw(sheet)
    big, small = ImageFont.truetype(BOLD, 19), ImageFont.truetype(FONT, 16)
    for i, shot in enumerate(shots):
        name = os.path.basename(shot)[:-4]
        x, y = PAD + (i % COLS) * (W + PAD), PAD + (i // COLS) * (H + LABEL + PAD)
        sheet.paste(Image.open(shot).resize((W, H), Image.LANCZOS), (x, y))
        draw.rectangle((x, y, x + W - 1, y + H - 1), outline=(205, 200, 190))
        draw.text((x + 2, y + H + 6), name.replace('_', ' '), font=big, fill=(18, 58, 99))
        p = report.get(name)
        if p:
            colours = len(p['slots_used'])
            h, m = (int(v.group(1)) if v else 0 for v in (re.search(r'(\d+)h', p['time']), re.search(r'(\d+)m', p['time'])))
            duree = f'{h} h {m:02d}' if h else f'{m} min' if m else '< 1 min'
            masse = f"{p['grams']:.0f} g" if p['grams'] >= 1 else '< 1 g'
            info = f"{duree} · {masse} · {colours} couleur{'s' if colours > 1 else ''}"
            if p['color_changes']:
                info += f" · {p['color_changes']} changement{'s' if p['color_changes'] > 1 else ''}"
            draw.text((x + 2, y + H + 32), info, font=small, fill=(80, 80, 80))
    sheet.save(f'{version}/images/plateaux.jpg', quality=86)
    print(version, len(shots), 'plateaux ->', f'{version}/images/plateaux.jpg')
