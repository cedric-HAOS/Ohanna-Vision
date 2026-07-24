# Charte graphique Ohana

## 1. Positionnement

Ohana représente une infrastructure observable, résiliente et pilotée par capacités.
L’identité visuelle associe un cercle continu, des circuits et des nœuds interconnectés.

## 2. Logo

Le symbole principal est un cercle réseau composé de pistes électroniques et de trois nœuds.
Le mot-symbole « Ohana » utilise une typographie sans serif moderne et sobre.

### Variantes

- `logo-dark.svg` : fond sombre, texte clair.
- `logo-light.svg` : fond clair, texte sombre.
- `logo.svg` : variante générique.
- `favicon.svg` : symbole seul.
- `favicon.ico` : compatibilité navigateurs.
- `apple-touch-icon.png` : raccourci iOS.
- `icon-192.png` et `icon-512.png` : PWA.

### Zone de protection

Conserver autour du logo un espace libre au moins égal à 25 % de la hauteur du symbole.
Ne pas étirer, incliner, recolorer ou ajouter d’effets au logo.

## 3. Palette

| Usage | Nom | Hex |
|---|---|---|
| Primaire | Cyan Ohana | `#18C5E8` |
| Secondaire | Bleu Ohana | `#1479D1` |
| Accent | Turquoise | `#4DE6C8` |
| Fond principal | Nuit | `#0F172A` |
| Surface | Ardoise | `#1E293B` |
| Texte clair | Neige | `#F8FAFC` |
| Texte secondaire | Brume | `#94A3B8` |
| Succès | Vert | `#22C55E` |
| Avertissement | Ambre | `#F59E0B` |
| Critique | Rouge | `#EF4444` |

## 4. Typographie

Police recommandée : `Inter`.
Alternative système : `Segoe UI`, `Arial`, sans-serif.

- Titres : 600 à 700.
- Corps : 400 à 500.
- Données et métriques : 500 à 600.
- Éviter les capitales intégrales hors libellés très courts.

## 5. Interface

- Fond principal sombre : `#0F172A`.
- Surfaces : `#1E293B`.
- Accent principal : `#18C5E8`.
- États de santé : vert, ambre, rouge.
- Rayon recommandé : 12 à 16 px.
- Ombres discrètes et contrastes accessibles.

## 6. Intégration HTML

```html
<link rel="icon" href="/ui/favicon.ico" sizes="any">
<link rel="icon" href="/ui/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/ui/apple-touch-icon.png">
<link rel="manifest" href="/ui/site.webmanifest">
<meta name="theme-color" content="#18C5E8">
```

## 7. Packaging Python

Ajouter les motifs suivants à `pyproject.toml` :

```toml
[tool.setuptools.package-data]
ohana_vision = [
    "web/static/*.html",
    "web/static/*.css",
    "web/static/*.js",
    "web/static/*.ico",
    "web/static/*.svg",
    "web/static/*.png",
    "web/static/*.webmanifest",
    "web/static/styles/*.css",
]
```
