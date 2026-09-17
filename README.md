# Recomposition de la brochure St-Maurice

Ce projet contient un petit script Python qui recompose un scan de brochure A5.

Le document source a été scanné sur des feuilles A4, avec deux pages A5 par
feuille. Les pages sont tournées de 90 degrés et disposées selon l'imposition
classique d'une brochure pliée. Le script :

- extrait la couverture depuis la **deuxième page** du PDF source ;
- ignore les deux premières feuilles dans la recomposition des pages intérieures ;
- découpe les 16 feuilles restantes en pages A5 portrait ;
- remet les pages numérotées dans l'ordre 1, 2, 3, ..., 31 ;
- conserve, par défaut, la page blanche finale ;
- produit un nouveau fichier PDF sans modifier le fichier source.

## Fichiers

- `recompose_brochure.py` : script de recomposition ;
- `Brochure St-Maurice.pdf` : PDF scanné original ;
- `Brochure St-Maurice_recompose.pdf` : PDF recomposé produit par le script.

Le PDF recomposé par défaut contient :

1. la couverture issue de la deuxième page du PDF source ;
2. les pages A5 numérotées de 1 à 31 ;
3. la page A5 blanche finale.

Il contient donc normalement **33 pages**.

## Prérequis

Python 3 et la bibliothèque [PyMuPDF](https://pymupdf.readthedocs.io/) sont
nécessaires.

Vérifier que Python est disponible :

```bash
python3 --version
```

Installer PyMuPDF si nécessaire :

```bash
python3 -m pip install PyMuPDF
```

Le script importe PyMuPDF avec :

```python
import pymupdf
```

## Utilisation rapide

Placer le script dans le même dossier que le PDF source, puis exécuter :

```bash
python3 recompose_brochure.py "Brochure St-Maurice.pdf"
```

Le fichier suivant est alors créé automatiquement :

```text
Brochure St-Maurice_recompose.pdf
```

Le nom est construit à partir du nom du fichier d'entrée : le suffixe
`_recompose` est ajouté avant l'extension `.pdf`.

## Choisir le nom du fichier de sortie

Un deuxième argument permet de choisir explicitement le fichier de sortie :

```bash
python3 recompose_brochure.py \
  "Brochure St-Maurice.pdf" \
  "Brochure St-Maurice-final.pdf"
```

Le fichier source et le fichier de sortie doivent être différents. Le script
refuse d'écraser directement le PDF original.

## Options

### Ne pas conserver la page blanche finale

La page blanche provenant de la moitié gauche de la première feuille intérieure
est conservée par défaut à la fin du document. Pour la supprimer :

```bash
python3 recompose_brochure.py \
  "Brochure St-Maurice.pdf" \
  "Brochure St-Maurice-sans-page-blanche.pdf" \
  --no-blank
```

Avec cette option, le PDF contient normalement 32 pages : la couverture et les
31 pages numérotées.

### Ne pas ajouter la couverture

Pour produire uniquement les pages intérieures :

```bash
python3 recompose_brochure.py \
  "Brochure St-Maurice.pdf" \
  "Brochure St-Maurice-interieur.pdf" \
  --no-cover
```

Cette option produit normalement 32 pages si la page blanche finale est
conservée, ou 31 pages avec `--no-cover --no-blank`.

Les options peuvent être combinées :

```bash
python3 recompose_brochure.py \
  "Brochure St-Maurice.pdf" \
  "Brochure St-Maurice-pages.pdf" \
  --no-cover \
  --no-blank
```

Afficher l'aide complète :

```bash
python3 recompose_brochure.py --help
```

## Organisation du PDF source

Le script est adapté au fichier source utilisé pour cette brochure :

- pages PDF 1 et 2 : feuilles de couverture ;
- pages PDF 3 à 18 : 16 feuilles A4 contenant les pages intérieures ;
- chaque page PDF est tournée de 90 degrés ;
- après rotation horaire, la moitié inférieure du scan devient la page de gauche
  et la moitié supérieure devient la page de droite.

Les pages intérieures sont imposées ainsi :

```text
feuille 1  : page blanche et page 1
feuille 2  : page 2       et page 31
feuille 3  : page 30      et page 3
feuille 4  : page 4       et page 29
feuille 5  : page 28      et page 5
...
feuille 15 : page 18      et page 15
feuille 16 : page 16      et page 17
```

Le script ne se contente donc pas de lire les feuilles dans l'ordre. Il applique
l'ordre de lecture correspondant à la brochure pliée :

```text
1, 2, 3, 4, ..., 15, 16, 17, 18, ..., 30, 31
```

La page blanche de la première feuille est déplacée à la fin, où elle
correspond à la dernière page physique non numérotée de la brochure.

## Fonctionnement technique

La fonction `add_half()` :

1. lit les dimensions de la page source ;
2. découpe la page selon son axe central ;
3. sélectionne la moitié gauche ou droite après rotation ;
4. crée une page A5 portrait de dimensions adaptées au scan ;
5. insère la portion originale avec `show_pdf_page()`.

Le contenu PDF est inséré directement, plutôt que converti en une nouvelle
image raster. Cela évite une perte de qualité inutile et conserve une taille de
page adaptée au document A5.

La fonction `page_order()` construit l'ordre des pages numérotées à partir de
l'imposition observée dans le scan.

## Contrôles effectués par le script

Le script vérifie notamment que :

- le fichier de sortie est différent du fichier source ;
- le PDF possède 16 feuilles après les deux feuilles de couverture ;
- le nombre de pages correspond à la structure attendue pour les pages 1 à 31.

Si le PDF source possède un autre nombre de pages, le script s'arrête avec un
message d'erreur plutôt que de produire un document probablement incorrect.

## Vérification manuelle recommandée

Après génération, ouvrir le PDF recomposé et contrôler :

1. la première page : elle doit être la couverture provenant de la deuxième
   page du PDF source ;
2. la page suivante : elle doit porter le numéro 1 en bas ;
3. les pages suivantes : les numéros doivent progresser de 1 à 31 sans saut ni
   inversion ;
4. la dernière page : elle doit être blanche si `--no-blank` n'a pas été utilisé ;
5. l'orientation : chaque page doit être lisible en format A5 portrait.

Une vérification rapide du nombre de pages peut être faite avec Python :

```bash
python3 - <<'PY'
import pymupdf

document = pymupdf.open("Brochure St-Maurice_recompose.pdf")
print(f"Nombre de pages : {document.page_count}")
document.close()
PY
```

Le résultat attendu avec les options par défaut est :

```text
Nombre de pages : 33
```

## Adapter le script à un autre scan

Le script est spécifiquement réglé pour cette brochure. Pour un autre scan, il
peut être nécessaire de modifier :

### Nombre de feuilles de couverture

La constante suivante indique combien de pages source sont réservées aux
couvertures :

```python
COVER_SHEETS = 2
```

### Page utilisée pour la couverture

Les index Python commencent à zéro. La deuxième page du PDF correspond donc à
l'index `1` :

```python
BEST_COVER_SHEET = 1
```

Si la meilleure couverture est située sur une autre page source, modifier cette
valeur.

### Ordre des pages

La fonction `page_order()` dépend de la disposition physique des pages dans le
scan. Si les pages sont imposées différemment, cette fonction doit être adaptée.
Il faut également vérifier le sens de rotation dans `add_half()` :

```python
page.show_pdf_page(page.rect, source, source_index, clip=clip, rotate=270)
```

Une rotation `90` au lieu de `270` peut être nécessaire si le scanner a tourné
les feuilles dans l'autre sens.

### Nombre de pages intérieures

Dans la version actuelle, le script attend exactement 16 feuilles après les
couvertures :

```python
if spread_count != 16:
```

Cette vérification doit être revue pour une brochure ayant un autre nombre de
feuilles ou de pages.

## Licence et usage

Ce script est un outil local de traitement du PDF. Il ne modifie pas le scan
original et ne nécessite aucune connexion réseau.
