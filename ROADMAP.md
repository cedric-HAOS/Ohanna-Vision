# ROADMAP

## Vision

Ohanna-Vision transforme les données produites par Ohanna-Agent en une représentation lisible, temps réel et historique de l'infrastructure.

Ohanna-Agent reste propriétaire de la configuration et de l'exécution des observations. Vision valide, projette et présente les snapshots et observations reçus.

---

# Socle de visualisation

## Phase 3.1 — Domaine backend

- Observation Store
- Projection Engine
- Health Engine
- Timeline Engine
- objets métier immuables

**Statut :** ✅ Terminé

## Phase 3.2 — Runtime et API

- Observation Processor
- API REST
- WebSocket
- runtime applicatif

**Statut :** ✅ Terminé

## Phase 3.3 — Dashboard

- indicateurs principaux
- alertes
- état du runtime
- observations temps réel

**Statut :** ✅ Terminé

## Phase 3.4 — Topologie interactive

- équipements et liaisons
- sélection d'un équipement
- panneau de détails
- projection des états de santé

**Statut :** ✅ Terminé

## Phase 3.5 — Frontend modulaire

- navigation
- modules JavaScript spécialisés
- CSS modulaire
- timeline fondée sur les périodes métier
- responsive
- audit frontend

**Statut :** ✅ Terminé

---

# Version 1.1.0 — Infrastructure pilotée par Agent

## 3.6.1 — Contrat d'infrastructure

- modèle Pydantic strict et versionné
- ingestion par `PUT /api/infrastructure`
- validation des nœuds et services
- remplacement atomique du snapshot

**Statut :** ✅ Terminé

## 3.6.2 — Topologie complète

- équipements
- liaisons
- layouts
- références vers les nœuds
- métadonnées topologiques

**Statut :** ✅ Terminé

## 3.6.3 — Grille horizontale

- positions logiques `column` / `row`
- conversion réalisée uniquement par Vision
- calcul du canvas et des couches
- rejet des cellules dupliquées

**Statut :** ✅ Terminé

## 3.6.4 — Source de vérité unique

- suppression de la topologie codée en dur du bootstrap de production
- état vide avant synchronisation
- projection complète après réception du snapshot
- événement WebSocket `infrastructure.updated`

**Statut :** ✅ Terminé

## 3.6.5 — Résilience Agent ↔ Vision

- synchronisation obligatoire avant les observations
- retry Agent toutes les 10 secondes
- refresh toutes les 5 minutes
- suspension des observations en cas de désynchronisation
- reprise automatique après retour de Vision

**Statut :** ✅ Terminé

## 3.6.6 — Validation

- quatre scénarios d'intégration réels
- cohérence des versions CLI et OpenAPI
- hygiène du dépôt
- 745 tests

**Statut :** ✅ Terminé

---

# Phase 4 — Administration contrôlée

L'administration reste exécutée par Ohanna-Agent. Vision ne fera qu'exposer les commandes et résultats à travers des contrats publics.

## 4.1 Infrastructure

- consultation détaillée de la configuration reçue
- comparaison entre snapshots
- validation avant application
- affichage des changements

## 4.2 Capacités

- vue détaillée
- dépendances
- statistiques
- historique complet

## 4.3 Observations

- recherche
- filtrage
- export

## 4.4 Plugins

- liste et état des plugins
- configuration exposée par Agent
- diagnostics

## 4.5 Runtime

- santé des composants
- informations système
- journaux et diagnostics

---

# Phase 5 — Historique et rapports

## 5.1 Timeline avancée

- zoom temporel
- navigation
- agrégation

## 5.2 Historique

- recherche
- comparaison de périodes
- évolution d'une capacité
- historique des snapshots d'infrastructure

## 5.3 Rapports

- disponibilité
- SLA
- export CSV
- export PDF

---

# Phase 6 — Sécurité et utilisateurs

- authentification
- rôles et permissions
- préférences utilisateur
- audit des actions
- notifications et Webhooks

---

# Phase 7 — Écosystème Ohanna

## 7.1 Multi-agents

- enregistrement de plusieurs Agents
- vues par site
- vue consolidée
- gestion des conflits d'identifiants

## 7.2 SDK et plugins

- documentation intégrée
- contrats des plugins
- informations de capacités

## 7.3 Actions contrôlées

- diagnostics à la demande
- opérations d'administration
- suivi de l'exécution
