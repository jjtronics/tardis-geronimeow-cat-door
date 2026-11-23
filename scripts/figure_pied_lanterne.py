"""Schema cote du pied de lanterne de la V8 : chambre de connexion sous la LED.

    .venv/bin/python scripts/figure_pied_lanterne.py tardis_v8

Deux coupes : de face (plan y = -10, toit en pointe a 45 degres) et de cote (plan
x = 0, ouverture vers la rainure de la facade). Ecrit <version>/images/pied_lanterne.jpg.
Les cotes reprennent generate.py (pied 28 x 20 x 4, disque Ø20, centrage Ø13,2,
logement LED Ø5,4, chambre 9 x 13,5, faite a 5,1 mm).
"""
import sys
from PIL import Image, ImageDraw, ImageFont

BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BG, PART, CUT, INK, BLUE = (250, 248, 244), (54, 84, 120), (205, 215, 228), (30, 34, 40), (18, 58, 99)
LEDC, LEG, CAPC, WIRE, CAV = (235, 238, 245), (150, 155, 160), (200, 150, 70), (230, 110, 20), (250, 248, 244)
K = 17  # px par mm
fb, f, fs = ImageFont.truetype(BOLD, 24), ImageFont.truetype(FONT, 19), ImageFont.truetype(FONT, 16)


def panel(title, draw_fn, w=560, h=520):
    im = Image.new('RGB', (w, h), BG); d = ImageDraw.Draw(im)
    d.text((24, 16), title, font=fb, fill=BLUE)
    draw_fn(d, w, h)
    return im


def front(d, w, h):
    ox, oz = w / 2, h - 120                                   # x = 0, z = LZ (dessus de la corniche)
    X = lambda x: ox + x * K; Z = lambda z: oz - z * K
    d.rectangle((X(-14), Z(0) + 4, X(14), Z(-4)), fill=(120, 130, 145))       # corniche
    d.text((X(-13), Z(-2)), 'façade', font=fs, fill=(240, 240, 240), anchor='lm')
    d.rectangle((X(-14), Z(4), X(14), Z(0)), fill=PART)                      # pied
    d.rectangle((X(-10), Z(7), X(10), Z(3)), fill=PART)                      # disque
    d.rectangle((X(-6.6), Z(9.5), X(6.6), Z(6.5)), fill=PART)                # centrage
    d.polygon([(X(-4.5), Z(0)), (X(-4.5), Z(.6)), (X(0), Z(5.1)), (X(4.5), Z(.6)), (X(4.5), Z(0))], fill=CAV,
              outline=INK)                                                  # chambre
    d.rectangle((X(-2.7), Z(11.5), X(2.7), Z(4)), fill=CAV)                  # logement LED
    d.rounded_rectangle((X(-2.5), Z(11), X(2.5), Z(4.6)), 30, fill=LEDC, outline=INK)
    for x in (-1.9, -.65, .65, 1.9):
        d.line((X(x), Z(4.6), X(x), Z(1.6)), fill=LEG, width=3)
        d.line((X(x), Z(1.6), X(x * 1.6), Z(1.0)), fill=LEG, width=3)
    d.rectangle((X(-1.9) - 2, Z(2.6), X(-.65) + 2, Z(2.2)), fill=CAPC, outline=INK)  # 0805 entre 5 V et GND
    d.line((X(-4.5), Z(-1.2) + 30, X(4.5), Z(-1.2) + 30), fill=INK, width=2)
    d.text((ox, Z(-1.2) + 46), '9 mm', font=f, fill=INK, anchor='mm')
    d.line((X(6.5), Z(0), X(6.5), Z(5.1)), fill=INK, width=2)
    d.text((X(6.5) + 8, Z(2.6)), '5,1 mm', font=fs, fill=INK, anchor='lm')
    d.text((24, 70), 'LED WS2812B dans son logement Ø5,4', font=fs, fill=INK)
    d.text((24, 92), 'condensateur 100 nF soudé entre 5 V et GND', font=fs, fill=CAPC)
    d.text((24, 114), 'toit à 45° : imprimé sans pont ni support', font=fs, fill=INK)


def side(d, w, h):
    oy, oz = w - 70, h - 120                                  # y = 0 (contre la porte) a droite
    Y = lambda y: oy + y * K * .9; Z = lambda z: oz - z * K
    d.rectangle((Y(-20), Z(0) + 4, Y(0), Z(-4)), fill=(120, 130, 145))
    d.rectangle((Y(0), Z(10), Y(0) + 40, Z(-4)), fill=(220, 210, 190))      # porte
    d.text((Y(0) + 20, Z(9)), 'porte', font=fs, fill=INK, anchor='mm')
    d.rectangle((Y(-20), Z(4), Y(0), Z(0)), fill=PART)
    d.rectangle((Y(-20), Z(7), Y(0), Z(3)), fill=PART)
    d.rectangle((Y(-16.6), Z(9.5), Y(-3.4), Z(6.5)), fill=PART)
    d.rectangle((Y(-15), Z(5.1), Y(-1.5), Z(0)), fill=CAV, outline=INK)      # chambre
    d.rectangle((Y(-2.5), Z(3), Y(0), Z(-4)), fill=CAV)                      # rainure (pied + facade)
    d.rectangle((Y(-12.7), Z(11.5), Y(-7.3), Z(4)), fill=CAV)
    d.rounded_rectangle((Y(-12.5), Z(11), Y(-7.5), Z(4.6)), 30, fill=LEDC, outline=INK)
    d.line((Y(-10), Z(4.6), Y(-10), Z(1.4)), fill=LEG, width=3)
    d.line((Y(-10), Z(1.4), Y(-4), Z(1.4)), fill=LEG, width=3)
    d.line((Y(-4), Z(1.4), Y(-1.2), Z(1.4), Y(-1.2), Z(-3.6)), fill=WIRE, width=4)
    d.rectangle((Y(-6.5), Z(1.4) - 6, Y(-4), Z(1.4) + 6), fill=(60, 60, 60))  # gaine thermo
    d.line((Y(-15), Z(-1.2) + 30, Y(-1.5), Z(-1.2) + 30), fill=INK, width=2)
    d.text(((Y(-15) + Y(-1.5)) / 2, Z(-1.2) + 46), '13,5 mm', font=f, fill=INK, anchor='mm')
    d.text((24, 70), 'la chambre débouche dans la rainure', font=fs, fill=INK)
    d.text((24, 92), 'de la façade : les fils descendent', font=fs, fill=INK)
    d.text((24, 114), 'cachés contre la porte', font=fs, fill=WIRE)


for v in sys.argv[1:]:
    a = panel('Coupe de face', front); b = panel('Coupe de côté', side)
    sheet = Image.new('RGB', (a.width + b.width, a.height + 70), BG)
    sheet.paste(a, (0, 0)); sheet.paste(b, (a.width, 0)); d = ImageDraw.Draw(sheet)
    d.line((a.width, 20, a.width, a.height - 20), fill=(205, 200, 190), width=2)
    d.text((24, a.height + 18), 'Pied de lanterne : chambre de connexion sous la LED (pattes coudées, soudures gainées, condensateur).',
           font=f, fill=INK)
    sheet.save(f'{v}/images/pied_lanterne.jpg', quality=90)
    print(v, '->', f'{v}/images/pied_lanterne.jpg')
