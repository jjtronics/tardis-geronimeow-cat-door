# Contributing / Contribuer

**English below.**

## Français

Le plus utile aujourd'hui, ce sont des **retours d'impression** : la chatière n'a pas
encore été imprimée.

- **Retour d'impression** : ouvrez une issue « Retour d'impression » avec votre
  imprimante, le filament, le plateau imprimé, ce qui s'ajuste bien ou mal, et des
  photos. Les résultats de l'éprouvette (`00_Eprouvette_jeux`) sont précieux.
- **Problème** : un plateau qui affiche un avertissement, une pièce qui ne s'assemble
  pas, une erreur dans la doc : ouvrez une issue « Problème ».
- **Modification** : la géométrie vient de `tardis_v8/generate.py`. Ne retouchez pas
  les STL ou 3MF à la main : changez le générateur, régénérez, puis lancez les
  contrôles décrits dans [docs/DEVELOPPEMENT.md](docs/DEVELOPPEMENT.md)
  (`verify_geometry.py`, `verify_3mf.py`, `trancher_creality_print.py`,
  `audit_tours.py`). Mentionnez leurs résultats dans la pull request.
- **Remix** : bienvenu, sous CC BY-NC-SA 4.0 (non commercial, même licence, en citant ce
  dépôt). Voir [LICENSE.md](LICENSE.md).

## English

The most useful contribution right now is a **print report**: the cat flap has not
been printed yet.

- **Print report**: open a "Print report" issue with your printer, filament, the plate
  you printed, what fits well or badly, and photos. Results from the test coupon
  (`00_Eprouvette_jeux`) are especially valuable.
- **Problem**: a plate that shows a slicer warning, a part that does not fit, a doc
  mistake: open a "Problem" issue.
- **Changes**: the geometry comes from `tardis_v8/generate.py`. Do not edit STL or 3MF
  files by hand: change the generator, regenerate, then run the checks listed in
  [docs/DEVELOPPEMENT.md](docs/DEVELOPPEMENT.md) (`verify_geometry.py`,
  `verify_3mf.py`, `trancher_creality_print.py`, `audit_tours.py`) and include their
  results in your pull request.
- **Remixes** are welcome under CC BY-NC-SA 4.0 (non-commercial, same license, credit
  this repository). See [LICENSE.md](LICENSE.md).

Issues and pull requests can be written in French or English.
