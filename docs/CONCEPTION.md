# Choix de conception — V8

## Passage commun et deux façades

Les deux façades encadrent le même tunnel. Deux battants double action pivotent
sur quatre axes côté avant. Ils sont décorés des deux côtés et donc vus en retrait
dans le tunnel depuis l'arrière. La longueur du tunnel suit l'épaisseur de la porte,
40 mm par défaut (`door_depth`).

Chaque façade mesure 244 × 314,5 mm avec sa lanterne. Le tunnel intérieur mesure
190 × 200 mm, son extérieur 194,8 × 204,8 mm. La découpe de la porte (gabarit) ajoute
0,7 mm par côté, soit 196,2 × 206,2 mm, plus une encoche de 36 × 11 mm sous le tunnel
pour l'ESP32.

Les portes ont des fenêtres à six carreaux et trois panneaux moulurés. La plaque, le
médaillon et les boutons sont présents des deux côtés. Les fenêtres sont décoratives,
en filament ivoire : ce ne sont pas des vitres.

## Charnières et rappel par gravité

Les battants tournent sur des axes acier Ø3 dans des alésages de Ø3,4 mm. Les axes
sont fixés au cadre par des clips : le battant coulisse dessus en montant.

Sous chaque battant, une **came en V rapportée** est enfilée sur l'axe et bloquée par
une clé en D sur le nœud du cadre : une seule position, et la même came à gauche et à
droite. Ouvert d'un angle φ, le battant monte de `r · |φ| / 90°`. Son poids le ramène
au centre avec un couple constant, dans les deux sens, sans ressort.

Trois pentes sont fournies : r = 3,5, 4,5 (d'origine) et 5,5 mm. Le dessous du nœud du
battant n'est pas la copie d'une came, mais l'**enveloppe** des trois : pente douce
jusqu'à 60° de part et d'autre du creux, raide au-delà. Pour toute came de la gamme,
le battant s'appuie sur les lignes à ±60°, à la même hauteur au repos. Il monte donc
selon la came posée, sans rien changer d'autre. Le battant est raccourci de 5 mm en
haut pour laisser la levée maximale (5,2 mm avec la came de 5,5 mm).

La plage libre va jusqu'à ±80° ; quatre butées TPU prennent l'effort à ±85°. Le jeu
central antipincement vaut 2,4 mm.

## Verrou central

Une lame imprimée de 10 × 4 mm coulisse verticalement dans le seuil, au milieu, dans
un canal guidé à 0,2 mm (0,4 mm sur la face avant, imprimée en pont). Montée, elle entre de 4 mm dans une poche au coin bas de
chaque battant. Ces poches sont fermées devant et derrière, si bien qu'aucun battant
ne peut tourner (blocage dès 0,5°).

Un bouton vissé sur la lame (M3 × 18) sort par une fente verticale du socle. Un
**tourniquet** pivotant (M3 × 12) se tourne d'un quart de tour sous le bouton pour le
tenir en haut. Relevé, il libère le bouton et la lame retombe par son poids sous le
seuil. Un cran latéral dans la fente ne conviendrait pas : la lame, guidée, ne peut
pas se décaler sur le côté.

## Aimants anti-vent

Un aimant Ø6 × 2 affleure sous chaque battant, à 20 mm du bord libre, au-dessus d'un
autre logé dans un puits de 6 mm du seuil. Des cales de 1 mm placées sous l'aimant du
seuil règlent l'écart de 1 à 5 mm, donc la force de maintien. La bonne valeur se
trouve sur le prototype : le battant doit tenir au vent et s'ouvrir d'une poussée
légère.

## Capteur de passage et éclairage

Un aimant Ø6 × 3 en haut de chaque battant ferme un ILS logé dans le linteau, à 9 mm
au-dessus. Les deux ILS sont en série : la boucle s'ouvre dès qu'un battant s'ouvre.
Le plastique laisse passer le champ magnétique, si bien que rien n'est visible.

Les lanternes reçoivent des LED WS2812B 5 mm. Sous chaque LED, le pied de la lanterne
est creusé d'une chambre de connexion de 9 × 13,5 mm, haute de 5 mm, ouverte dessous et
vers l'arrière. Elle loge les pattes coudées, les soudures gainées et le condensateur
de 100 nF. Son toit en pointe à 45° s'imprime sans pont ni support (un toit plat
déclenchait l'avertissement « surplomb flottant » de Creality Print). Une rainure de 4,5 × 2,5 mm au dos de
chaque façade, contre la porte, mène les câbles de la lanterne et du capteur jusqu'à
un berceau imprimé sous le tunnel. Ce berceau loge un ESP32-C3 SuperMini, dont la prise
USB-C est accessible par une fenêtre de la façade arrière. La configuration ESPHome
fournie gère les lumières, le capteur, un compteur et un flash à chaque passage.

## Battants en demi-coques

Les reliefs des deux faces empêchent d'imprimer un battant entier à plat. Chaque
battant est fait de deux demi-coques multicolores, faces de collage contre le plateau.
Les pions Ø2 × 3 mm se logent dans des trous de 2,2 mm et alignent les demi-coques. Le
collage porte l'effort ; le joint nominal réservé vaut 0,1 mm. Les poches du verrou et
des aimants sont centrées sur le plan de collage, si bien que les deux demi-coques en
portent chacune la moitié.

## Fixation des façades

Quatre M4 traversent les deux façades et la porte, avec des entraxes de 214 mm
horizontalement et 146 mm verticalement. Pour une porte de 40 mm : vis de 70 mm à
tête basse (Ø ≤ 7,6 mm, hauteur ≤ 2,2 mm), rondelles Ø ≤ 8 mm et écrous ≤ 3,2 mm.
Les caches arrière sont évidés pour recevoir le bout des vis.

## Fichiers d'impression

`generate.py` construit les volumes dans Blender, en millimètres, et range les
pièces sur douze plateaux K1 Max. Il les écrit directement comme projets Creality
Print complets (imprimante, profil, couleurs, tour de purge hors des pièces), avec
des réglages par objet : couches de 0,1 mm pour les cames, bordure de 5 mm pour les
petites pièces (espacées de 13 mm pour que les bordures ne se soudent pas), supports
limités aux fourreaux d'axe. L'orientation de chaque pièce évite les surplombs : caches
tête en bas, lame du verrou et butées TPU couchées, bouton laiton évasé en cône vers sa
face, dessous du toit des lanternes en cône à 45°.

## Limites

Les paramètres de tête de fichier ne rendent pas tout adaptatif : changer la largeur
ou la hauteur du passage demande de revoir les moulures, les perçages et les
dégagements, puis de relancer les contrôles. Les contrôles portent sur des volumes
rigides à cotes nominales. Le frottement de la came, la force des aimants, le seuil
des ILS, le collage et la fatigue doivent être validés sur le prototype.
