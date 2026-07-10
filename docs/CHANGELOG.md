# CHANGELOG

Toutes les évolutions importantes du projet **Ohanna-Vision** seront documentées dans ce fichier.

Le format s'inspire de **Keep a Changelog** et le projet suit le principe du **Semantic Versioning**.

---

# [Unreleased]

## À venir

### Architecture

* Définition de l'architecture logicielle détaillée.
* Définition des contrats d'échange avec Ohanna-Agent.
* Définition des modèles de données internes.

### Backend

* Mise en place du backend de Ohanna-Vision.
* Gestion de l'état courant.
* Historisation des observations.
* API interne.

### Frontend

* Premier tableau de bord.
* Vue des capacités.
* Vue des services.
* Vue des nœuds.
* Temps réel.

### Administration

* Gestion des plugins.
* Consultation des baux DHCP.
* Réservations DHCP.
* Diagnostics.
* Exécution d'actions via Ohanna-Agent.

---

# [0.1.0] - 2026-07-10

## Ajouté

### Fondation du projet

* Création du dépôt **Ohanna-Vision**.
* Mise en place de l'organisation documentaire initiale.
* Définition de la vision du projet.

### Documentation

Création des documents fondateurs :

* `README.md`
* `ROADMAP.md`
* `CHANGELOG.md`
* `docs/Vision.md`
* `docs/Architecture.md`
* `docs/Observation-Model.md`
* `docs/Health-Model.md`
* `docs/Architecture/ADR-0000-Vision-d-Architecture.md`

### Vision d'architecture

Définition des principes fondamentaux de l'écosystème :

* séparation des responsabilités entre Ohanna-Agent et Ohanna-Vision ;
* Ohanna-Agent comme moteur de supervision et d'administration ;
* Ohanna-Vision comme interface web et portail d'administration ;
* communication fondée sur des contrats versionnés ;
* indépendance vis-à-vis de Home Assistant ;
* distinction entre observations, état courant, historique et santé.

### Modèle fonctionnel

Définition des concepts principaux :

* observation ;
* capacité ;
* service ;
* nœud ;
* état courant ;
* historique ;
* santé globale.

### Roadmap

Définition des premières phases du projet :

* architecture ;
* backend ;
* API ;
* interface web ;
* historique ;
* administration ;
* sécurité ;
* déploiement ;
* première version stable.

---

## Objectif de cette version

Cette première version ne contient aucun code applicatif.

Elle établit les fondations architecturales de **Ohanna-Vision** afin de garantir une évolution cohérente, modulaire et durable avant le début du développement.

L'objectif est de reproduire l'approche qui a permis de structurer efficacement **Ohanna-Agent**, en privilégiant les décisions d'architecture avant l'implémentation.
