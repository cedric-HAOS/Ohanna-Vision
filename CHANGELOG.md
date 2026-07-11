# Changelog

Toutes les évolutions importantes du projet **Ohanna-Vision** sont documentées dans ce fichier.

Le projet suit les principes de **Keep a Changelog** et du **Semantic Versioning**.

---

# [0.1.0] - 2026-07-11

Première version fonctionnelle d'Ohanna-Vision.

Cette version établit l'ensemble des fondations du projet : modèle de domaine, moteurs de calcul, backend Web, API REST, WebSocket et première interface utilisateur.

## Added

### Domaine

* Modèle immuable `Observation`
* États de santé (`HealthStatus`)
* Validation des observations
* Identifiants d'observations
* Métadonnées extensibles

### Observation Store

* Stockage immuable des observations
* Détection des doublons
* Historique chronologique
* Filtres :

  * nœud
  * service
  * capacité
  * période

### Projection Engine

* Projection des observations
* Calcul de l'état courant
* Agrégation des capacités

### Health Engine

* Calcul de l'état des services
* Calcul de l'état des nœuds
* Calcul de l'état global
* Projection déterministe

### Timeline Engine

* Gestion des périodes d'état
* `StatePeriod`
* `CapabilityTimeline`
* `ServiceTimeline`
* `NodeTimeline`
* `InfrastructureTimeline`
* Reconstruction complète à partir des observations

### Runtime

* `BackendRuntime`
* États du runtime
* Statistiques
* Snapshots
* Horloge injectable
* `ObservationProcessor`
* Résultats de traitement

### Backend Web

* Application FastAPI
* Point de composition (`bootstrap.py`)
* `ApplicationContext`
* Injection de dépendances
* Documentation OpenAPI

### API REST

Ajout des endpoints :

* `GET /`
* `GET /api/`
* `GET /api/runtime`
* `GET /api/observations`
* `GET /api/timeline`
* `GET /api/timeline/nodes/{node_id}`
* `GET /api/timeline/nodes/{node_id}/services/{service_id}`

### WebSocket

* Endpoint `/ws`
* Gestionnaire `WebSocketHub`
* Gestion des connexions
* Broadcast multi-clients
* Heartbeat `ping` / `pong`

### Interface Web

* Tableau de bord HTML statique
* CSS intégré
* JavaScript natif
* Rafraîchissement manuel
* Connexion WebSocket
* Affichage :

  * Runtime
  * Statistiques
  * Timeline
  * Observations

### Tests

Ajout d'une couverture complète pour :

* domaine
* moteurs
* runtime
* API REST
* WebSocket
* interface Web
* bootstrap

## Changed

* Séparation stricte entre le domaine métier et la couche Web.
* Le `BackendRuntime` reste totalement indépendant de FastAPI.
* Le `TimelineEngine` reconstruit les timelines exclusivement à partir des observations.
* L'interface Web consomme uniquement les API REST et le WebSocket.
* Le point d'entrée officiel devient :

```powershell
python -m uvicorn ohanna_vision.web.bootstrap:app --reload
```

## Quality

* 270 tests unitaires
* Ruff sans erreur
* Documentation OpenAPI générée automatiquement
* Architecture entièrement injectée
* Bootstrap de production opérationnel

---

# Historique

## Pré-version

Les travaux ayant conduit à cette première version comprennent :

* définition de la vision d'architecture ;
* conception du modèle d'observation ;
* implémentation des moteurs métier ;
* construction du runtime ;
* développement de l'API Web ;
* création de l'interface utilisateur.

Cette version marque la fin de la **Phase 1** du projet.
