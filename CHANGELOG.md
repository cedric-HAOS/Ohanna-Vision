# Changelog

Toutes les évolutions importantes du projet **Ohanna-Vision** sont documentées dans ce fichier.

Le projet suit les principes de *Keep a Changelog* et du *Semantic Versioning*.

---

# [0.1.0] - 2026-07-10

Première version du cœur métier de **Ohanna-Vision**.

Cette version pose les fondations architecturales du projet en introduisant les modèles métier, les moteurs de projection, d'évaluation et de reconstruction temporelle de l'infrastructure.

---

## Ajouté

### Documentation

* Création de la vision du projet.
* Définition de l'architecture générale.
* Documentation du modèle des observations.
* Documentation du modèle de santé.
* Création de la feuille de route.
* Rédaction du README.

### Architecture

* ADR-0000 — Vision d'Architecture.
* ADR-0001 — Projection Engine.
* ADR-0002 — Health Engine.

---

## Phase 1 — Domaine métier

### Domain Model

Création des principaux objets métier :

* Observation
* ObservationStatus
* Health
* HealthStatus
* CapabilityState
* ServiceState
* NodeState
* InfrastructureState
* Criticality

---

### Observation Store

Ajout du stockage immuable des observations.

Fonctionnalités :

* ajout d'observations ;
* conservation chronologique ;
* consultation de l'historique ;
* filtrage par infrastructure.

---

### Projection Engine

Ajout du moteur de projection permettant de reconstruire automatiquement :

* l'état des capacités ;
* l'état des services ;
* l'état des nœuds ;
* l'état global de l'infrastructure.

Le moteur fonctionne exclusivement à partir des observations stockées.

---

### Health Engine

Ajout du moteur d'évaluation métier.

Fonctionnalités :

* interprétation indépendante des projections ;
* prise en compte de la criticité ;
* gestion des observations obsolètes (*stale*) ;
* propagation des états vers les services, les nœuds et l'infrastructure ;
* production d'un `HealthReport`.

---

### Timeline Engine

Ajout du moteur de reconstruction temporelle.

Nouveaux objets métier :

* StatePeriod
* CapabilityTimeline
* ServiceTimeline
* NodeTimeline
* InfrastructureTimeline

Fonctionnalités :

* fusion des observations successives ;
* reconstruction des périodes d'état ;
* génération des timelines hiérarchiques ;
* interrogation de l'état à un instant donné ;
* calcul de la durée de la période courante ;
* gestion des transitions d'état.

---

## Qualité

* Développement intégral en Test-Driven Development (TDD).
* Validation systématique avec Ruff.
* Typage Python complet.
* Documentation des principaux composants.

---

## Tests

État actuel de la couverture fonctionnelle :

```text
119 tests
100 % réussis
```

---

## Architecture obtenue

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

Cette version constitue le socle métier d'Ohanna-Vision.

Les prochaines versions se concentreront sur le modèle d'administration, le backend REST et l'interface web.
