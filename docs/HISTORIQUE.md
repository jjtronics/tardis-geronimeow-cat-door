# Historique de la conception

Les étapes ci-dessous retracent le travail réalisé le **4 novembre 2026**, dans
l'ordre des demandes et des corrections. Le projet a été initialisé dans Git
après ces itérations ; les dates ne sont pas des jalons d'impression physique.

## Point de départ : le kit et l'image de référence

La demande initiale était de reprendre un TARDIS imprimable pour en faire une
chatière à deux portes, dans l'esprit d'une image imaginée par IA. L'espace de
travail contenait le TARDIS Deluxe Kit de countspatula : panneaux, fenêtres,
base, toit, pièces de lanterne, étiquettes et guide PDF.

L'examen des STL a montré une façade miniature d'environ **65,74 × 115,79 mm**,
avec une base de 77,55 mm de côté. Le projet a donc été reconstruit par code à
la taille d'un passage de chat, avec une mécanique propre. Les générateurs des
prototypes n'importent pas les maillages de ce kit.

## Dimensions et sens de circulation

Le gabarit demandé était celui d'un chat européen courant, en s'inspirant des
chatières ordinaires. Une ouverture de 170 × 190 mm a d'abord été envisagée.
Le choix a ensuite été porté à **190 × 200 mm** pour ménager les pivots et le
débattement. Cette cote est celle du tunnel ; les pièces mobiles peuvent réduire
localement le passage réel.

La première préférence exprimée était une ouverture dans un seul sens. Elle a
été corrigée immédiatement : les chats doivent passer dans les deux sens. La
demande ajoutait un moyen d'interdire complètement le passage. Les versions
construites ont donc des battants libres dans les deux sens et un verrou amovible.

La référence d'épaisseur de porte est restée **40 mm**, faute de mesure réelle.
Il s'agit d'un paramètre à adapter, pas d'une cote fournie par l'utilisateur.

## V0 — prototype mécanique

Le dossier `prototype_tardis/` contenait un premier modèle Blender, 30 STL, les
rendus fermé/ouvert, un contrôle des maillages et un contrôle du débattement à
sept angles. Le cadre et le tunnel sont alors constitués de plusieurs éléments.

Un verrou métallique traverse des œillets visibles sur les deux jambages et les
deux battants. Les fenêtres sont des plaquettes décoratives rapportées ; le texte
de présentation n'est pas encore entièrement présent en volume imprimable.

La fermeture reste manuelle : des pivots verticaux ne referment pas naturellement
les battants. Aucun mécanisme de rappel n'a été ajouté au fil des versions.

## V1 — finition et quatre couleurs

Le retour demandait davantage de couleur et une apparence de produit abouti.
Le matériel a été précisé : **Creality K1 Max, CFS, Creality Print**.

La V1 introduit les quatre couleurs bleu, ivoire, noir et laiton, les fenêtres à
petits carreaux, les panneaux moulurés, la plaque « OF CATS », le médaillon,
les boutons et une lanterne détaillée. Les lettres deviennent de vrais maillages.
Le cadre et le tunnel sont monoblocs, les vis sont masquées et le verrou descend
près du seuil pour libérer visuellement la façade.

Les exports comprennent des 3MF multiparties orientés par sous-ensemble et une
palette avec affectations de filament. Leur structure a été contrôlée avec la
bibliothèque indépendante lib3mf. Une éprouvette a été ajoutée avant l'impression
des grandes pièces.

## V2 — verrou caché et montage animé

La demande suivante était de supprimer les fixations visibles du verrou. La tige
entre désormais par le flanc droit, traverse **l'épaisseur des deux portes**, puis
rejoint un logement borgne dans le jambage gauche. Une petite poignée bleue permet
son retrait. La traverse basse est renforcée à 9 mm pour recevoir le trou de 4,5 mm
et conserver de la matière autour de la tige de 4 mm.

Les contrôles ont confirmé le blocage de chacun des battants dans les deux sens.
Le modèle était alors livré avec 13 sous-ensembles 3MF et une tige de 240 mm.

La demande de visualisation a conduit à produire un GIF légendé de 34 secondes,
un MP4, une scène Blender animée et des rendus de pose. La porte de démonstration
mesure 830 × 2040 × 40 mm et les pièces de la chatière sont à l'échelle réelle.
La découpe, le tunnel et la visserie sont représentés dans la scène.

L'ajout des vis a révélé un manque de place derrière les caches avant. Leurs
tenons ont été raccourcis pour laisser la place à des têtes basses de 2,2 mm.
La V2 et son archive ont été actualisées avec cette correction.

## V3 — le TARDIS aussi à l'arrière

Le dernier retour sur le dessin validait l'avant mais demandait de retrouver la
cabine de l'autre côté, à la place du simple contre-cadre.

La V3 ajoute une façade arrière complète, une seconde enseigne, une seconde
lanterne et des caches pour les écrous. Les battants sont communs au passage et
reçoivent des décors sur leurs deux faces. Les décors arrière sont tournés pour
que les textes se lisent normalement depuis l'autre pièce.

Pour imprimer ces deux faces à plat, chaque battant est séparé en deux demi-coques
multicolores. Deux pions par battant alignent les demi-coques avant collage ; un
joint nominal de colle de 0,1 mm est réservé. La plaque et le médaillon arrière
ont été encastrés davantage pour dégager l'ouverture à 90°.

Le contrôle du mouvement a été renforcé à **37 positions par pas de 5°**. Il a
révélé un léger contact aux angles de 80°/85°, corrigé en augmentant le dégagement
des ouvertures de cadre de 0,4 mm de chaque côté. Les contrôles numériques finaux
ne détectent plus de collision ou de chevauchement au montage nominal.

La V3 comprend 22 sous-ensembles 3MF, 50 volumes fermés, les sources Blender,
les contrôles, cinq vues de pose, une comparaison avant/arrière et un GIF/MP4 de
38 secondes. La fin du montage présente la seconde façade terminée.

## V4 — verrou traversant et profondeur arrière rééquilibrée

Le verrou borgne de la V3 pouvait être mal interprété visuellement. La V4 fait
donc déboucher le canal à travers les deux jambages : une tige acier Ø 4 × 248 mm
traverse le jambage droit, les deux battants puis le jambage gauche. Deux embouts
bleus matérialisent et retiennent ses extrémités, celui de gauche restant amovible.

Déplacer les battants au milieu des 40 mm aurait reculé la façade avant et rendu
le verrou latéral inaccessible dans l'épaisseur de la porte support. La solution
retenue conserve les axes à l'avant et encastre un filet ivoire affleurant à
mi-profondeur du tunnel. Ce repère rééquilibre la vue arrière sans réduire le
passage ni entrer dans le balayage des battants.

La V4 conserve 22 sous-ensembles 3MF et comporte 52 volumes fermés. Les contrôles
confirment le débattement de −90° à +90° sans collision, le blocage des deux
battants dans les deux sens et le dépassement de la tige au-delà des deux côtés
du cadre.

## V5 — double action réellement exploitable

La V5 répond à la demande de rendre le passage quotidien plus autonome. La longue
tige amovible est remplacée par deux pênes Ø 4 × 87 mm captifs dans les battants.
Leurs curseurs n'ont que 12 mm de course et ne demandent aucun dégagement latéral.

Les charnières basses gagnent une enveloppe Ø 7 × 6 mm pour deux paires de
ressorts opposés, afin de rappeler les battants après une ouverture dans l'un ou
l'autre sens. Les axes sont retenus par rondelles de blocage. Quatre butées TPU
remplaçables limitent la course à 85° et le jeu central antipincement passe à
2,4 mm.

Le contrôle V5 ne détecte aucune collision de −80° à +80°, confirme le contact
des quatre butées à ±85°, le blocage bilatéral de chaque pêne et leur dégagement
complet après 12 mm. Deux prototypes grandeur réelle du bas du mécanisme permettent
un essai économique avant les grandes impressions. La version comprend finalement
25 sous-ensembles 3MF et 61 volumes.

## V6 — WhisperLock quatre modes

La V6 ajoute une cassette intérieure démontable sous le seuil, hors du passage
utile. Une molette cruciforme indexée tous les 90° sélectionne libre, entrée
seule, sortie seule ou fermé. Deux paires de cliquets opposés gèrent les sens
uniques ; le mode fermé conserve le blocage positif par les deux pênes acier.

Deux lèvres TPU décalées réduisent le bruit et les courants d'air sans se toucher
au repos. Trois clés de précharge permettent d'ajuster le rappel. Un prototype
WhisperLock à 40 % complète les prototypes bas à l'échelle 1:1. La version
comprend 31 groupes 3MF, 81 volumes et une animation dédiée aux quatre modes.

## V6 Lite — version simplifiée pour la K1 Max

Après examen de la V6 (non imprimée), une variante robuste a été demandée : seulement
LIBRE et FERMÉ avec le verrou simple, et un regroupement des pièces pour la K1 Max.
La V6 Lite retire le WhisperLock, les joints TPU et les clés de précharge, fond les
enseignes dans les façades et le chapeau dans la cage de lanterne, et répartit le tout
en 10 plateaux 3MF. La surface utile avec le CFS (300 × 295 mm) et la tour large
du profil ont conduit à tourner les façades de 90°. Aucun essai physique.

## Contrôle Creality Print de la V6 et de la V6 Lite

Demande : vérifier que les deux versions se tranchent parfaitement dans Creality
Print, couleurs comprises, puis les tester dans l'interface, sans aucun avertissement,
avec des supports seulement là où il en faut. Défauts trouvés et corrigés :

- V6 : butées, couvercle, molette, cliquets de sortie et prototype à 40 % restaient
  en position d'assemblage, en l'air. Le moteur plantait sur 23, 27, 28 et 31. Ces
  pièces sont posées à plat, côte à côte.
- V6 : les lèvres TPU de 0,4 mm debout faisaient planter le trancheur ; elles sont
  couchées sur leur largeur de 1 mm.
- V6 et Lite : la demi-coque arrière des prototypes 65 mm était imprimée décor en
  bas, ses panneaux flottant à 0,8 mm du plateau. Elle est posée comme le vrai
  battant arrière, décor vers le haut.
- V6 et Lite : couchés à plat, les fourreaux d'axe de charnière du cadre avant ont
  leur dessous arrondi à 0,8 mm du plateau (« régions flottantes »). Des volumes de
  support en mode manuel couvrent uniquement cette zone et s'arrêtent sous le trou
  d'axe, qui reste libre.
- Ouverts tels quels, les 3MF étaient vus comme « pas de Creality Print » : pièces
  recentrées, tour de purge du préréglage posée sur les battants, purge à 1,0 au lieu
  de 1,3. `scripts/exporter_projets_creality.py` fait réenregistrer chaque plateau par
  Creality Print (K1 Max 0,4 mm, Hyper PLA) avec la tour en x 60, y 257 et la purge
  par défaut.

Le CLI de Creality Print 7.2.1 plante sur tout 3MF multicolore qui déclare un
plateau ; les scripts travaillent sur une copie sans bloc `<plate>`. Résultat :
41 plateaux (31 V6, 10 Lite) ouverts et tranchés dans l'interface sans aucun
avertissement. Aucune impression réelle.

## V7 et V7 Lite : rappel par gravité

Demande : les ressorts de torsion et les axes sont difficiles à trouver ; supprimer
les ressorts et imprimer ce qui peut l'être. Les axes Ø3 se coupent dans une tige
acier, comme les pênes Ø4. Les ressorts sont remplacés par une **came en V à double
effet** sous chaque battant (principe des portes de saloon) : le battant monte de
4,5 mm par quart de tour et son poids le ramène au centre, avec un couple constant.
Les battants sont raccourcis de 5 mm, les dégagements de charnière prolongés et les
axes fixés au cadre (34 et 23,5 mm). Les colliers de pênes sont imprimés. En V7, les
clés de précharge disparaissent ; les cliquets du WhisperLock gardent leurs petits
ressorts inox.

Contrôles : débattement de −80° à +80° avec la levée, aucune collision ; maillages
fermés (la came est jointe à chaque demi-coque sans union booléenne, pour éviter les
facettes dégénérées). Creality Print est passé en 7.3.1 entre-temps : son CLI ne
plante plus sur les plateaux multicolores mais ne sait plus exporter de projet ;
`exporter_projets_creality.py` pose donc les réglages complets d'un projet Creality
Print (modèles dans `scripts/modeles_creality/`). La 7.3.1 signale aussi un surplomb
flottant sur la molette du plateau 27 (V6 et V7) : son moyeu est rendu affleurant et
elle s'imprime sur sa face de prise. Résultat : 41 plateaux V7 et V7 Lite ouverts et
tranchés dans l'interface 7.3.1 sans aucun avertissement. Aucune impression réelle.

### V7 Lite : éclairage RGB pilotable

Demande : piloter les LED des lanternes (RGB, clignotements) avec un ESP placé sous
le tunnel, dans une encoche de la porte, avec le passage des câbles. Les battants
restent sans LED. Chaque façade reçoit au dos une rainure 3 × 2 mm (lanterne,
traverse haute, jambage, retour sous le tunnel), invisible contre la porte, et le
pied de lanterne une rainure de sortie. Un berceau imprimé pour ESP32-C3 SuperMini
se loge sous le tunnel entre les deux façades ; la façade arrière a une fenêtre
USB-C côté maison. Les lanternes reçoivent des WS2812B 5 mm, pilotées par WLED.
Contrôles : 62 volumes fermés, aucune collision, supports inchangés (fourreaux
seuls), plateaux 04, 05 et 07 tranchés dans l'interface sans avertissement.
Le guide détaille ensuite toute l'électronique : schéma de câblage, résistances de
330 Ω sur les données, condensateurs de 100 nF au pied des LED, adaptateur de niveau
74AHCT125 en secours, configuration WLED et essai sur table avant collage.

## V8 : version unique

Demande : partir de la V7 Lite, ne plus suivre qu'une version, et ajouter cinq
améliorations : gabarit de découpe, cames rapportées réglables « faites
intelligemment », aimants anti-vent, capteur de passage relié à l'ESP (avec la place
pour son câble) et verrou unique.

- **Cames rapportées.** La came fixe devient une pièce enfilée sur l'axe, avec une clé
  en D sous elle (une seule position, la même came à gauche et à droite). Trois
  pentes : 3,5, 4,5 et 5,5 mm. Le dessous du nœud du battant est l'enveloppe des trois
  (pente douce avant ±60°, raide après) : le contact se fait toujours sur les lignes à
  ±60°, à la même hauteur, quelle que soit la came. Vérifié numériquement (jeu minimal
  0,3 mm pour chaque came et chaque angle) et en débattement pour les trois pentes.
  Cames imprimées en couches de 0,1 mm, pleines (réglages par objet du projet).
- **Verrou central.** Pênes acier, colliers et curseurs supprimés. Une lame imprimée
  de 10 × 4 mm coulisse dans le seuil et monte de 4 mm dans une poche fermée au coin
  bas de chaque battant ; bouton vissé. Un premier essai avec une encoche traversante
  ne bloquait rien (la lame glissait dans la poche) ; poche fermée et contrôle par
  balayage fin : blocage dès 0,5°. La première retenue (fente en L avec cran) était
  impossible : la lame, guidée à 0,2 mm, ne peut pas se décaler sur le côté. Elle est
  remplacée par un tourniquet pivotant (vis M3 × 12) qui tient le bouton en haut.
- **Plateaux.** Le générateur convertit lui-même les 3MF en projets Creality Print
  (plus jamais de fichier « géométrie seule », dont l'ouverture replaçait la tour de
  purge sur les pièces), et met une bordure de 5 mm sous les petites pièces et les
  pièces plus hautes que larges (pions, cames, cales, verrou, diffuseurs, cages).
  Les anciennes versions V1 à V5 ont été converties à leur tour, tour placée sur une
  zone libre ; deux plateaux d'archive aux pièces flottantes (V4 `12`, V5 `23`) ont été
  posés à plat. `scripts/audit_tours.py` contrôle tout le dépôt : 0 problème.
- **Chambre de connexion.** Le pied de lanterne n'avait pas la place prévue pour les
  soudures et le condensateur de 100 nF : une chambre de 9 × 13,5 × 5 mm est creusée
  sous la LED. Un premier toit plat était signalé « surplomb flottant » par Creality
  Print ; il est remplacé par un toit en pointe à 45°.
- **Aimants anti-vent.** Ø6 × 2 sous les battants et dans le seuil, puits de 6 mm et
  cales imprimées de 1 mm : écart réglable de 1 à 5 mm.
- **Capteur de passage.** Aimant Ø6 × 3 en haut des battants, deux ILS en série dans
  des poches du linteau, rainure de 2 fils sous le linteau. La rainure de câbles passe
  à 4,5 × 2,5 mm (le canal des pênes ayant disparu) pour loger les 5 fils côté avant.
  Configuration ESPHome fournie et validée (`esphome config`).
- **Gabarit.** Plateau 11 : gabarit de 3 mm, fenêtre au trait de scie, avant-trous
  des M4, encoches d'axe, gravures ; figure cotée dans le guide.

Contrôles : 75 volumes fermés, aucune interférence ni collision, 12 plateaux tranchés
dans Creality Print 7.3.1 (ligne de commande et interface) sans avertissement, captures
du guide refaites sur la V8. Aucune impression réelle.

### Revue d'impression de la V8

Analyse des surplombs et de l'espacement sur les 12 plateaux. Corrigés :
- bordures soudées entre pièces voisines (marge de 13 mm) ;
- bouton laiton à cône inversé ;
- caches de vis posés tête en bas ;
- lame du verrou et butées TPU couchées ;
- plafond conique dans la cage des lanternes ;
- jeu de 0,4 mm sur la face du canal du verrou imprimée en pont ;
- commentaires obsolètes du générateur.

Les 12 plateaux restent sans avertissement (ligne de commande ; interface vérifiée sur
les plateaux 04, 07 et 09).

## Archivage des anciennes versions

La V8 étant la seule version suivie, le prototype V0 et les dossiers V1 à V7 Lite ont
été retirés du dépôt (environ 1,3 Go), ainsi que les fichiers du kit d'origine, qui
restent cités et liés dans [PROVENANCE.md](PROVENANCE.md).

## Préparation de la publication : TARDIS Geronimeow

Le projet prend le nom public **TARDIS Geronimeow** (dépôt
`tardis-geronimeow-cat-door`) :
- licences CC BY-NC-SA 4.0 (modèles, images, documentation) et MIT (code), mention des
  marques de la BBC, kit d'origine cité et lié mais plus redistribué ;
- accueil bilingue avec image de couverture, FAQ et téléchargements ;
- toute la documentation utile traduite en anglais (`tardis_v8/README.en.md`,
  `docs/en/`), captures Creality Print refaites sur les plateaux actuels et annotées
  dans les deux langues par script ;
- vidéo de montage rendue à nouveau sur la géométrie actuelle, en version française et
  anglaise ;
- configuration ESPHome sécurisée (API chiffrée, mots de passe OTA et point d'accès) ;
- code de conduite, guide de contribution, modèles d'issues et de pull request.

## Ce qui reste à confirmer

Les validations sont numériques. Aucune impression complète ou pose réelle n'a
été réalisée pendant ce travail. Restent notamment les profils du slicer, les
jeux imprimés, la retenue des axes et des caches, le collage, l'effort d'ouverture,
la résistance du verrou et le choix de la hauteur d'installation selon le chat.
