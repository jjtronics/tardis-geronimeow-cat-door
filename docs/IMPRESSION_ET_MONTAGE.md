# TARDIS Geronimeow — impression, fournitures et montage (V8)

**[English version](en/PRINTING_AND_ASSEMBLY.md)**

La [V8](../tardis_v8/README.md) est la seule version suivie. Ce document résume
l'impression, la liste d'achat et l'ordre de montage. Le guide V8 les détaille, avec
les réglages, le câblage et ESPHome. Le [guide illustré Creality Print](GUIDE_CREALITY_PRINT.md)
montre chaque étape dans le logiciel.

## Préparer l'impression

1. Mesurer la porte (épaisseur, hauteur de passage souhaitée). Les fichiers sont
   calculés pour une porte de 40 mm : les vis M4 × 70 en dépendent.
2. Ouvrir les plateaux de `tardis_v8/3mf/` dans Creality Print 7.3.1. Chaque fichier
   est un projet complet : K1 Max 0,4 mm, 0,20 mm Standard, Hyper PLA (ou CR-TPU pour
   les butées), purge × 1,3. Tour de purge, supports et bordures sont déjà réglés.
3. Bobines du CFS : 1 bleu, 2 ivoire, 3 noir, 4 laiton. Le TPU passe par la bobine
   externe.
4. Ne pas déplacer la tour de purge ni modifier les volumes « support fourreau » du
   cadre avant : ce sont les seuls supports nécessaires.
5. Commencer par `00_Eprouvette_jeux`, `01_Prototype_mecanique_75mm`,
   `10_Cames_reglables` et `07_Petites_pieces_bleu`, puis `11_Gabarit_porte`.

Les petites pièces et les pièces plus hautes que larges reçoivent une bordure de 5 mm
(réglage par objet) : elle se retire à la main. Les cames s'impriment en couches de
0,1 mm, pleines.

## Les 12 plateaux

| Plateau | Contenu |
| --- | --- |
| `00_Eprouvette_jeux` | essais : axe, vis M4, cache, pion, logement d'aimant, avant-trou M3, poche d'ILS, canal du verrou, clé en D |
| `01_Prototype_mecanique_75mm` | bas du cadre et bas des battants à l'échelle 1:1 : charnière, came, verrou, aimants |
| `02_Battant_gauche`, `03_Battant_droit` | deux demi-coques multicolores et deux pions par battant |
| `04_Facade_avant` | cadre avant et enseigne POLICE BOX |
| `05_Facade_arriere` | façade arrière, enseigne, fenêtre USB-C |
| `06_Tunnel` | tunnel et filet ivoire |
| `07_Petites_pieces_bleu` | caches de vis, lame, bouton et tourniquet du verrou, berceau ESP, cales d'aimant, bases et cages de lanterne |
| `08_Diffuseurs_ivoire` | deux diffuseurs de lanterne |
| `09_Butees_TPU` | quatre butées souples (TPU) |
| `10_Cames_reglables` | cames de 3,5, 4,5 et 5,5 mm, deux de chaque |
| `11_Gabarit_porte` | gabarit de découpe et de perçage de la porte |

Gauche et droite désignent la vue depuis l'avant (extérieur). Garder les caches avant
et arrière séparés : leurs formes internes diffèrent.

## Liste d'achat

### Mécanique

| Qté | Fourniture | Précisions |
| ---: | --- | --- |
| 2 + 2 | tiges acier Ø3 mm | coupées à **39,4 mm** (axes bas) et **24,3 mm** (axes hauts), ébavurées |
| 8 | clips pour axe Ø3 mm | e-clips DIN 6799 taille 2,3 (gorge à la lime) ou rondelles Starlock Ø3 à pousser |
| 4 | aimants néodyme **Ø6 × 2 mm** | N35 conseillé : un aimant plus fort (N52) peut retenir trop fort |
| 2 | aimants néodyme **Ø6 × 3 mm** | N35 à N52, pour le capteur |
| 2 (+1) | ILS normalement ouverts | ampoule de verre 2 × 14 mm, sensibilité 10 à 20 AT |
| 1 | vis M3 × 18 | bouton du verrou, vissée dans la lame |
| 1 | vis M3 × 12 | pivot du tourniquet, avec une rondelle M3 si besoin |
| 4 | vis M4 × 70 tête basse | avec 4 rondelles (Ø ext. ≤ 8 mm) et 4 écrous (≤ 3,2 mm) ; longueur pour une porte de 40 mm |
| — | colles et adhésifs | cyanoacrylate (aimants, pions), colle pour PLA (demi-coques), double face mousse, gaine thermo |
| — | facultatif | graphite sec pour la rampe des cames |

### Éclairage et capteur

| Qté | Fourniture | Précisions |
| ---: | --- | --- |
| 1 | ESP32-C3 SuperMini | 22,5 × 18 mm, USB-C ; vérifier les cotes avant d'imprimer le berceau |
| 2 (+1) | LED RGB adressables 5 mm WS2812B F5 | brochage à vérifier chez le vendeur |
| 2 | résistances 330 Ω, ¼ W | sur chaque ligne de données, côté ESP |
| 2 | condensateurs céramique 100 nF | CMS 0805 conseillé (ou petit traversant), logé dans le pied de la lanterne |
| 2 × 60 cm | fil fin 3 conducteurs, AWG 28 à 30 | 5 V, masse, données (une lanterne chacun) |
| 60 cm | fil fin 2 conducteurs, AWG 28 à 30 | boucle des deux ILS |
| 1 | câble USB-C et chargeur 5 V, 1 A | alimentation, côté maison |
| en option | module 74AHCT125 | seulement si une lanterne scintille |

Outillage : scie sauteuse, perceuse (forets Ø3, Ø5 et Ø10), lime fine, pince à
dénuder, fer à souder à panne fine, multimètre.

## Montage

1. **Valider** l'éprouvette et le prototype 75 mm : came (choix de la pente), aimants
   (nombre de cales), verrou, capteur. Voir
   [Valider et régler](../tardis_v8/README.md#valider-et-régler).
2. **Découper la porte** avec le gabarit (plateau 11) : fenêtre au trait de scie,
   avant-trous Ø3,2 puis perçage Ø5 pour les M4.
3. **Battants** : coller les aimants (Ø6 × 2 en bas, Ø6 × 3 en haut) en respectant la
   polarité notée. Ne pas encore coller les demi-coques : elles se ferment sur l'axe et
   son clip haut, à l'étape 6.
4. **Façade avant** : cales et aimants du seuil, ILS dans le linteau, câbles dans les
   rainures, lanterne et sa LED (soudures et condensateur dans la chambre de connexion
   du pied).
5. **Verrou** : lame dans son canal, bouton vissé (M3 × 18), tourniquet sur son pivot
   (M3 × 12).
6. **Cames et battants** : cames sur leurs clés en D, axes et clips. Poser la
   demi-coque avant sur sa came, placer les pions, puis coller la demi-coque arrière. Chaque battant doit revenir seul au centre dans les deux sens.
7. **Électronique** : soudure, essai sur table, ESP dans le berceau, berceau dans
   l'encoche de la porte.
8. **Tunnel, façade arrière**, vis M4, rondelles, écrous, caches, butées TPU.
9. Charger la configuration ESPHome et faire au moins **50 cycles** à la main en LIBRE
   et en FERMÉ avant de laisser le chat seul.

La [vidéo de montage](../tardis_v8/visualisations/montage_complet_V8.mp4) suit cet
ordre, avec des gros plans sur chaque mécanisme.

## Versions précédentes

Le dépôt ne contient que la V8. Les itérations V0 à V7 Lite (ressorts, WhisperLock,
pênes acier…) sont racontées dans [HISTORIQUE.md](HISTORIQUE.md) ; leurs fournitures
ne concernent pas la V8.
