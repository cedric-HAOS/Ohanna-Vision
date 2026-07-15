# CHANGELOG

Toutes les évolutions importantes du projet sont documentées dans ce fichier.

Le projet suit les principes de Semantic Versioning.

---

# v0.4.0 — Frontend modulaire et Timeline métier

## Ajouté

### Frontend modulaire

- Découpage complet du JavaScript en modules spécialisés.
- Introduction d'un `ApplicationController` responsable de l'orchestration.
- Centralisation de l'état partagé dans `application_state.js`.
- Séparation des contrôleurs :
  - Dashboard
  - Navigation
  - Topologie
  - Timeline
  - Observations
  - Détails des équipements
  - WebSocket

### CSS modulaire

Découpage complet de la feuille de style en modules indépendants :

- foundations.css
- layout.css
- components.css
- dashboard.css
- topology.css
- timeline.css
- observations.css
- device-details.css
- responsive.css

### Navigation

- Navigation latérale entièrement modulaire.
- Synchronisation avec l'URL (`location.hash`).
- Conservation de la vue active.
- Vue d'ensemble regroupant dashboard, topologie et timeline.

### Timeline

Refonte complète de la timeline.

Le frontend n'utilise plus les observations pour reconstruire l'historique.

La timeline repose désormais sur les périodes métier calculées par le backend.

Ajouts :

- modèle JavaScript `TimelinePeriod`
- rendu par périodes
- compteur de périodes
- affichage des périodes par nœud
- simplification importante du contrôleur Timeline

### Dashboard

- restauration complète de la vue d'ensemble
- intégration de la topologie
- intégration de la timeline
- amélioration du responsive
- optimisation des proportions du tableau de bord

### Qualité

- suppression du code mort
- suppression des anciens styles de timeline
- suppression des anciens regroupements d'observations
- suppression des logs JavaScript de production
- amélioration des messages d'erreur utilisateur

---

## Modifié

### Architecture Frontend

Le frontend devient un moteur de visualisation.

Toute la logique métier est désormais calculée côté backend.

Le navigateur ne reconstruit plus les modèles métier.

### Timeline

Abandon définitif du pipeline :

```
Observation
    ↓
Javascript
    ↓
Regroupement
```

au profit de :

```
Observation
    ↓
TimelineEngine
    ↓
StatePeriod
    ↓
API
    ↓
TimelinePeriod
    ↓
Frontend
```

### Interface

- amélioration de la disposition générale
- meilleure séparation des responsabilités
- simplification de la navigation
- amélioration de la cohérence visuelle

---

## Supprimé

- ancien rendu fondé sur les observations
- `renderEvent()`
- `renderRow()`
- `groupObservationsByNode()`
- `groupPeriodsByNode()`
- `isObservationVisible()`
- styles `timeline-event`
- compteur d'événements
- logs JavaScript de production

---

## Qualité

- 620 tests unitaires
- validation complète du responsive
- audit du frontend
- audit du CSS
- audit de la timeline
- audit d'hygiène du dépôt