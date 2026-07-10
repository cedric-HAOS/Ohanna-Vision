# Ohanna-Vision

**Ohanna-Vision** est l'interface web de l'écosystème **Ohanna**.

Son rôle est de transformer les observations produites par **Ohanna-Agent** en une représentation claire, synthétique et administrable de l'état réel d'une infrastructure.

Contrairement à un logiciel de supervision traditionnel, Ohanna-Vision ne réalise aucun contrôle technique.

Il s'appuie exclusivement sur les informations et les capacités exposées par Ohanna-Agent.

---

# Philosophie

Une infrastructure fiable ne se résume pas à une succession de services opérationnels.

Elle doit être comprise.

Ohanna-Agent observe les capacités.

Ohanna-Vision les rend visibles.

L'utilisateur doit pouvoir ouvrir l'interface et répondre immédiatement à des questions telles que :

* L'infrastructure est-elle saine ?
* Quelle capacité est dégradée ?
* Depuis quand ?
* Quel service est concerné ?
* Quelles sont les conséquences ?
* Quelle action puis-je entreprendre ?

---

# Les responsabilités

## Ohanna-Agent

* Observe l'infrastructure.
* Exécute les plugins.
* Produit les observations.
* Expose les fonctions d'administration.

## Ohanna-Vision

* Présente l'état courant.
* Conserve l'historique.
* Affiche la santé globale.
* Fournit un portail d'administration.
* Transmet les demandes à Ohanna-Agent.

---

# Fonctionnalités prévues

## Tableau de bord

* Vue globale de l'infrastructure.
* Santé des capacités.
* Santé des services.
* Santé des nœuds.

## Historique

* Observations.
* Changements d'état.
* Chronologie.
* Recherche.

## Administration

* Gestion des plugins.
* Consultation des baux DHCP.
* Réservations DHCP.
* Configuration des plugins.
* Diagnostics.
* Exécution d'actions.

---

# Architecture

```text
Utilisateur
      │
      ▼
Ohanna-Vision
      │
      ▼
API Ohanna-Agent
      │
      ▼
Infrastructure
```

Ohanna-Vision n'interagit jamais directement avec les équipements.

Toutes les opérations transitent par Ohanna-Agent.

---

# Principes

* séparation des responsabilités ;
* architecture modulaire ;
* contrats versionnés ;
* historique complet ;
* administration centralisée ;
* indépendance vis-à-vis de Home Assistant.

---

# Documentation

Le projet est structuré autour des documents suivants :

* Vision
* ADR-0000 — Vision d'Architecture
* Architecture
* Observation Model
* Health Model
* ROADMAP

Ces documents constituent la référence du projet avant le début du développement.

---

# État du projet

Le projet est actuellement en phase de conception.

L'architecture fonctionnelle est définie avant toute implémentation afin de garantir une évolution cohérente et durable.

---

# Licence

Ce projet est distribué sous licence MIT.
