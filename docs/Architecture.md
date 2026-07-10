# Architecture

## Objectif

Ohanna-Vision est une application web dont la mission est de rendre l'état de l'infrastructure compréhensible et administrable.

Contrairement à Ohanna-Agent, Ohanna-Vision n'exécute aucun contrôle technique.

Il construit une représentation cohérente de l'infrastructure à partir des observations produites par Ohanna-Agent.

Son architecture est organisée autour de responsabilités clairement séparées afin de permettre une évolution indépendante de chaque composant.

---

# Vue d'ensemble

```text
                    Utilisateur
                         │
                Interface Web (Frontend)
                         │
                         ▼
                 Backend Ohanna-Vision
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
     Etat courant   Historique   Administration
            │            │            │
            └────────────┼────────────┘
                         │
                  API Ohanna-Agent
                         │
                Plugins & Infrastructure
```

---

# Les composants

## Frontend

Le frontend est responsable de la présentation.

Il permet notamment :

* d'afficher le tableau de bord ;
* de consulter les capacités ;
* de visualiser les services et les nœuds ;
* d'explorer l'historique ;
* de lancer des actions d'administration ;
* d'afficher les résultats des actions.

Le frontend ne contient aucune logique métier liée à l'infrastructure.

---

## Backend

Le backend constitue le cœur de Ohanna-Vision.

Il est responsable de :

* recevoir les observations ;
* maintenir l'état courant ;
* conserver l'historique ;
* calculer les informations de présentation ;
* exposer les API consommées par le frontend ;
* transmettre les demandes d'administration vers Ohanna-Agent.

Le backend ne réalise jamais directement les opérations sur l'infrastructure.

---

## État courant

L'état courant représente la meilleure connaissance disponible de chaque capacité.

Il est construit à partir des dernières observations reçues.

Une capacité possède toujours un état courant unique.

---

## Historique

L'historique conserve les observations et les changements d'état.

Il permet de répondre à des questions telles que :

* Quand un incident est-il apparu ?
* Combien de temps a-t-il duré ?
* À quelle fréquence se reproduit-il ?
* Quelle action a permis son retour à la normale ?

---

## Administration

Le module d'administration permet à l'utilisateur d'interagir avec l'infrastructure.

Il ne réalise aucune opération lui-même.

Toutes les demandes sont transmises à Ohanna-Agent.

Exemples :

* consulter les baux DHCP ;
* créer une réservation DHCP ;
* installer un plugin ;
* modifier la configuration d'un plugin ;
* lancer un diagnostic.

---

# Flux d'observation

Le flux d'observation transporte exclusivement des faits.

```text
Infrastructure
      │
      ▼
Ohanna-Agent
      │
Observations
      │
      ▼
Ohanna-Vision
```

Une observation ne doit jamais être modifiée.

Elle constitue la source de vérité.

---

# Flux d'administration

Le flux d'administration transporte des intentions.

```text
Utilisateur
      │
      ▼
Ohanna-Vision
      │
Commande
      │
      ▼
Ohanna-Agent
      │
Exécution
      │
      ▼
Infrastructure
```

L'utilisateur n'interagit jamais directement avec les équipements.

---

# Principes d'architecture

L'architecture de Ohanna-Vision repose sur les principes suivants :

* séparation stricte entre présentation et exécution ;
* Ohanna-Agent reste le seul composant connecté à l'infrastructure ;
* toute donnée affichée provient d'observations ou d'informations exposées par Ohanna-Agent ;
* l'historique est conservé indépendamment de l'état courant ;
* l'administration est réalisée exclusivement via les API publiques d'Ohanna-Agent ;
* les composants peuvent évoluer indépendamment tant que les contrats restent compatibles.

---

# Évolutions prévues

Cette architecture permet d'ajouter progressivement :

* des tableaux de bord personnalisés ;
* une authentification multi-utilisateurs ;
* des notifications ;
* des statistiques ;
* des rapports ;
* des vues multi-sites ;
* des tableaux de bord spécialisés ;
* de nouveaux modules d'administration.

Aucune de ces évolutions ne doit remettre en cause la séparation entre Ohanna-Agent et Ohanna-Vision.
