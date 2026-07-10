# ROADMAP

# Vision

Une infrastructure fiable n'est pas seulement une infrastructure qui fonctionne.

C'est une infrastructure dont l'état est compréhensible, explicable et administrable.

Ohanna-Agent garantit les capacités de l'infrastructure.

Ohanna-Vision les rend visibles.

L'objectif d'Ohanna-Vision est de transformer les observations produites par Ohanna-Agent en une représentation claire de l'état de l'infrastructure, tout en offrant un portail d'administration cohérent de l'écosystème Ohanna.

---

# Phase 0 — Architecture

Objectif : construire les fondations du projet.

* Vision
* ADR-0000
* Architecture
* Observation Model
* Health Model
* README
* ROADMAP
* CHANGELOG

---

# Phase 1 — Backend

Objectif : construire le cœur de Ohanna-Vision.

* API interne
* Modèle de santé
* Gestion des observations
* État courant
* Historique
* Contrats d'échange avec Ohanna-Agent

---

# Phase 2 — API Ohanna-Agent

Objectif : communiquer avec Ohanna-Agent.

* Client API
* Réception des observations
* Actions d'administration
* Gestion des erreurs
* Compatibilité des versions

---

# Phase 3 — Interface Web

Objectif : créer la première interface utilisateur.

* Tableau de bord
* Vue des capacités
* Vue des services
* Vue des nœuds
* Navigation
* Rafraîchissement temps réel

---

# Phase 4 — Historique

Objectif : permettre l'analyse des événements.

* Historique des observations
* Historique des changements d'état
* Chronologie
* Recherche
* Filtres

---

# Phase 5 — Administration

Objectif : administrer l'infrastructure.

* Gestion des plugins
* Réservations DHCP
* Consultation des baux DHCP
* Paramètres des plugins
* Diagnostics
* Exécution d'actions

---

# Phase 6 — Santé

Objectif : fournir une vision globale.

* Santé des capacités
* Santé des services
* Santé des nœuds
* Santé globale
* Gestion des dépendances

---

# Phase 7 — Utilisateurs

Objectif : sécuriser l'accès.

* Authentification
* Autorisations
* Journal d'audit
* Gestion des sessions

---

# Phase 8 — Déploiement

Objectif : préparer la production.

* Packaging
* Installation
* Sauvegarde
* Migration
* Documentation d'exploitation

---

# Phase 9 — Version 1.0

Objectif : première version stable.

* Audit complet
* Documentation finale
* Optimisations
* Tests
* Release v1.0.0

---

# Vision long terme

À terme, Ohanna-Vision devra devenir le portail central de l'écosystème Ohanna.

Il permettra de :

* superviser l'infrastructure ;
* comprendre son état ;
* consulter son historique ;
* administrer les plugins ;
* piloter certaines opérations ;
* offrir une interface moderne indépendante de Home Assistant.

Le développement restera guidé par un principe simple :

> Une information doit être comprise avant d'être administrée.
