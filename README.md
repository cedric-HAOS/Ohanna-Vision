# Ohanna-Vision

> Visualiser l'état réel des capacités d'une infrastructure dans le temps.

---

# Vision

Une infrastructure fiable ne se résume pas à des services qui répondent.

Elle doit permettre de comprendre :

* ce qui fonctionne actuellement ;
* ce qui s'est produit auparavant ;
* depuis quand une capacité est disponible ;
* comment l'état global évolue dans le temps.

Ohanna-Vision est le composant de visualisation d'Ohanna.

Il transforme les observations produites par **Ohanna-Agent** en une représentation exploitable de l'état de l'infrastructure.

Son rôle est exclusivement de présenter les informations.

Il ne réalise aucune supervision réseau et n'exécute aucune vérification.

---

# Architecture

```
                 Ohanna-Agent
                       │
                Observations
                       │
                       ▼
               Observation Store
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
 Projection Engine  Health Engine  Timeline Engine
         │             │             │
         └─────────────┼─────────────┘
                       ▼
               Backend Runtime
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
      REST API                 WebSocket
          │                         │
          └────────────┬────────────┘
                       ▼
                 Static Web UI
```

---

# Fonctionnalités

## Domaine

* Modèle d'observation immuable
* États de santé
* Observation Store
* Historique filtrable

## Moteurs

* Projection Engine
* Health Engine
* Timeline Engine

## Runtime

* Backend Runtime
* Runtime Snapshot
* Runtime Statistics
* Observation Processor

## API REST

* Runtime
* Observations
* Timeline

## Temps réel

* WebSocket
* Broadcast multiclient
* Heartbeat ping/pong

## Interface Web

* Tableau de bord statique
* Sans framework JavaScript
* HTML/CSS/JavaScript natifs

---

# Structure du projet

```
src/
└── ohanna_vision/
    ├── domain/
    ├── projection/
    ├── health/
    ├── timeline/
    ├── runtime/
    └── web/
        ├── routers/
        ├── static/
        ├── websocket_hub.py
        ├── bootstrap.py
        └── app.py

tests/
docs/
```

---

# Installation

Créer un environnement virtuel :

```powershell
python -m venv .venv
```

Activer l'environnement :

```powershell
.\.venv\Scripts\Activate.ps1
```

Installer le projet :

```powershell
python -m pip install -e .
```

---

# Lancer Ohanna-Vision

Le point d'entrée officiel est :

```powershell
python -m uvicorn ohanna_vision.web.bootstrap:app --reload
```

L'application est alors disponible sur :

```
http://127.0.0.1:8000/
```

Documentation OpenAPI :

```
http://127.0.0.1:8000/docs
```

Interface Web :

```
http://127.0.0.1:8000/ui/
```

---

# API REST

## Runtime

```
GET /api/runtime
```

Retourne :

* état du backend ;
* statistiques ;
* snapshot courant.

---

## Observations

```
GET /api/observations
```

Filtres disponibles :

* node_id
* service_id
* capability_id
* since
* until

---

## Timeline

Infrastructure complète :

```
GET /api/timeline
```

Timeline d'un nœud :

```
GET /api/timeline/nodes/{node_id}
```

Timeline d'un service :

```
GET /api/timeline/nodes/{node_id}/services/{service_id}
```

---

# WebSocket

Connexion :

```
/ws
```

Messages actuellement supportés :

```
connected
ping
pong
```

L'architecture permet ensuite de diffuser :

* observation.received
* runtime.updated
* timeline.updated

---

# Interface Web

Le tableau de bord affiche :

* état du runtime ;
* statistiques ;
* observations récentes ;
* timeline de l'infrastructure ;
* état de la connexion WebSocket.

Les données proviennent exclusivement des API REST et du canal WebSocket.

Aucune donnée n'est stockée côté navigateur.

---

# Développement

Vérification Ruff :

```powershell
python -m ruff check .
```

Exécution des tests :

```powershell
python -m pytest
```

Tous les warnings deviennent des erreurs :

```powershell
python -m pytest -W error
```

---

# Qualité

Version actuelle :

* 270 tests unitaires
* Ruff sans erreur
* API REST documentée automatiquement
* Interface Web intégrée
* WebSocket intégré

---

# Roadmap

La Phase 1 est terminée.

La prochaine étape consiste à connecter Ohanna-Vision à Ohanna-Agent afin de recevoir les observations en temps réel et d'afficher l'évolution de l'infrastructure sans rechargement de la page.

---

# Licence

Projet distribué sous licence MIT.
