# ROADMAP

## Vision

Une infrastructure fiable n'est pas uniquement une infrastructure qui fonctionne.

C'est une infrastructure dont les capacités sont garanties dans le temps.

Ohanna-Vision ne supervise pas les équipements.

Il présente l'état réel des capacités observées par Ohanna-Agent afin de permettre une compréhension immédiate de la santé de l'infrastructure et de son évolution.

Le projet poursuit un objectif unique :

> Transformer des observations techniques en une vision claire, historique et temps réel des capacités de l'infrastructure.

---

# Phase 1 — Domaine, moteurs et backend Web

**Statut : Terminée ✅**

Cette première phase a permis de construire l'ensemble des fondations d'Ohanna-Vision.

## Domaine

* [x] 1.1 Domain Model
* [x] Observation
* [x] HealthStatus
* [x] Validation métier

## Stockage

* [x] 1.2 Observation Store
* [x] Historique
* [x] Filtres
* [x] Détection des doublons

## Moteurs

* [x] 1.3 Projection Engine
* [x] 1.4 Health Engine
* [x] 1.5 Timeline Engine
* [x] StatePeriod
* [x] CapabilityTimeline
* [x] ServiceTimeline
* [x] NodeTimeline
* [x] InfrastructureTimeline

## Runtime

* [x] BackendRuntime
* [x] RuntimeStatistics
* [x] RuntimeSnapshot
* [x] ObservationProcessor

## Backend Web

* [x] FastAPI
* [x] API REST
* [x] Runtime API
* [x] Observation API
* [x] Timeline API
* [x] WebSocket
* [x] Application Context
* [x] Bootstrap de production

## Interface Web

* [x] Tableau de bord HTML
* [x] CSS
* [x] JavaScript natif
* [x] Connexion WebSocket

---

# Phase 2 — Intégration avec Ohanna-Agent

**Objectif**

Recevoir les observations produites par Ohanna-Agent en temps réel.

## 2.1 Connecteur Agent

* [x] Client de réception des observations
* [x] Validation des messages
* [x] Gestion des erreurs

## 2.2 Ingestion

* [x] Injection automatique dans l'Observation Store
* [x] Mise à jour du Projection Engine
* [x] Mise à jour du Health Engine
* [x] Mise à jour du Timeline Engine

## 2.3 Temps réel

* [x] GET /api/runtime enrichi
* [x] Connecter ObservationProcessor à TimelineRuntime
* [ ] Notification temps réel lors d'une ingestion
* [ ] Tests d'intégration REST ↔ WebSocket

---

# Phase 3 — Dashboard

**Objectif**

Construire une interface de supervision exploitable au quotidien.

## Vue Infrastructure

* [ ] Santé globale
* [ ] Historique des changements
* [ ] Derniers événements

## Vue Nœuds

* [ ] Santé par machine
* [ ] Services actifs
* [ ] Capacités

## Vue Services

* [ ] Historique
* [ ] Latence
* [ ] Disponibilité

## Timeline

* [ ] Navigation temporelle
* [ ] Zoom
* [ ] Filtres
* [ ] Recherche

---

# Phase 4 — Administration

**Objectif**

Administrer l'infrastructure directement depuis Ohanna-Vision.

## Configuration

* [ ] Gestion des nœuds
* [ ] Gestion des services
* [ ] Capacités

## Administration

* [ ] Déploiement de configuration
* [ ] Validation
* [ ] Rechargement

## Supervision

* [ ] Gestion des agents connectés
* [ ] Informations système
* [ ] Diagnostics

---

# Phase 5 — Historique

**Objectif**

Conserver les observations sur le long terme.

* [ ] Persistance
* [ ] Archivage
* [ ] Recherche historique
* [ ] Statistiques
* [ ] Tendances
* [ ] Rapports

---

# Phase 6 — Visualisation avancée

**Objectif**

Transformer les données en véritable outil d'analyse.

* [ ] Graphiques temporels
* [ ] Heatmaps
* [ ] Disponibilité
* [ ] Évolution des capacités
* [ ] Analyse des incidents
* [ ] Corrélations

---

# Phase 7 — Écosystème Ohanna

**Objectif**

Faire d'Ohanna-Vision le centre de visualisation de l'écosystème.

* [ ] Intégration complète avec Ohanna-Agent
* [ ] API publique
* [ ] Notifications
* [ ] Export des données
* [ ] Authentification
* [ ] Gestion des utilisateurs

---

# Objectif de la prochaine release

## v0.2.0

Connexion temps réel avec Ohanna-Agent :

* réception automatique des observations ;
* mise à jour immédiate des moteurs ;
* diffusion WebSocket des événements ;
* tableau de bord réellement vivant.

---

# État actuel

* Version : **v0.1.0**
* Phase 1 : **Terminée**
* Couverture : **270 tests unitaires**
* Qualité : **Ruff sans erreur**
* Interface Web : **Opérationnelle**
* API REST : **Opérationnelle**
* WebSocket : **Opérationnel**
* Bootstrap : **Opérationnel**
