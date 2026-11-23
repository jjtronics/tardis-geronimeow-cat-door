"""Convertit les plateaux 3MF generes en projets Creality Print complets.

    python3 scripts/exporter_projets_creality.py tardis_v8

A lancer apres generate.py et verify_3mf.py. Un 3MF qui ne vient pas de Creality
Print est ouvert en « geometrie seule » : l'interface recentre les pieces et place
la tour de purge selon le preregalage, souvent sur les pieces. Ce script donne a
chaque plateau les reglages complets d'un projet Creality Print (modeles dans
scripts/modeles_creality/ : K1 Max 0,4 mm, 0,20 mm Standard, Hyper PLA ou CR-TPU en
emplacement 1, purge x 1,3), avec la position de tour et les couleurs du 3MF
genere. Geometrie, couleurs par piece, plateau, supports et reglages par objet ne
changent pas.

Les modeles viennent de projets enregistres par Creality Print 7.2.1 (export en
ligne de commande, disparu en 7.3.1) ; Creality Print 7.3.1 les ouvre et les
tranche sans avertissement.
"""
import glob, json, os, re, sys, zipfile

MODELES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modeles_creality')
APPLICATION = 'Creality_Print V7.2.1.5476 Release'


def convert(src):
    with zipfile.ZipFile(src) as zi:
        files = {it.filename: zi.read(it.filename) for it in zi.infolist()}
    model = files['3D/3dmodel.model']
    if b'Creality_Print' in model:
        return False  # deja un projet Creality Print
    ours = json.loads(files['Metadata/project_settings.config'])
    tpu = ours['filament_type'][0] == 'TPU'
    settings = json.load(open(f"{MODELES}/projet_{'tpu' if tpu else 'pla'}.json"))
    settings['filament_colour'] = ours['filament_colour']
    for key in ('wipe_tower_x', 'wipe_tower_y'):
        if key in ours:
            settings[key] = ours[key]
    files['3D/3dmodel.model'] = re.sub(rb'(<metadata name="Application">)[^<]*(</metadata>)',
                                       rb'\g<1>' + APPLICATION.encode() + rb'\g<2>', model)
    files['Metadata/project_settings.config'] = json.dumps(settings, indent=4).encode()
    for name in ('creality.config', 'slice_info.config'):
        files['Metadata/' + name] = open(f'{MODELES}/{name}', 'rb').read()
    tmp = src + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zo:
        for name, data in files.items():
            zo.writestr(name, data)
    os.replace(tmp, src)
    return True


def main():
    for version in sys.argv[1:]:
        for src in sorted(glob.glob(f'{version}/3mf/*.3mf')):
            print('projet Creality Print :' if convert(src) else 'deja converti :', src, flush=True)


if __name__ == '__main__':
    main()
