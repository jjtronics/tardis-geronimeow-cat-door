"""Figure cotee du gabarit de decoupe de la porte (V8).

    .venv/bin/python scripts/figure_gabarit.py tardis_v8

Lit les parametres de <version>/verification.json et ecrit <version>/images/gabarit_porte.png :
trait de scie (tunnel + jeu, encoche de l'ESP), quatre percages M4 et cotes utiles.
"""
import json, sys
from PIL import Image, ImageDraw, ImageFont

BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BG, INK, BLUE, CUT, MUTED = (250, 248, 244), (30, 34, 40), (18, 58, 99), (200, 50, 30), (110, 110, 110)
for v in sys.argv[1:]:
    P = json.load(open(f'{v}/verification.json'))['parameters']
    W, H, t, cl = P['opening_width'], P['opening_height'], P['tunnel_wall'], P['door_cut_clearance']
    nw, nh = P['esp_notch']
    cx, z0, z1 = W / 2 + t + cl, -t - cl, H + t + cl
    k = 2.6; ox, oy = 117 * k + 190, 150          # px/mm, origine x = 0, haut de la figure
    top = z1 + 12
    def X(x): return ox + x * k
    def Y(z): return oy + (top - z) * k
    im = Image.new('RGB', (int(X(117) + 330), int(Y(z0 - nh - 13) + 190)), BG); d = ImageDraw.Draw(im)
    f, fb, ft = ImageFont.truetype(FONT, 18), ImageFont.truetype(BOLD, 20), ImageFont.truetype(BOLD, 28)
    d.text((40, 18), 'Gabarit de découpe de la porte · V8 (plateau 11)', font=ft, fill=BLUE)
    # Plaque du gabarit et fenetre (trait de scie).
    d.rectangle((X(-117), Y(top), X(117), Y(z0 - nh - 13)), fill=(205, 218, 232), outline=BLUE, width=3)
    win = [(X(-cx), Y(z1)), (X(cx), Y(z1)), (X(cx), Y(z0)), (X(nw / 2), Y(z0)), (X(nw / 2), Y(z0 - nh)),
           (X(-nw / 2), Y(z0 - nh)), (X(-nw / 2), Y(z0)), (X(-cx), Y(z0))]
    d.polygon(win, fill=BG, outline=CUT, width=4)
    for s in (-1, 1):
        for z in (30, H - 24):
            d.ellipse((X(s * 107) - 6, Y(z) - 6, X(s * 107) + 6, Y(z) + 6), fill=BG, outline=INK, width=3)
    d.line((X(0), Y(top) - 10, X(0), Y(z0 - nh - 13) + 10), fill=MUTED, width=1)

    def dim_h(xa, xb, y, text):
        d.line((X(xa), y, X(xb), y), fill=INK, width=2)
        for x in (xa, xb):
            d.line((X(x), y - 8, X(x), y + 8), fill=INK, width=2)
        d.text(((X(xa) + X(xb)) / 2, y - 6), text, font=fb, fill=INK, anchor='mb')

    def dim_v(za, zb, x, text, left=False):
        d.line((x, Y(za), x, Y(zb)), fill=INK, width=2)
        for z in (za, zb):
            d.line((x - 8, Y(z), x + 8, Y(z)), fill=INK, width=2)
        d.text((x + (-12 if left else 12), (Y(za) + Y(zb)) / 2), text, font=fb, fill=INK,
               anchor='rm' if left else 'lm')

    fmt = lambda v: f'{v:.1f}'.replace('.', ',').replace(',0', '')
    dim_h(-cx, cx, Y(top) - 22, f'{fmt(2 * cx)} mm (tunnel + {fmt(cl)} mm par côté)')
    dim_v(z0, z1, X(117) + 40, f'{fmt(z1 - z0)} mm')
    dim_h(-nw / 2, nw / 2, Y(z0 - nh - 13) + 50, f'encoche ESP {fmt(nw)} mm')
    dim_v(z0 - nh, z0, X(-117) - 40, f'{fmt(nh)} mm', left=True)
    dim_h(-107, 107, Y(H - 24) - 30, f'entraxe des vis {fmt(214)} mm')
    dim_v(30, H - 24, X(117) + 150, f'{fmt(H - 54)} mm entre vis')
    dim_v(z0, 30, X(-117) - 40, f'{fmt(30 - z0)} mm', left=True)
    y = Y(z0 - nh - 13) + 80
    for i, line in enumerate(['Trait rouge : trait de scie (scie sauteuse, avant-trous Ø10 dans les angles, côté chute).',
                              'Cercles : avant-trous Ø3,2 du gabarit, percer ensuite Ø5 à travers la porte (vis M4).',
                              'Le gabarit se pose sur la face extérieure, inscription lisible, « HAUT » en haut.']):
        d.text((40, y + i * 28), line, font=f, fill=INK)
    im.save(f'{v}/images/gabarit_porte.png', optimize=True)
    print(v, '->', f'{v}/images/gabarit_porte.png')
