"""Titres, explications et etiquettes sur les images de render_visuals.py, puis
encodage MP4 (H.264) et GIF.

    python3 tardis_v8/visualisations/compose_montage.py [test] [en]

Avec « en », les textes sont traduits en anglais (table EN ci-dessous) et la video
est ecrite en montage_complet_V8_en.mp4 / .gif.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json, subprocess, shutil, sys

OUT = Path(__file__).resolve().parent
TEST = 'test' in sys.argv
EN_MODE = 'en' in sys.argv
SUFFIX = '_en' if EN_MODE else ''
spec = json.loads((OUT / ('montage_test.json' if TEST else 'montage.json')).read_text())
# Anciennes legendes encore presentes dans un montage.json rendu avant le renommage.
RENAME = {'Chatière TARDIS · V8': 'TARDIS Geronimeow',
          'Une chatière double action à imprimer en 3D : rappel par gravité, verrou central, capteur et lanternes RGB.':
          'Une chatière TARDIS double action à imprimer en 3D : rappel par gravité, verrou central, capteur et lanternes RGB.'}
EN = {
    'TARDIS Geronimeow': 'TARDIS Geronimeow',
    'Une chatière TARDIS double action à imprimer en 3D : rappel par gravité, verrou central, capteur et lanternes RGB.':
        'A 3D-printable, double-swing TARDIS cat door: gravity return, central lock, passage sensor and RGB lanterns.',
    'Les pièces': 'The parts',
    'Façade avant, battants, cames, verrou, aimants, capteur, électronique, tunnel et façade arrière.':
        'Front, flaps, cams, lock, magnets, sensor, electronics, tunnel and rear front.',
    'Les cames réglables': 'Adjustable cams',
    'Chaque came s’emboîte sur la clé en D du nœud de charnière. Trois pentes (3,5 · 4,5 · 5,5 mm) règlent la force de rappel.':
        'Each cam slides onto the D-key of the hinge knuckle. Three slopes (3.5 · 4.5 · 5.5 mm) set the return force.',
    'Clé en D : une seule position': 'D-key: one position only',
    'Came 4,5 mm (2 rainures)': '4.5 mm cam (2 grooves)',
    'Les battants et leurs axes': 'Flaps and axles',
    'Chaque battant se pose sur sa came ; les axes acier Ø3 montent par le bas et sont tenus par des clips.':
        'Each flap sits on its cam; the Ø3 steel axles slide in from below and are held by clips.',
    'Axe Ø3 × 39,4 mm': 'Ø3 × 39.4 mm axle',
    'Battant : deux demi-coques collées': 'Flap: two glued half-shells',
    'Aimants anti-vent': 'Wind-proof magnets',
    'Un aimant sous le battant, un dans le seuil, posé sur des cales de 1 mm : plus de cales, maintien plus fort.':
        'One magnet under the flap, one in the sill on 1 mm shims: more shims, stronger hold.',
    'Aimant Ø6 × 2 du battant': 'Ø6 × 2 flap magnet',
    'Aimant du seuil': 'Sill magnet',
    'Cale de 1 mm (réglage)': '1 mm shim (adjustment)',
    'Capteur de passage': 'Passage sensor',
    'Un aimant en haut du battant ferme un ILS caché dans le linteau. Le battant s’ouvre : le contact s’ouvre, le passage est compté.':
        'A magnet at the top of the flap closes a reed switch hidden in the lintel. The flap opens, the contact opens, the passage is counted.',
    'ILS (ampoule de verre) dans le linteau': 'Reed switch (glass) in the lintel',
    'Aimant Ø6 × 3 du battant': 'Ø6 × 3 flap magnet',
    'Les lanternes': 'The lanterns',
    'Socle, diffuseur ivoire, cage-chapeau : une LED RGB WS2812B se loge dans le socle.':
        'Base, ivory diffuser, cage and roof: a WS2812B RGB LED sits in the base.',
    'Câbles dans les façades': 'Wires inside the fronts',
    'Au dos de la façade, une rainure invisible mène les câbles de la lanterne et du capteur jusque sous le tunnel.':
        'A hidden groove on the back of the front routes the lantern and sensor wires down under the tunnel.',
    'Câble de la lanterne': 'Lantern wire',
    'Câble du capteur': 'Sensor wire',
    'Berceau de l’ESP32': 'ESP32 cradle',
    'L’ESP32 se cache sous le tunnel, dans une encoche de la porte ; la prise USB-C est côté maison.':
        'The ESP32 hides under the tunnel, in a notch of the door; the USB-C socket faces indoors.',
    'Berceau ESP32': 'ESP32 cradle',
    'Prise USB-C (côté maison)': 'USB-C socket (indoor side)',
    'Câbles des façades': 'Wires from the fronts',
    'Tunnel, porte et façade arrière': 'Tunnel, door and rear front',
    'Le tunnel traverse la porte découpée au gabarit ; la façade arrière vient en face.':
        'The tunnel goes through the door, cut with the template; the rear front closes it on the other side.',
    'Vis, caches et butées': 'Screws, caps and stops',
    'Quatre vis M4 traversantes, huit caches, et quatre butées TPU qui amortissent les battants à 85°.':
        'Four through M4 screws, eight caps, and four TPU stops that cushion the flaps at 85°.',
    'Verrou central : FERMÉ': 'Central lock: LOCKED',
    'On monte le bouton et on tourne le tourniquet dessous : la lame entre dans les deux battants, ils sont bloqués.':
        'Lift the knob and turn the latch under it: the blade enters both flaps and locks them.',
    'Bouton': 'Knob',
    'Tourniquet': 'Turn latch',
    'Lame dans les deux battants': 'Blade inside both flaps',
    'Verrou central : LIBRE': 'Central lock: FREE',
    'Tourniquet relevé, la lame retombe sous le seuil : rien ne dépasse, les battants sont libres.':
        'Latch turned up, the blade drops below the sill: nothing sticks out, the flaps swing freely.',
    'Lame sous le seuil': 'Blade below the sill',
    'Tourniquet relevé': 'Latch turned up',
    'Passage détecté': 'Passage detected',
    'Le chat pousse le battant : l’ILS s’ouvre, l’ESP compte le passage et fait flasher les lanternes.':
        'The cat pushes the flap: the reed switch opens, the ESP counts the passage and flashes the lanterns.',
    'ILS : passage compté': 'Reed switch: passage counted',
    'Retour par gravité': 'Gravity return',
    'En s’ouvrant, le battant monte sur sa came (3 mm à 60°) ; lâché, son poids le ramène au centre.':
        'As it opens, the flap rides up its cam (3 mm at 60°); released, its own weight brings it back to centre.',
    'La dent monte sur la rampe': 'The tooth rides up the ramp',
    'Éclairage RGB': 'RGB lighting',
    'Les lanternes se pilotent depuis le téléphone (ESPHome ou WLED) : couleurs, gyrophare, minuterie.':
        'Control the lanterns from your phone (ESPHome or WLED): colours, beacon, timers.',
    'Illustration : frottements, aimants et électronique non simulés':
        'Illustration: friction, magnets and electronics are not simulated',
    'TARDIS V8 · prête à imprimer': 'TARDIS Geronimeow · ready to print',
    '12 plateaux · cames réglables · verrou central · capteur · lanternes RGB':
        '12 plates · adjustable cams · central lock · sensor · RGB lanterns',
}


def tr(text):
    text = RENAME.get(text, text)
    if not EN_MODE:
        return text
    if text not in EN:
        raise KeyError('Traduction manquante : ' + text)
    return EN[text]


for sc in spec['scenes']:
    sc['title'], sc['text'] = tr(sc['title']), tr(sc['text'])
for labs in spec['labels'].values():
    for lab in labs:
        lab['label'] = tr(lab['label'])
FPS, W, H = spec['fps'], spec['width'], spec['height']
DEST = OUT / ('montage_legende' + SUFFIX); DEST.mkdir(exist_ok=True)
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
REG = '/System/Library/Fonts/Supplemental/Arial.ttf'
F_TITLE, F_TEXT, F_SMALL = ImageFont.truetype(BOLD, 34), ImageFont.truetype(REG, 23), ImageFont.truetype(REG, 16)
F_STEP, F_LABEL = ImageFont.truetype(BOLD, 18), ImageFont.truetype(BOLD, 19)
F_HERO, F_HERO2 = ImageFont.truetype(BOLD, 64), ImageFont.truetype(REG, 26)
GOLD, IVORY, NAVY, ORANGE = (189, 148, 82), (244, 230, 200), (18, 33, 52), (255, 150, 40)


def smooth(t, a, b):
    v = max(0., min(1., (t - a) / (b - a)))
    return v * v * (3 - 2 * v)


def wrap(text, draw, font, width):
    lines, line = [], ''
    for word in text.split():
        test = (line + ' ' + word).strip()
        if draw.textlength(test, font=font) > width and line:
            lines.append(line); line = word
        else:
            line = test
    return lines + [line]


def scene_at(t):
    return max((s for s in spec['scenes'] if s['t'] <= t), key=lambda s: s['t'])


def overlay(img, t, labels):
    sc = scene_at(t)
    base = img.convert('RGBA'); layer = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    a_in = smooth(t, sc['t'] + .15, sc['t'] + .7) * (1 - smooth(t, sc['end'] - .35, sc['end']))
    if sc['intro']:
        k = smooth(t, .4, 1.4) * (1 - smooth(t, 4.2, 5))
        d.rectangle((0, H * .62, W, H * .62 + 150), fill=(8, 14, 24, int(170 * k)))
        d.text((W / 2, H * .62 + 48), sc['title'], font=F_HERO, fill=(*IVORY, int(255 * k)), anchor='mm')
        for j, line in enumerate(wrap(sc['text'], d, F_HERO2, W - 200)):
            d.text((W / 2, H * .62 + 100 + 32 * j), line, font=F_HERO2, fill=(*GOLD, int(255 * k)), anchor='mm')
        return Image.alpha_composite(base, layer).convert('RGB')
    # Bandeau haut : numero d'etape et titre.
    a = int(255 * a_in)
    d.rounded_rectangle((24, 22, 24 + 28 + d.textlength(sc['title'], font=F_TITLE) + 120, 82), 14, fill=(8, 14, 24, int(200 * a_in)))
    d.rounded_rectangle((34, 33, 108, 71), 10, fill=(*GOLD, a))
    d.text((71, 52), f"{sc['step']}/{sc['steps']}", font=F_STEP, fill=(*NAVY, a), anchor='mm')
    d.text((124, 52), sc['title'], font=F_TITLE, fill=(*IVORY, a), anchor='lm')
    # Bandeau bas en degrade : explication.
    lines = wrap(sc['text'], d, F_TEXT, W - 120)
    hh = 40 + 32 * len(lines)
    for y in range(hh + 40):
        k = min(1, y / 40)
        d.line((0, H - hh - 40 + y, W, H - hh - 40 + y), fill=(6, 10, 18, int(200 * k * a_in)))
    for j, line in enumerate(lines):
        d.text((60, H - hh + 6 + 32 * j), line, font=F_TEXT, fill=(*IVORY, a))
    d.text((W - 24, H - 14), tr('Illustration : frottements, aimants et électronique non simulés'), font=F_SMALL,
           fill=(170, 180, 195, int(200 * a_in)), anchor='rd')
    # Barre de progression avec reperes d'etapes.
    d.rectangle((0, H - 4, int(W * t / spec['duration_seconds']), H), fill=(*GOLD, 255))
    # Etiquettes : pastille sur la piece, trait, cartouche.
    ka = smooth(t, sc['t'] + .9, sc['t'] + 1.5) * (1 - smooth(t, sc['end'] - .4, sc['end']))
    placed = []
    for j, lab in enumerate(labels or []):
        x, y, ok = lab['xy']
        if not ok:
            continue
        alpha = int(255 * ka)
        tw = d.textlength(lab['label'], font=F_LABEL)
        # Cartouche a gauche ou a droite selon la position, decale verticalement.
        right = x < W * .55
        bx = x + 90 if right else x - 90 - tw - 24
        by = y - 70 - 0 * j
        by = max(100, min(H - 200, by))
        for px, py in placed:
            if abs(py - by) < 44 and abs(px - bx) < 300:
                by = py + 48
        placed.append((bx, by))
        ex = bx if right else bx + tw + 24
        d.line((x, y, ex, by + 17), fill=(*ORANGE, alpha), width=3)
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(*ORANGE, alpha), outline=(255, 255, 255, alpha), width=2)
        d.rounded_rectangle((bx, by, bx + tw + 24, by + 34), 9, fill=(255, 255, 255, int(235 * ka)), outline=(*ORANGE, alpha), width=2)
        d.text((bx + 12, by + 17), lab['label'], font=F_LABEL, fill=(*NAVY, alpha), anchor='lm')
    out = Image.alpha_composite(base, layer)
    if sc['outro']:
        # Carton final sur son propre calque (un trace RGBA remplace les pixels, il ne
        # se melange pas : sur le meme calque, il effacerait titres et textes).
        k = smooth(t, spec['duration_seconds'] - 3.5, spec['duration_seconds'] - 2.5)
        if k > 0:
            card = Image.new('RGBA', base.size, (6, 10, 18, int(190 * k))); c = ImageDraw.Draw(card)
            c.text((W / 2, H / 2 - 40), tr('TARDIS V8 · prête à imprimer'), font=F_HERO, fill=(*IVORY, int(255 * k)), anchor='mm')
            c.text((W / 2, H / 2 + 30), tr('12 plateaux · cames réglables · verrou central · capteur · lanternes RGB'),
                   font=F_HERO2, fill=(*GOLD, int(255 * k)), anchor='mm')
            out = Image.alpha_composite(out, card)
    return out.convert('RGB')


frames = sorted((OUT / 'montage_frames').glob('*.png'))
for f in frames:
    i = int(f.stem); t = i / FPS
    img = overlay(Image.open(f).convert('RGB'), t, spec['labels'].get(str(i)))
    img.save(DEST / f.name)
if TEST:
    print('TEST', len(frames), DEST); sys.exit()
src = str(DEST / '%04d.png')
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', src,
                '-vf', 'hqdn3d=3:3:4:4', '-c:v', 'libx264', '-crf', '23', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                str(OUT / f'montage_complet_V8{SUFFIX}.mp4')], check=True)
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', src, '-vf',
                'hqdn3d=4:4:6:6,fps=6,scale=560:-2:flags=lanczos,split[a][b];[a]palettegen=max_colors=96:stats_mode=diff[p];'
                '[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                '-loop', '0', str(OUT / f'montage_complet_V8{SUFFIX}.gif')], check=True)
for name, t in (('apercu_eclate', 7.5), ('apercu_cames', 11.5), ('apercu_verrou', 52), ('apercu_ouvert', 58.6)):
    shutil.copyfile(DEST / f'{int(t * FPS):04d}.png', OUT / f'montage_{name}{SUFFIX}.png')
summary = dict(fps=FPS, frame_count=len(frames), duration_seconds=len(frames) / FPS, width=W, height=H,
               mp4=f'montage_complet_V8{SUFFIX}.mp4', gif=f'montage_complet_V8{SUFFIX}.gif',
               steps=[s['title'] for s in spec['scenes']])
(OUT / f'export_animation{SUFFIX}.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False))
shutil.rmtree(DEST)
print(json.dumps(summary, ensure_ascii=False))
