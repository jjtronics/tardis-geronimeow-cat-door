"""Image de couverture du depot (1280 x 640, format apercu GitHub) en anglais et en
francais, a partir du rendu ouvert de la V8.

    .venv/bin/python scripts/couverture.py

Ecrit docs/images/couverture.jpg (anglais) et docs/images/couverture_fr.jpg.
"""
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
REG = '/System/Library/Fonts/Supplemental/Arial.ttf'
BG = (55, 63, 73)
IVORY, GOLD, NAVY = (244, 230, 200), (205, 165, 95), (10, 24, 44)
W, H = 1280, 640
TEXTS = {
    'couverture.jpg': ('Bigger on the inside… for cats.',
                       ['3D-printable double-swing cat door', 'Gravity return · adjustable cams',
                        'One-button lock · RGB lanterns · ESPHome']),
    'couverture_fr.jpg': ('Plus grande à l’intérieur… pour les chats.',
                          ['Chatière double action à imprimer en 3D', 'Rappel par gravité · cames réglables',
                           'Verrou à un bouton · lanternes RGB · ESPHome']),
}


def keyed(path, height):
    """Rendu detoure : le fond uni du rendu devient transparent, bord adouci."""
    im = Image.open(path).convert('RGB')
    px = im.load(); mask = Image.new('L', im.size, 0); m = mask.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = px[x, y]
            d = abs(r - BG[0]) + abs(g - BG[1]) + abs(b - BG[2])
            m[x, y] = 0 if d < 10 else (255 if d > 30 else int((d - 10) * 255 / 20))
    im.putalpha(mask.filter(ImageFilter.GaussianBlur(.8)))
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * height / im.height), height), Image.LANCZOS)


def background():
    bg = Image.new('RGB', (W, H)); d = ImageDraw.Draw(bg)
    for x in range(W):
        k = x / W
        d.line((x, 0, x, H), fill=tuple(int(NAVY[i] * (1 - k) + (28, 44, 70)[i] * k) for i in range(3)))
    rnd = random.Random(42)
    for _ in range(260):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H), rnd.choice((.6, .8, 1, 1.4))
        a = rnd.randint(90, 230)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(a, a, min(255, a + 20)))
    glow = Image.new('L', (W, H), 0); ImageDraw.Draw(glow).ellipse((760, 40, 1240, 640), fill=110)
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    return Image.composite(Image.new('RGB', (W, H), (60, 110, 170)), bg, glow)


opened = keyed('tardis_v8/02_vue_ouverte.png', 580)
POS = (W - opened.width - 40, 34)
for name, (tagline, lines) in TEXTS.items():
    im = background().convert('RGBA')
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    s = Image.new('RGBA', opened.size, (0, 0, 0, 140)); s.putalpha(opened.getchannel('A').point(lambda v: v * 140 // 255))
    shadow.alpha_composite(s, (POS[0] + 14, POS[1] + 16))
    im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))
    im.alpha_composite(opened, POS)
    d = ImageDraw.Draw(im)
    d.text((64, 150), 'TARDIS', font=ImageFont.truetype(BOLD, 92), fill=IVORY)
    d.text((64, 250), 'Geronimeow', font=ImageFont.truetype(BOLD, 72), fill=GOLD)
    d.text((66, 345), tagline, font=ImageFont.truetype(REG, 30), fill=IVORY)
    for i, line in enumerate(lines):
        y = 410 + i * 42
        d.ellipse((68, y + 10, 80, y + 22), fill=GOLD)
        d.text((96, y), line, font=ImageFont.truetype(REG, 26), fill=(215, 222, 232))
    im.convert('RGB').save(f'docs/images/{name}', quality=90)
    print('docs/images/' + name)
