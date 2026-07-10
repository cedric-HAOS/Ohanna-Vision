# Roadmap

## Vision

Une infrastructure fiable n'est pas uniquement une infrastructure qui fonctionne.

C'est une infrastructure dont les capacités sont connues, comprises et administrables dans le temps.

Ohanna-Agent produit des observations.

Ohanna-Vision les transforme en une représentation complète de l'infrastructure, de sa santé et de son évolution.

À terme, Ohanna-Vision deviendra également l'interface d'administration de l'ensemble de l'écosystème Ohanna.

---

# État du projet

| Phase                                |   Statut   |
| ------------------------------------ | :--------: |
| Phase 0 — Architecture               | ✅ Terminée |
| Phase 1 — Domaine métier             | ✅ Terminée |
| Phase 2 — Backend                    | 🚧 À venir |
| Phase 3 — Interface Web              |  📅 Prévue |
| Phase 4 — Intégration Home Assistant |  📅 Prévue |

---

# Phase 0 — Architecture

## Objectif

Définir les fondations fonctionnelles et techniques du projet.

### Réalisé

* Vision du projet
* Architecture générale
* Modèle des observations
* Modèle de santé
* Documentation
* ADR-0000 — Vision d'Architecture

**Statut : terminé**

---

# Phase 1 — Domaine métier

## Objectif

Construire l'ensemble du modèle métier indépendamment de toute interface utilisateur.

### 1.1 Domain Model

* Observation
* Health
* CapabilityState
* ServiceState
* NodeState
* InfrastructureState
* Criticality

### 1.2 Observation Store

* stockage immuable
* historique
* filtrage
* consultation

### 1.3 Projection Engine

* reconstruction automatique de l'état courant
* agrégation des capacités
* projection des services
* projection des nœuds
* projection globale

ADR-0001 — Projection Engine

### 1.4 Health Engine

* interprétation métier
* criticité
* obsolescence
* propagation des états
* HealthReport

ADR-0002 — Health Engine

### 1.5 Timeline Engine

* StatePeriod
* CapabilityTimeline
* ServiceTimeline
* NodeTimeline
* InfrastructureTimeline
* TimelineEngine

**Statut : terminé**

---

# Phase 2 — Backend

## Objectif

Construire le backend de Ohanna-Vision et exposer le domaine métier via une API REST.

### 2.1 Administration Model

Création des modèles d'administration :

* Plugin
* PluginRepository
* PluginPackage
* InfrastructureConfiguration
* DHCPReservation
* DHCPLease
* HealthPolicy
* AdministrationCommand

### 2.2 Backend Runtime

* cycle de vie de l'application
* configuration
* injection des moteurs métier
* services internes
* gestion des erreurs

### 2.3 API REST

Première version de l'API.

Exposition de :

* observations
* projections
* santé
* timelines
* administration

### 2.4 Démonstration console

Application minimale permettant de :

* charger des observations ;
* reconstruire l'infrastructure ;
* afficher la santé ;
* afficher les timelines.

### 2.5 Audit & Release

* audit de cohérence
* documentation
* tests
* première version du backend

---

# Phase 3 — Interface Web

## Objectif

Créer une interface moderne permettant d'observer et d'administrer l'infrastructure.

### Tableau de bord

* santé globale
* capacités
* services
* nœuds
* infrastructure

### Historique

* timelines
* transitions
* durée des états
* incidents

### Administration

* configuration
* plugins
* politiques de santé
* réservations DHCP
* baux DHCP
* services disponibles

### Temps réel

* mise à jour automatique
* notifications
* événements

---

# Phase 4 — Intégration Home Assistant

## Objectif

Intégrer Ohanna-Vision dans l'écosystème Home Assistant.

### Fonctionnalités

* entités Home Assistant
* tableaux de bord
* événements
* services
* navigation entre Vision et Home Assistant

---

# Principes d'évolution

Toutes les évolutions respecteront les principes suivants :

* les observations restent la source de vérité ;
* les objets métier sont immuables ;
* chaque moteur possède une responsabilité unique ;
* les interfaces ne contiennent aucune logique métier ;
* les fonctionnalités d'administration restent découplées du moteur d'observation.

---

# Vision à long terme

À terme, Ohanna-Vision deviendra le point d'entrée unique de l'écosystème Ohanna.

Il permettra :

* d'observer l'infrastructure en temps réel ;
* de comprendre son évolution ;
* d'évaluer sa santé ;
* d'administrer les services ;
* de gérer les plugins ;
* de piloter les capacités de l'infrastructure depuis une interface web unique.

Le cœur métier restera indépendant de toute technologie d'interface afin de garantir la pérennité du projet.
