# Ohanna-Vision

> Transformer des observations techniques en une vision compréhensible de l'infrastructure.

## Présentation

Ohanna-Vision est l'interface d'observation et d'administration de l'écosystème **Ohanna**.

Contrairement à un outil de supervision traditionnel, Ohanna-Vision ne collecte pas directement les informations techniques.

Il s'appuie sur les observations produites par **Ohanna-Agent** afin de reconstruire une représentation complète de l'infrastructure, d'évaluer sa santé et de présenter son évolution dans le temps.

L'objectif est de fournir une vue claire, cohérente et durable des capacités de l'infrastructure, indépendamment des équipements qui les réalisent.

---

# Philosophie

Une infrastructure fiable n'est pas uniquement une infrastructure qui fonctionne.

C'est une infrastructure dont les capacités sont connues, comprises et suivies dans le temps.

Ohanna-Vision transforme les observations techniques en informations exploitables.

Il distingue volontairement plusieurs niveaux d'abstraction :

* les faits ;
* l'état courant ;
* l'interprétation métier ;
* l'évolution temporelle.

Cette séparation permet de faire évoluer l'interface sans modifier les modèles métier.

---

# Architecture

```text
                    Observations
                           │
                           ▼
                  ObservationStore
                    │           │
                    │           │
                    ▼           ▼
          ProjectionEngine   TimelineEngine
                    │           │
                    ▼           ▼
       InfrastructureState  InfrastructureTimeline
                    │
                    ▼
               HealthEngine
                    │
                    ▼
                HealthReport
```

Chaque moteur possède une responsabilité unique.

* **ObservationStore** conserve les observations.
* **ProjectionEngine** reconstruit l'état courant.
* **HealthEngine** interprète cet état.
* **TimelineEngine** reconstruit son évolution.

---

# Fonctionnalités

## Observation Store

* stockage immuable des observations ;
* consultation chronologique ;
* base de tous les traitements.

## Projection Engine

Reconstruit automatiquement :

* les capacités ;
* les services ;
* les nœuds ;
* l'infrastructure complète.

## Health Engine

Évalue :

* la santé des capacités ;
* la criticité ;
* l'obsolescence des observations ;
* la propagation des incidents.

## Timeline Engine

Construit l'historique temporel sous forme de périodes d'état :

```text
Healthy      08:00 → 08:15
Degraded     08:15 → 08:25
Healthy      08:25 → maintenant
```

---

# Interface d'administration

À terme, Ohanna-Vision ne sera pas uniquement un tableau de bord.

Il constituera également une interface d'administration de l'écosystème Ohanna.

Les fonctionnalités envisagées comprennent notamment :

* gestion des plugins Ohanna-Agent ;
* import et mise à jour de plugins ;
* consultation et édition de la configuration ;
* gestion des baux DHCP statiques ;
* consultation des baux DHCP actifs ;
* visualisation des capacités disponibles ;
* supervision des services et des nœuds ;
* gestion des politiques de santé.

---

# Relation avec Ohanna-Agent

Ohanna-Agent produit des observations.

Ohanna-Vision les exploite.

Les deux projets restent volontairement indépendants.

Cette séparation permet :

* de faire évoluer l'interface sans modifier l'agent ;
* d'utiliser plusieurs agents simultanément ;
* de conserver une architecture modulaire.

---

# État du projet

Version actuelle :

* Domaine métier : ✅
* Observation Store : ✅
* Projection Engine : ✅
* Health Engine : ✅
* Timeline Engine : ✅
* Interface d'administration : en préparation
* Backend REST : à venir
* Interface Web : à venir

---

# Feuille de route

## Phase 0

* Vision
* Architecture
* Modèles métier
* Documentation

**Statut : terminée**

## Phase 1

* Domain Model
* Observation Store
* Projection Engine
* Health Engine
* Timeline Engine

**Statut : terminée**

## Phase 2

* Administration Model
* Backend Runtime
* API REST
* Démonstration console

## Phase 3

* Interface Web
* Tableau de bord temps réel
* Historique
* Administration

## Phase 4

* Intégration Home Assistant

---

# Documentation

La documentation d'architecture est disponible dans le répertoire :

```text
docs/
```

Les principales décisions d'architecture sont documentées dans les ADR :

* ADR-0000 — Vision d'Architecture
* ADR-0001 — Projection Engine
* ADR-0002 — Health Engine

---

# Tests

Le projet est entièrement développé selon une approche **Test-Driven Development (TDD)**.

Chaque composant est accompagné de tests unitaires.

État actuel :

```text
119 tests
100 % réussis
```

---

# Licence

Ce projet est distribué sous licence MIT.

Voir le fichier `LICENSE`.

---

# Vision

Ohanna-Vision n'est pas un simple tableau de bord.

C'est la représentation vivante d'une infrastructure.

Les observations constituent la source de vérité.

Les projections décrivent cette vérité.

La santé en est l'interprétation métier.

La timeline raconte son évolution.

L'interface permet enfin de comprendre, d'administrer et de piloter l'ensemble de l'infrastructure Ohanna.
