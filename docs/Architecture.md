# Architecture d'Ohanna-Vision

## Objectif

Ohanna-Vision est l'interface d'observation et d'administration de l'écosystème **Ohanna**.

Sa mission est de transformer les observations produites par **Ohanna-Agent** en une représentation compréhensible, exploitable et durable de l'infrastructure.

Contrairement à un outil de supervision classique, Ohanna-Vision ne collecte aucune donnée directement.

Il reconstruit l'état de l'infrastructure exclusivement à partir des observations qui lui sont fournies.

---

# Principes d'architecture

L'architecture repose sur quatre principes fondamentaux :

* les observations constituent la source de vérité ;
* chaque moteur possède une responsabilité unique ;
* les objets métier sont immuables ;
* les couches supérieures ne modifient jamais les couches inférieures.

Cette séparation garantit une architecture simple, testable et évolutive.

---

# Vue d'ensemble

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
                    │
                    ▼
        Backend REST / Interface Web
```

Chaque composant possède une responsabilité clairement définie.

---

# ObservationStore

Le `ObservationStore` constitue le point d'entrée du domaine.

Il conserve les observations dans leur ordre chronologique.

Les observations sont considérées comme immuables et ne sont jamais modifiées après leur enregistrement.

Le store permet notamment :

* l'ajout d'observations ;
* la consultation de l'historique ;
* le filtrage par nœud, service ou capacité ;
* l'alimentation des différents moteurs métier.

---

# Projection Engine

Le `ProjectionEngine` reconstruit l'état courant de l'infrastructure.

Il répond à la question :

> Quel est le dernier état connu de l'infrastructure ?

Le moteur transforme les observations en objets métier :

* `CapabilityState`
* `ServiceState`
* `NodeState`
* `InfrastructureState`

La projection représente uniquement les faits connus.

Elle ne contient aucune logique métier d'interprétation.

---

# Health Engine

Le `HealthEngine` interprète les projections.

Il répond à la question :

> Quelle est la santé de l'infrastructure ?

Contrairement au `ProjectionEngine`, il applique des règles métier telles que :

* la criticité ;
* l'obsolescence des observations (*stale*) ;
* la propagation des incidents.

Son résultat est un `HealthReport` indépendant des projections.

Cette séparation permet de faire évoluer les politiques de santé sans modifier les observations ni les projections.

---

# Timeline Engine

Le `TimelineEngine` reconstruit l'évolution temporelle de l'infrastructure.

Il répond à la question :

> Comment l'état a-t-il évolué dans le temps ?

Il transforme les observations successives en périodes d'état.

Exemple :

```text
Healthy      08:00 → 08:15
Degraded     08:15 → 08:25
Healthy      08:25 → maintenant
```

Le moteur produit plusieurs niveaux de timeline :

* `CapabilityTimeline`
* `ServiceTimeline`
* `NodeTimeline`
* `InfrastructureTimeline`

Toutes reposent sur le même objet métier :

* `StatePeriod`

---

# Modèle métier

Le domaine s'articule autour de plusieurs objets fondamentaux.

## Observation

Une observation représente un fait technique observé à un instant donné.

Elle constitue la seule source de vérité du système.

---

## Projection

La projection représente le dernier état connu.

Elle est composée de :

* `CapabilityState`
* `ServiceState`
* `NodeState`
* `InfrastructureState`

---

## Santé

La santé représente l'interprétation métier de la projection.

Elle est encapsulée dans un `HealthReport`.

---

## Timeline

La timeline représente l'évolution historique d'une entité.

Elle est composée de plusieurs `StatePeriod`.

---

# Séparation des responsabilités

Les différents moteurs ne partagent pas leurs responsabilités.

## ObservationStore

Responsable du stockage.

---

## ProjectionEngine

Responsable de la reconstruction de l'état.

---

## HealthEngine

Responsable de l'évaluation métier.

---

## TimelineEngine

Responsable de la reconstruction temporelle.

---

# Dépendances

Les dépendances entre moteurs sont strictement unidirectionnelles.

```text
ObservationStore
        │
        ├──────────────┐
        │              │
        ▼              ▼
ProjectionEngine   TimelineEngine
        │
        ▼
HealthEngine
```

Le `TimelineEngine` ne dépend pas du `HealthEngine`.

Le `HealthEngine` ne dépend pas du `TimelineEngine`.

Cette indépendance permet de les utiliser séparément selon les besoins.

---

# Backend REST

La future API REST exposera les objets métier produits par les différents moteurs.

Elle ne contiendra aucune logique métier.

Son rôle sera uniquement de publier :

* les projections ;
* les rapports de santé ;
* les timelines ;
* les fonctions d'administration.

---

# Interface Web

L'interface web consommera exclusivement l'API REST.

Elle proposera notamment :

* un tableau de bord temps réel ;
* l'historique des capacités ;
* la visualisation des services ;
* la santé globale ;
* l'administration de l'infrastructure ;
* la gestion des plugins ;
* la gestion des baux DHCP ;
* la configuration des politiques de santé.

La logique métier restera entièrement dans le backend.

---

# Relation avec Ohanna-Agent

Ohanna-Agent et Ohanna-Vision sont volontairement découplés.

Le premier produit des observations.

Le second les interprète.

Cette séparation permet :

* de faire évoluer les deux projets indépendamment ;
* de connecter plusieurs agents à une même instance de Vision ;
* de préserver une architecture modulaire.

---

# État actuel de l'architecture

À l'issue de la Phase 1, le cœur métier est entièrement opérationnel.

Les composants disponibles sont :

* Domain Model ;
* Observation Store ;
* Projection Engine ;
* Health Engine ;
* Timeline Engine.

Le projet dispose actuellement de **119 tests unitaires**, tous validés, garantissant la cohérence du modèle métier avant le développement du backend et de l'interface web.
