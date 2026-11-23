# Régénérer et maintenir le projet — V8

**[English version](en/DEVELOPMENT.md)**

## Outils

| Outil | Version utilisée |
| --- | --- |
| Blender | 5.0.1, application macOS |
| Creality Print | 7.3.1 (ouverture et tranchage, interface et ligne de commande) |
| lib3mf, Pillow | voir `requirements-tools.txt` |
| FFmpeg | 8.1 |
| ESPHome | 2025.5 (validation de la configuration uniquement) |

Les générateurs Blender utilisent `bpy`, `bmesh` et `mathutils`, fournis par Blender.
Les autres scripts utilisent Python avec les dépendances de `requirements-tools.txt` :

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-tools.txt
```

FFmpeg doit être dans le `PATH`. Sous macOS, Blender est appelé par
`/Applications/Blender.app/Contents/MacOS/Blender`, et Creality Print est cherché dans
`/Applications/Creality Print.app`. Les scripts chargent Arial depuis les polices
système macOS. Adapter ces chemins sur un autre système.

## Modèle et plateaux

Depuis la racine du dépôt :

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python tardis_v8/generate.py
```

`generate.py` écrit les STL, les 12 plateaux 3MF (déjà convertis en projets Creality
Print), l'assemblage de référence, `verification.json` (avec le contrôle de
l'enveloppe des cames), le modèle Blender et trois rendus. Ajouter
`-- --no-render` pour sauter les rendus. Les paramètres sont en tête du fichier :
épaisseur de porte, pentes des cames, verrou, aimants, capteur, rainures, gabarit.

La conversion en projet Creality Print se fait par `scripts/exporter_projets_creality.py`,
appelé par le générateur. Elle reprend les réglages des modèles de
`scripts/modeles_creality/`, puis y ajoute la tour de purge, les couleurs et les
réglages par objet du fichier généré.

## Contrôles

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python tardis_v8/verify_geometry.py
.venv/bin/python tardis_v8/verify_3mf.py
python3 scripts/trancher_creality_print.py tardis_v8
python3 scripts/audit_tours.py
```

- `verify_geometry.py` : montage fermé, débattement pour les trois cames, butées,
  verrou (balayage fin), tourniquet, aimants. Résultat dans `controle_geometrie.json`.
- `verify_3mf.py` : lecture indépendante des 3MF par lib3mf (`controle_3mf.json`).
- `trancher_creality_print.py` : tranchage de chaque plateau par Creality Print en ligne
  de commande (`controle_tranchage.json` : temps, masse, couleurs, conflits).
- `audit_tours.py` : tout le dépôt, projets natifs et tour de purge hors des pièces.

Blender peut renvoyer un code nul même si son script lève une exception : lire aussi
les rapports JSON et la sortie. L'ouverture et le tranchage dans l'interface de
Creality Print se vérifient à la main, plateau par plateau.

## Figures et vidéo

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/vignettes_plateaux.py -- tardis_v8
.venv/bin/python scripts/planche_plateaux.py tardis_v8
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_came.py -- tardis_v8
.venv/bin/python scripts/planche_came.py tardis_v8
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_details_v8.py -- tardis_v8
.venv/bin/python scripts/planche_details_v8.py tardis_v8
/Applications/Blender.app/Contents/MacOS/Blender --background --python scripts/render_cablage.py -- tardis_v8
.venv/bin/python scripts/planche_cablage.py tardis_v8
.venv/bin/python scripts/schema_eclairage.py tardis_v8
.venv/bin/python scripts/figure_gabarit.py tardis_v8
/Applications/Blender.app/Contents/MacOS/Blender --background --python tardis_v8/visualisations/render_visuals.py -- montage
python3 tardis_v8/visualisations/compose_montage.py        # sous-titres français
python3 tardis_v8/visualisations/compose_montage.py en     # sous-titres anglais
.venv/bin/python scripts/couverture.py                     # images de couverture
.venv/bin/python scripts/annoter_captures.py               # captures Creality Print annotées
```

La vidéo (78 s, 1280 × 720) est rendue image par image dans EEVEE. `render_visuals.py`
enregistre pour chaque image la position à l'écran des pièces étiquetées ;
`compose_montage.py` ajoute titres, textes et étiquettes, puis encode le MP4 et le GIF.
`-- test` rend quatorze images de contrôle.

Les captures du guide Creality Print sont faites à la main dans l'interface (plein
écran, fenêtre maximisée) et rangées dans `docs/images/creality/brut/` ; les cadres et
légendes sont ajoutés par `scripts/annoter_captures.py`, qui écrit les versions
française et anglaise. Pour une nouvelle capture, ajuster les coordonnées des cadres
dans ce script.

## ESPHome

```sh
pip install esphome
cp tardis_v8/esphome/secrets.yaml.example tardis_v8/esphome/secrets.yaml   # puis le remplir
esphome config tardis_v8/esphome/chatiere-tardis.yaml
```

## Publier

Le projet est publié sous le nom **TARDIS Geronimeow** :
[github.com/jjtronics/tardis-geronimeow-cat-door](https://github.com/jjtronics/tardis-geronimeow-cat-door)
(public, Discussions ouvertes, aperçu social `docs/images/couverture.jpg`).

Le travail se fait dans le dépôt du mainteneur, qui garde tout l'historique de
conception. Le dépôt public en reçoit une copie à l'identique, avec un historique
propre et léger. Les deux dossiers sont côte à côte : `CHATIERE/` (travail) et
`tardis-geronimeow-cat-door/` (publication). Pour publier l'état courant :

```sh
cd ../tardis-geronimeow-cat-door
git pull
git rm -rq . && git -C ../CHATIERE archive HEAD | tar -x -C .
git add -A && git commit -m "…" && git push
diff <(git ls-files | sort) <(git -C ../CHATIERE ls-files | sort)   # doit être vide
```

Quand les plateaux, les STL ou la configuration ESPHome changent, refaire les archives
et les joindre à une release (`--clobber` remplace celles d'une release existante) :

```sh
python3 scripts/archives_release.py v8
gh release upload v8.0 -R jjtronics/tardis-geronimeow-cat-door --clobber dist/*.zip
```

Avant chaque publication : contrôles de [Contrôles](#contrôles), liens de la
documentation, et documentation française et anglaise tenues à jour ensemble.

## Gestion des fichiers

Le dépôt ne contient que la V8 ; les itérations précédentes sont racontées dans
[HISTORIQUE.md](HISTORIQUE.md).

Git ignore les images intermédiaires (`montage_frames/`, `montage_legende*/`), les
archives de release (`dist/`), les secrets ESPHome (`secrets.yaml`), les sauvegardes `.blend1`, les journaux et les
caches. Les modèles Blender, STL, 3MF, rendus, GIF et MP4 sont versionnés.

Après une régénération, actualiser l'inventaire SHA-256 :

```sh
python3 scripts/update_inventory.py
```
