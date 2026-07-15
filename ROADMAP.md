# ROADMAP

## Vision

Ohanna-Vision est l'interface de visualisation d'Ohanna.

Son objectif est de représenter l'état réel des capacités d'une infrastructure, leur évolution dans le temps et leurs dépendances.

Le frontend est volontairement simple.

Toute la logique métier est calculée par le backend.

---

# Phase 3 — Dashboard interactif

## 3.1

- Domaine Web
- Observation Store
- Projection Engine
- Health Engine
- Timeline Engine

**Statut :** ✅ Terminé

---

## 3.2

- Runtime Backend
- Observation Processor
- API REST
- WebSocket

**Statut :** ✅ Terminé

---

## 3.3

- Dashboard
- KPI
- Runtime
- Alertes

**Statut :** ✅ Terminé

---

## 3.4

- Topologie interactive
- Sélection des équipements
- Panneau de détails

**Statut :** ✅ Terminé

---

## 3.5

- Navigation
- Frontend modulaire
- CSS modulaire
- Timeline fondée sur les périodes métier
- Responsive
- Audit frontend

**Statut :** ✅ Terminé

---

# Phase 4 — Administration

L'objectif de cette phase est de permettre l'administration de l'infrastructure depuis Ohanna-Vision.

## 4.1 Infrastructure

- consultation de la configuration
- modification des nœuds
- modification des services
- validation de configuration

## 4.2 Capacités

- vue détaillée d'une capacité
- historique complet
- dépendances
- statistiques

## 4.3 Observations

- recherche
- filtrage
- export

## 4.4 Plugins

- liste des plugins installés
- informations
- configuration

## 4.5 Runtime

- informations système
- santé des composants
- diagnostics

---

# Phase 5 — Historique

## 5.1 Timeline

- zoom temporel
- navigation
- agrégation

## 5.2 Historique

- recherche
- comparaison
- évolution d'une capacité

## 5.3 Rapports

- disponibilité
- SLA
- export PDF
- export CSV

---

# Phase 6 — Administration avancée

## 6.1 Utilisateurs

- authentification
- rôles
- permissions

## 6.2 Configuration

- paramètres globaux
- préférences utilisateur

## 6.3 Notifications

- événements
- alertes
- Webhooks

---

# Phase 7 — Écosystème Ohanna

## 7.1 Ohanna-Agent

- supervision multi-agents
- vue consolidée

## 7.2 Ohanna-SDK

- informations plugins
- documentation intégrée

## 7.3 Ohanna-CLI

- intégration des diagnostics
- lancement d'actions

---

# Objectif v1.0

La version 1.0 sera atteinte lorsque Ohanna-Vision permettra :

- de visualiser l'état courant d'une infrastructure ;
- d'explorer son historique ;
- d'administrer sa configuration ;
- d'analyser les capacités supervisées ;
- de fonctionner entièrement avec Ohanna-Agent.