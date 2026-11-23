"""Schema electrique de l'eclairage RGB et du capteur de passage (V8).

    .venv/bin/python scripts/schema_eclairage.py tardis_v8

ESP32-C3 SuperMini alimente par USB-C, deux LED WS2812B 5 mm (lanternes avant et
arriere), une resistance de 330 ohms sur chaque ligne de donnees cote ESP et un
condensateur de 100 nF au pied de chaque LED. Ecrit <version>/images/schema_eclairage.png.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BG, INK, MUTED = (250, 248, 244), (30, 34, 40), (110, 110, 110)
BLUE, RED, BLACK, DATA, DATA2 = (18, 58, 99), (200, 40, 30), (25, 25, 25), (235, 120, 10), (150, 60, 170)
W, H = 1500, 960
im = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(im)
f_title, f_big, f, f_small = (ImageFont.truetype(BOLD, 30), ImageFont.truetype(BOLD, 22),
                              ImageFont.truetype(FONT, 19), ImageFont.truetype(FONT, 16))

d.text((40, 26), 'Éclairage RGB et capteur de passage de la V8 : schéma de câblage', font=f_title, fill=BLUE)
d.text((40, 70), 'Tout se soude sur l\'ESP, sauf les condensateurs, soudés sur les pattes de chaque LED.',
       font=f, fill=MUTED)

# ESP32-C3 SuperMini et son USB-C.
ex0, ey0, ex1, ey1 = 250, 220, 470, 715
d.rounded_rectangle((ex0, ey0, ex1, ey1), 14, fill=(30, 110, 60), outline=INK, width=3)
d.text(((ex0 + ex1) / 2, ey0 + 40), 'ESP32-C3', font=f_big, fill='white', anchor='mm')
d.text(((ex0 + ex1) / 2, ey0 + 68), 'SuperMini', font=f, fill='white', anchor='mm')
d.text(((ex0 + ex1) / 2, ey1 - 30), 'dans le berceau', font=f_small, fill=(220, 240, 225), anchor='mm')
d.rounded_rectangle((ex0 - 46, 400, ex0, 460), 6, fill=(180, 184, 190), outline=INK, width=2)
d.line((60, 430, ex0 - 46, 430), fill=BLACK, width=8)
d.text((60, 470), 'Câble USB-C', font=f_big, fill=INK)
d.text((60, 498), 'chargeur 5 V, 1 A', font=f, fill=MUTED)
d.text((60, 522), 'fenêtre au bas de la', font=f, fill=MUTED)
d.text((60, 546), 'façade arrière', font=f, fill=MUTED)
pins = {'5V': 280, 'GND': 340, 'GPIO 3': 470, 'GPIO 4': 560}
pins['GPIO 5'] = 640
for name, y in pins.items():
    d.ellipse((ex1 - 9, y - 9, ex1 + 9, y + 9), fill=(230, 200, 120), outline=INK, width=2)
    d.text((ex1 - 18, y), name, font=f_big, fill='white', anchor='rm')


def resistor(x, y, color):
    d.line((x - 70, y, x - 30, y), fill=color, width=5); d.line((x + 30, y, x + 70, y), fill=color, width=5)
    d.rectangle((x - 30, y - 12, x + 30, y + 12), fill=(225, 205, 160), outline=INK, width=2)
    for k in (-14, 0, 14):
        d.line((x + k, y - 12, x + k, y + 12), fill=(120, 70, 30), width=3)
    d.text((x, y - 22), '330 Ω', font=f_small, fill=INK, anchor='mb')


def led(x0, y0, title, sub, data_color):
    # LED 5 mm vue de face : DIN, 5 V, GND, DOUT ; condensateur entre 5 V et GND.
    d.rounded_rectangle((x0, y0, x0 + 300, y0 + 190), 14, fill=(255, 255, 255), outline=INK, width=3)
    d.text((x0 + 150, y0 + 24), title, font=f_big, fill=BLUE, anchor='mm')
    d.text((x0 + 150, y0 + 50), sub, font=f_small, fill=MUTED, anchor='mm')
    d.ellipse((x0 + 222, y0 + 70, x0 + 288, y0 + 136), fill=(240, 240, 255), outline=INK, width=2)
    for k, c in enumerate(((255, 60, 60), (60, 200, 80), (60, 110, 255))):
        d.ellipse((x0 + 236 + k * 13, y0 + 98, x0 + 246 + k * 13, y0 + 108), fill=c)
    legs = {'DIN': y0 + 80, '5V': y0 + 108, 'GND': y0 + 136, 'DOUT': y0 + 164}
    for name, y in legs.items():
        d.line((x0, y, x0 + 118, y), fill=INK, width=2)
        d.text((x0 + 124, y), name + (' : libre' if name == 'DOUT' else ''), font=f_small, fill=INK, anchor='lm')
    # Condensateur 100 nF entre 5 V et GND, au pied de la LED.
    cx = x0 + 40
    d.line((cx, legs['5V'], cx, legs['5V'] + 8), fill=INK, width=2)
    d.line((cx - 10, legs['5V'] + 8, cx + 10, legs['5V'] + 8), fill=INK, width=3)
    d.line((cx - 10, legs['5V'] + 14, cx + 10, legs['5V'] + 14), fill=INK, width=3)
    d.line((cx, legs['5V'] + 14, cx, legs['GND']), fill=INK, width=2)
    d.text((cx + 12, legs['5V'] + 11), '100 nF', font=f_small, fill=INK, anchor='lm')
    return legs


front = led(1120, 150, 'Lanterne avant', 'WS2812B 5 mm', DATA)
rear = led(1120, 500, 'Lanterne arrière', 'WS2812B 5 mm', DATA2)


def route(points, color, width=5):
    d.line(points, fill=color, width=width, joint='curve')


# Bus 5 V et masse vers les deux LED (cable 3 conducteurs par lanterne).
bx5, bxg = 760, 800
route([(ex1 + 9, pins['5V']), (bx5, pins['5V'])], RED)
route([(bx5, front['5V']), (bx5, rear['5V'])], RED)
route([(ex1 + 9, pins['GND']), (bxg, pins['GND'])], BLACK)
route([(bxg, front['GND']), (bxg, rear['GND'])], BLACK)
for legs in (front, rear):
    route([(bx5, legs['5V']), (1120, legs['5V'])], RED)
    route([(bxg, legs['GND']), (1120, legs['GND'])], BLACK)
    for x, y in ((bx5, legs['5V']), (bxg, legs['GND'])):
        d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=INK)
for x, y in ((bx5, pins['5V']), (bxg, pins['GND'])):
    d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=INK)
# Donnees : resistance cote ESP, puis cable dans la rainure.
resistor(590, pins['GPIO 3'], DATA)
route([(ex1 + 9, pins['GPIO 3']), (520, pins['GPIO 3'])], DATA)
route([(660, pins['GPIO 3']), (720, pins['GPIO 3']), (720, front['DIN']), (1120, front['DIN'])], DATA)
resistor(590, pins['GPIO 4'], DATA2)
route([(ex1 + 9, pins['GPIO 4']), (520, pins['GPIO 4'])], DATA2)
route([(660, pins['GPIO 4']), (700, pins['GPIO 4']), (700, rear['DIN']), (1120, rear['DIN'])], DATA2)

d.rounded_rectangle((850, 372, 1095, 452), 10, fill=(255, 244, 230), outline=(220, 170, 120), width=2)
d.text((972, 396), 'environ 60 cm par lanterne', font=f_small, fill=INK, anchor='mm')
d.text((972, 424), 'dans la rainure de la façade', font=f_small, fill=INK, anchor='mm')

GREEN = (30, 150, 70)
# Capteur de passage : deux ILS en serie entre GPIO 5 (rappel interne au 3,3 V) et la masse.
def reed(x, y, label):
    d.rounded_rectangle((x, y - 16, x + 90, y + 16), 14, fill=(225, 242, 246), outline=INK, width=2)
    d.line((x - 10, y, x + 38, y), fill=GREEN, width=4); d.line((x + 52, y - 6, x + 100, y), fill=GREEN, width=4)
    d.text((x + 45, y - 24), label, font=f_small, fill=INK, anchor='mb')
y5 = 760
route([(ex1 + 9, pins['GPIO 5']), (530, pins['GPIO 5']), (530, y5), (550, y5)], GREEN)
reed(560, y5, 'ILS gauche'); route([(660, y5), (670, y5)], GREEN)
reed(680, y5, 'ILS droit'); route([(780, y5), (bxg, y5), (bxg, rear['GND'])], GREEN)
d.ellipse((bxg - 6, rear['GND'] - 6, bxg + 6, rear['GND'] + 6), fill=INK)
d.rounded_rectangle((900, 735, 1420, 790), 10, fill=(234, 247, 238), outline=(120, 190, 140), width=2)
d.text((1160, 762), 'dans le linteau, fermés par les aimants des battants', font=f_small, fill=INK, anchor='mm')

y = 840
d.line((40, y - 20, W - 40, y - 20), fill=(215, 210, 200), width=2)
legend = [(RED, '5 V'), (BLACK, 'masse'), (DATA, 'données avant (GPIO 3)'), (DATA2, 'données arrière (GPIO 4)')]
legend.append((GREEN, 'capteur (GPIO 5)'))
for i, (color, text) in enumerate(legend):
    x = 40 + i * 285
    d.line((x, y + 12, x + 46, y + 12), fill=color, width=6)
    d.text((x + 58, y + 12), text, font=f, fill=INK, anchor='lm')
d.text((40, y + 50), 'Brochage de la LED : se fier au schéma du vendeur (l\'ordre des pattes varie selon le modèle).',
       font=f, fill=MUTED)
d.text((40, y + 80), 'Si une lanterne scintille : intercaler un 74AHCT125 alimenté en 5 V entre chaque GPIO et sa résistance.',
       font=f, fill=MUTED)
for version in sys.argv[1:]:
    im.save(f'{version}/images/schema_eclairage.png', optimize=True)
    print(version, '->', f'{version}/images/schema_eclairage.png')
