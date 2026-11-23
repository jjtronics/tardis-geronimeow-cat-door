"""Annote les captures d'ecran de Creality Print du guide, en francais et en anglais.

    .venv/bin/python scripts/annoter_captures.py

Les captures brutes (plein ecran, 1372 x 891) sont dans docs/images/creality/brut/.
Chaque capture est recadree sur la fenetre, puis recoit des cadres numerotes et une
legende. Ecrit docs/images/creality/<nom>.jpg (francais) et
docs/images/creality/en/<nom>.jpg (anglais).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent / 'docs' / 'images' / 'creality'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
REG = '/System/Library/Fonts/Supplemental/Arial.ttf'
GREEN, WHITE, INK, PAPER = (34, 177, 96), (255, 255, 255), (30, 34, 40), (246, 244, 239)
WINDOW = (0, 30, 1372, 838)        # fenetre de Creality Print dans la capture plein ecran

# nom : (recadrage, [(cadre x0, y0, x1, y1, position de la pastille), ...], legendes fr, legendes en)
SHOTS = {
    '01_projet_ouvert': (WINDOW, [
        ((30, 110, 222, 130), 'left'), ((1072, 110, 1362, 192), 'left'),
        ((304, 194, 374, 258), 'left'), ((912, 783, 1048, 805), 'left')],
        ["Imprimante K1 Max 0,4 mm chargée par le projet",
         "CFS : 1 bleu · 2 ivoire · 3 noir · 4 laiton",
         "Tour de purge déjà placée, hors des pièces",
         "Découper le plateau"],
        ["K1 Max 0.4 mm printer loaded by the project",
         "CFS: 1 blue · 2 ivory · 3 black · 4 brass",
         "Prime tower already placed, away from the parts",
         "Slice the plate"]),
    '02_apercu_tranche': (WINDOW, [
        ((100, 250, 336, 287), 'left'), ((100, 390, 386, 529), 'left'),
        ((104, 555, 292, 573), 'left'), ((700, 715, 788, 752), 'left'),
        ((912, 809, 1048, 831), 'left')],
        ["Durée et masse totales",
         "Détail par couleur : pièce, purge, tour",
         "Nombre de changements de couleur",
         "Bordures (5 mm) autour des petites pièces, bien séparées",
         "Envoyer à l'imprimante"],
        ["Total time and weight",
         "Per colour: part, purge, tower",
         "Number of colour changes",
         "5 mm brims around small parts, kept apart",
         "Send to the printer"]),
    '03_supports_fourreaux': (WINDOW, [
        ((38, 312, 132, 389), 'left'), ((413, 292, 447, 327), 'top'),
        ((733, 292, 767, 327), 'top')],
        ["4 volumes « support fourreau » dans le projet",
         "Volume de support sous un fourreau d'axe",
         "Idem, deuxième charnière (les deux autres sont en bas)"],
        ["4 \"support fourreau\" volumes in the project",
         "Support volume under an axle sleeve",
         "Same, second hinge (the other two are at the bottom)"]),
    '04_support_genere': ((100, 225, 960, 760), [
        ((410, 296, 458, 327), 'top'), ((728, 296, 774, 327), 'top'),
        ((396, 648, 444, 680), 'top'), ((756, 648, 802, 680), 'top')],
        ["Support (vert) sous un fourreau d'axe haut",
         "Idem, deuxième charnière haute",
         "Fourreau d'axe bas",
         "Fourreau d'axe bas : rien d'autre n'est supporté"],
        ["Support (green) under an upper axle sleeve",
         "Same, second upper hinge",
         "Lower axle sleeve",
         "Lower axle sleeve: nothing else is supported"]),
    '05_tpu': (None, [((22, 88, 244, 183), 'left')],
               ["Emplacement 1 : CR-TPU (bobine externe, hors CFS)"],
               ["Slot 1: CR-TPU (external spool, not through the CFS)"]),
}


def badge(d, x, y, n, font):
    d.ellipse((x - 15, y - 15, x + 15, y + 15), fill=GREEN, outline=WHITE, width=3)
    d.text((x, y + 1), str(n), font=font, fill=WHITE, anchor='mm')


def annotate(name, crop, marks, captions):
    im = Image.open(ROOT / 'brut' / f'{name}.jpg').convert('RGB')
    ox, oy = (crop[0], crop[1]) if crop else (0, 0)
    if crop:
        im = im.crop(crop)
    scale = 1 if im.width > 900 else 1.4
    if scale != 1:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    fb = ImageFont.truetype(BOLD, 17)
    for n, ((x0, y0, x1, y1), where) in enumerate(marks, 1):
        box = [(x0 - ox) * scale, (y0 - oy) * scale, (x1 - ox) * scale, (y1 - oy) * scale]
        d.rounded_rectangle(box, 6, outline=WHITE, width=5)
        d.rounded_rectangle(box, 6, outline=GREEN, width=3)
        bx, by = (box[0] - 4, box[1] - 4) if where == 'left' else ((box[0] + box[2]) / 2, box[1] - 18)
        badge(d, bx, by, n, fb)
    f = ImageFont.truetype(REG, 19)
    band = 24 + 34 * len(captions)
    out = Image.new('RGB', (im.width, im.height + band), PAPER)
    out.paste(im, (0, 0)); d = ImageDraw.Draw(out)
    for n, text in enumerate(captions, 1):
        y = im.height + 28 + 34 * (n - 1)
        badge(d, 28, y, n, fb)
        d.text((56, y), text, font=f, fill=INK, anchor='lm')
    return out


(ROOT / 'en').mkdir(exist_ok=True)
for name, (crop, marks, fr, en) in SHOTS.items():
    for folder, captions in ((ROOT, fr), (ROOT / 'en', en)):
        annotate(name, crop, marks, captions).save(folder / f'{name}.jpg', quality=88)
    print(name)
