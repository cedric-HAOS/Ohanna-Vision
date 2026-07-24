# Architecture d'Ohana-Vision

## Objectif

Ohana-Vision est l'interface d'observation et d'administration de l'écosystème **Ohana**.

Sa mission est de transformer les observations produites par **Ohana-Agent** en une représentation compréhensible, exploitable et durable de l'infrastructure.

Contrairement à un outil de supervision classique, Ohana-Vision ne collecte aucune donnée directement.

Il reçoit d'Ohana-Agent un snapshot complet de l'infrastructure ainsi que les observations qui décrivent son fonctionnement.

Le snapshot fournit la structure de référence ; les observations alimentent l'état courant, la santé et l'historique.

---

# Principes d'architecture

L'architecture repose sur cinq principes fondamentaux :

* Ohana-Agent possède la définition de l'infrastructure ;
* les observations constituent la source de vérité de l'état mesuré ;
* chaque moteur possède une responsabilité unique ;
* les objets métier sont immuables ;
* les couches supérieures ne modifient jamais les couches inférieures.

Cette séparation garantit une architecture simple, testable et évolutive.

---

# Vue d'ensemble

```text
       Snapshot d'infrastructure       Observations
                    │                       │
                    ▼                       ▼
       InfrastructureMapper        ObservationStore
                    │                 │           │
                    ▼                 ▼           ▼
                Topology      ProjectionEngine  TimelineEngine
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


# Infrastructure Mapper

Le `InfrastructureMapper` transforme le contrat reçu par `PUT /api/infrastructure` en modèles de topologie utilisés par Vision.

Il valide notamment :

* les identifiants uniques ;
* les références entre services et nœuds ;
* les références entre équipements et nœuds ;
* les extrémités des liaisons ;
* les équipements positionnés dans les layouts ;
* l'unicité des cellules de grille.

Les positions `column` / `row` sont ensuite converties en coordonnées de présentation par Vision. L'Agent ne connaît ni les marges, ni les espacements, ni les dimensions du canvas.

Le snapshot courant est remplacé atomiquement. Avant sa réception, Vision expose une topologie vide.

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

## Infrastructure Snapshot

Le snapshot représente la structure déclarée par Ohana-Agent : nœuds, services, équipements, liaisons et layouts.

Il constitue la source de vérité de la topologie affichée.

## Observation

Une observation représente un fait technique observé à un instant donné.

Elle constitue la source de vérité de l'état mesuré.

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
InfrastructureMapper ───────────────► Topology

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

L'API REST expose les contrats d'ingestion et les objets projetés par le backend.

Elle ne déplace aucune logique métier dans les routeurs. Ceux-ci assurent principalement :

* la validation des requêtes ;
* l'ingestion du snapshot d'infrastructure ;
* l'ingestion des observations ;
* la publication de la topologie ;
* la publication des projections, rapports de santé et timelines ;
* l'exposition de l'état du runtime.

---

# Interface Web

L'interface web consomme exclusivement les API REST et le WebSocket de Vision.

Elle propose actuellement :

* un tableau de bord temps réel ;
* la topologie dynamique ;
* la visualisation des services et des équipements ;
* la santé globale ;
* les observations ;
* la timeline des périodes métier.

Les fonctions d'administration, de gestion des plugins et d'actions contrôlées restent des évolutions futures. La logique métier demeure dans le backend et, pour les opérations sur l'infrastructure, dans Ohana-Agent.

---

# Relation avec Ohana-Agent

Ohana-Agent et Ohana-Vision sont découplés par des contrats HTTP versionnés.

L'Agent :

* possède la configuration de l'infrastructure ;
* transmet le snapshot complet ;
* exécute les observations ;
* suspend leur production lorsque Vision n'est plus synchronisé.

Vision :

* valide et projette le snapshot ;
* conserve les observations ;
* calcule les états, la santé et les périodes ;
* expose les résultats à l'interface.

Cette séparation permet de faire évoluer les deux projets indépendamment tout en conservant une source de vérité unique.

---

# État actuel de l'architecture

La version 1.1.0 dispose notamment de :

* Domain Model ;
* Infrastructure Mapper ;
* Topology Models ;
* Observation Store ;
* Projection Engine ;
* Health Engine ;
* Timeline Engine ;
* API REST ;
* WebSocket ;
* frontend modulaire et responsive.

La suite complète contient **745 tests validés**. Les scénarios réels de démarrage dans les deux ordres, de perte de Vision et d'arrêt pendant la resynchronisation ont également été vérifiés.
