# V8 — vidéo de montage

`montage_complet_V8.mp4` (H.264, 1280 × 720, 15 images/s, 78 s) et
`montage_complet_V8.gif` (aperçu en boucle, 560 px, 6 images/s) montrent la chatière pièce par
pièce, avec un plan de caméra par étape, des gros plans et des étiquettes qui suivent
les pièces à l'écran :

1. les pièces, en vue éclatée ;
2. les cames réglables sur leur clé en D (gros plan) ;
3. les battants et leurs axes ;
4. les aimants anti-vent et leurs cales (vue fantôme : façade et battants translucides) ;
5. le capteur de passage : aimant du battant et ILS dans le linteau (vue fantôme) ;
6. les lanternes ;
7. les câbles dans les rainures, au dos de la façade ;
8. le berceau de l'ESP32 et sa prise USB-C ;
9. tunnel, porte découpée et façade arrière ;
10. vis, caches et butées TPU ;
11. verrou central FERMÉ : bouton monté, tourniquet tourné, lame dans les deux battants ;
    une poussée sur le battant est bloquée ;
12. verrou LIBRE : tourniquet relevé, lame sous le seuil ;
13. passage détecté : l'ILS s'ouvre, les lanternes flashent ;
14. retour par gravité : la dent du battant monte sur la came (vue fantôme) ;
15. éclairage RGB et carton final.

Les images `montage_apercu_*.png` reprennent quatre moments clés pour la
documentation.

La même vidéo existe avec des sous-titres anglais : `montage_complet_V8_en.mp4`,
`montage_complet_V8_en.gif` et `montage_apercu_*_en.png` (`compose_montage.py en`).

L'animation est illustrative : la levée de la came est représentée, mais elle ne
simule ni les frottements, ni la force des aimants, ni le collage, ni l'électronique.
Elle est tirée des mêmes maillages que les plateaux 3MF.

## Régénérer

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --python tardis_v8/visualisations/render_visuals.py -- montage
python3 tardis_v8/visualisations/compose_montage.py
```

`render_visuals.py` rend les images et calcule, pour chacune, la position à l'écran
des pièces étiquetées (`montage.json`). `compose_montage.py` ajoute titres, textes et
étiquettes avec Pillow, puis encode avec ffmpeg. `-- test` (puis `compose_montage.py
test`) ne rend que quatorze images de contrôle. Les dossiers `montage_frames/` et
`montage_legende/` sont intermédiaires et ne sont pas versionnés.
