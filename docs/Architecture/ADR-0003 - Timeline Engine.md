# ADR-0003 — Timeline Engine

**Statut :** Accepté

**Date :** 2026-07-10

---

# Contexte

Ohanna-Vision reçoit un flux continu d'observations provenant d'Ohanna-Agent.

Ces observations permettent de reconstruire l'état courant de l'infrastructure grâce au `ProjectionEngine`.

Elles permettent également d'évaluer sa santé grâce au `HealthEngine`.

En revanche, ces deux moteurs ne répondent pas à une question essentielle :

> Comment l'infrastructure a-t-elle évolué dans le temps ?

Cette information est indispensable pour :

* afficher un historique des incidents ;
* mesurer la durée des états ;
* reconstruire une chronologie ;
* produire des graphiques temporels ;
* alimenter le futur tableau de bord.

Un moteur dédié est donc nécessaire.

---

# Décision

Ohanna-Vision introduit un moteur indépendant nommé **TimelineEngine**.

Sa responsabilité est unique :

> Transformer une succession chronologique d'observations en périodes d'état.

Le TimelineEngine ne réalise aucune interprétation métier.

Il ne calcule pas la santé.

Il ne connaît pas la criticité.

Il ne modifie jamais les observations.

Il se contente de reconstruire fidèlement l'évolution temporelle des états observés.

---

# Architecture

Le TimelineEngine fait partie des moteurs principaux du domaine.

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

Le TimelineEngine dépend uniquement des observations.

Il ne dépend ni du ProjectionEngine ni du HealthEngine.

---

# Objet métier fondamental

Le TimelineEngine repose sur un nouvel objet métier :

```text
StatePeriod
```

Un `StatePeriod` représente une période continue pendant laquelle une entité conserve le même état.

Exemple :

```text
Healthy

08:00

↓

08:15
```

Il est composé de :

* un `HealthStatus` ;
* une date de début ;
* une date de fin éventuelle.

Une période ouverte représente l'état courant.

---

# Timelines

Le TimelineEngine construit une hiérarchie complète de timelines.

## CapabilityTimeline

Historique d'une capacité.

```text
DNS Resolve

Healthy

↓

Degraded

↓

Healthy
```

---

## ServiceTimeline

Historique d'un service.

Construit à partir des timelines de ses capacités.

---

## NodeTimeline

Historique d'un nœud.

Construit à partir des timelines de ses services.

---

## InfrastructureTimeline

Historique complet de l'infrastructure.

Construit à partir des timelines des nœuds.

---

# Construction des périodes

Les observations successives possédant le même état sont fusionnées.

Exemple :

```text
Healthy
08:00

Healthy
08:05

Healthy
08:10
```

devient :

```text
Healthy

08:00

↓

08:10
```

Une nouvelle période est créée uniquement lorsqu'un changement d'état est observé.

---

# Agrégation hiérarchique

Les timelines des services, des nœuds et de l'infrastructure sont obtenues par agrégation des timelines de niveau inférieur.

À chaque instant, le statut retenu est le plus sévère parmi les enfants actifs.

Ordre de sévérité :

```text
HEALTHY

↓

UNKNOWN

↓

STALE

↓

DEGRADED

↓

UNAVAILABLE
```

Cette agrégation est purement factuelle.

Elle ne prend pas en compte la criticité métier.

Cette responsabilité reste celle du `HealthEngine`.

---

# Séparation des responsabilités

Chaque moteur répond à une question différente.

## ProjectionEngine

> Quel est l'état courant ?

Produit :

* CapabilityState
* ServiceState
* NodeState
* InfrastructureState

---

## HealthEngine

> Quelle est la santé de l'infrastructure ?

Produit :

* HealthReport

---

## TimelineEngine

> Comment cet état a-t-il évolué dans le temps ?

Produit :

* CapabilityTimeline
* ServiceTimeline
* NodeTimeline
* InfrastructureTimeline

---

# Invariants

Le TimelineEngine garantit plusieurs propriétés.

Les périodes sont :

* ordonnées chronologiquement ;
* contiguës ;
* non chevauchantes.

Une seule période ouverte est autorisée.

Les périodes consécutives possédant le même état sont automatiquement fusionnées.

Les observations simultanées présentant des états contradictoires sont rejetées.

---

# Conséquences

Cette architecture présente plusieurs avantages.

## Simplicité

Chaque moteur possède une responsabilité unique.

Aucune logique n'est partagée.

---

## Testabilité

Le TimelineEngine peut être testé indépendamment des autres moteurs.

Les timelines sont déterministes.

---

## Réutilisabilité

Les timelines pourront être utilisées par :

* le backend REST ;
* le tableau de bord web ;
* les graphiques historiques ;
* les futures API ;
* les exports.

---

## Évolutivité

Le TimelineEngine reste indépendant des politiques métier.

De nouvelles règles de santé pourront être introduites sans modifier la reconstruction temporelle.

Inversement, les timelines pourront évoluer sans impacter les moteurs de projection ou d'évaluation.

---

# Décision retenue

Le TimelineEngine devient le troisième moteur métier fondamental d'Ohanna-Vision.

Le domaine repose désormais sur quatre briques indépendantes :

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

Cette organisation garantit une architecture modulaire, testable et durable, où chaque moteur possède une responsabilité clairement définie et peut évoluer indépendamment des autres.
