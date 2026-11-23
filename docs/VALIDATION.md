# Vérifications — V8

Les contrôles ci-dessous sont numériques : ils portent sur les fichiers et sur une
simulation à volumes rigides. Aucune pièce de la V8 n'a encore été imprimée.

## Résultats V8

| Contrôle | Résultat |
| --- | --- |
| Volumes | 76 volumes fermés, aucune arête non manifold |
| Plateaux | 12 3MF + assemblage de référence, lus sans avertissement par lib3mf |
| Montage fermé | aucun chevauchement entre pièces imprimées, aimants, ILS, axes, visserie et verrou |
| Débattement | −80° à +80° par pas de 5°, battant soulevé par la came, pour chacune des cames 3,5, 4,5 et 5,5 mm : aucune collision |
| Enveloppe des cames | pour chaque came et chaque angle (pas de 0,5°), jeu minimal de 0,3 mm et contact sur les lignes à ±60° |
| Butées | contact des quatre butées TPU à ±85° |
| Verrou central | FERMÉ : chaque battant bloqué dès 0,5°, dans les deux sens ; bouton posé sur le tourniquet ; LIBRE : lame 1,5 mm sous les battants, tourniquet hors du bouton |
| Aimants | écart anti-vent de 1 à 5 mm selon les cales (4 mm d'origine) ; aimant du capteur à 9 mm de l'ILS |
| ESPHome | `esphome config` : configuration valide |
| Creality Print 7.3.1, interface | 12 projets ouverts et tranchés un par un : aucun avertissement, tour de purge hors des pièces, bordures présentes |
| Creality Print 7.3.1, ligne de commande | 12 plateaux tranchés sans conflit ; chaque couleur affectée est extrudée ; cames en 141 couches de 0,1 mm |
| Dépôt entier | `scripts/audit_tours.py` : tous les 3MF du dépôt sont des projets Creality Print, tours de purge hors des pièces |

### Rapports sources

- [Maillages, plateaux, paramètres et enveloppe des cames](../tardis_v8/verification.json)
- [Assemblage, débattement, verrou, aimants](../tardis_v8/controle_geometrie.json)
- [Lecture indépendante des 3MF](../tardis_v8/controle_3mf.json)
- [Tranchage Creality Print](../tardis_v8/controle_tranchage.json)

Les versions antérieures (V0 à V7 Lite) ne font pas partie de ce dépôt.

## Défauts trouvés et corrigés en V8

- **Verrou sans blocage** : la première poche traversait le battant, et la lame
  glissait dedans. La poche est maintenant fermée devant et derrière, et le contrôle
  balaie les angles par pas de 0,5° : un pas unique de 5° laissait la paroi « sauter »
  par-dessus la lame.
- **Retenue du verrou impossible** : la fente en L avec un cran supposait que la lame
  se décale sur le côté, ce que son guidage interdit. Elle est remplacée par un
  tourniquet.
- **Fichiers « géométrie seule »** : un 3MF régénéré sans conversion s'ouvrait avec un
  avertissement, et Creality Print replaçait la tour de purge sur les pièces. Le
  générateur écrit désormais directement des projets Creality Print. Les anciennes
  versions ont été converties et auditées.
- **Petites pièces** : une bordure de 5 mm est ajoutée automatiquement pour qu'elles
  ne se décrochent pas.
- **Gravure du gabarit** : le texte gravé rendait le maillage ouvert ; la soustraction
  tolère maintenant ses auto-intersections.

### Revue d'impression

Une analyse des surfaces tournées vers le bas, plateau par plateau, a relevé et fait
corriger :
- des bordures de 5 mm espacées de 8 mm seulement, qui se soudaient entre pièces
  voisines (pions, cales, cames, butées, caches) : marge portée à 13 mm ;
- un bouton laiton à cône inversé, qui laissait deux corniches à plat : le pied
  s'évase maintenant vers la face ;
- des caches de vis imprimés tête en haut, avec une corniche et un plafond de cavité en
  pont : ils sont posés tête sur le plateau ;
- une lame de verrou debout, dont les couches tombaient dans le plan de cisaillement :
  elle est couchée ;
- des butées TPU debout en parois de 1 mm : elles sont couchées ;
- un plafond plat de 16 mm dans la cage des lanternes : creusé en cône à 45° ;
- la face avant du canal du verrou, pont de 10,4 mm sur une surface de guidage : jeu
  porté de 0,2 à 0,4 mm de ce côté.

Restent des ponts courts sans conséquence : rainures de câbles (4,5 mm), trous d'axe,
anneau haut de la cage entre ses montants.

## Portée et validations restantes

Il s'agit de volumes rigides à cotes nominales et de positions discrètes. Les contrôles
ne sont ni une simulation continue, ni une validation de résistance, de frottement ou
de vieillissement.

Restent à valider sur le prototype et la chatière réelle :
- le glissement de la came et le choix de la pente ;
- la force des aimants et le nombre de cales ;
- le seuil des ILS et la fiabilité du comptage ;
- le collage des demi-coques et des aimants ;
- la tenue des butées TPU et du tourniquet ;
- les jeux réels sur votre imprimante ;
- l'effort d'ouverture pour le chat et sa sécurité (au moins 50 cycles à la main).
