# Ohanna-Vision

> Visualiser l'état réel d'une infrastructure pilotée par capacités.

Ohanna-Vision est l'interface web de l'écosystème Ohanna.

Il reçoit d'Ohanna-Agent deux flux complémentaires :

- un **snapshot complet d'infrastructure** décrivant les nœuds, services, équipements, liaisons et positions logiques ;
- les **observations dynamiques** décrivant l'état réel des capacités dans le temps.

Ohanna-Agent reste la source de vérité de la configuration. Ohanna-Vision valide, projette, historise et affiche les données reçues.

---

## Principes

Ohanna-Vision ne collecte aucune donnée directement sur l'infrastructure.

Il ne dialogue ni avec les équipements ni avec les services supervisés. Il s'appuie exclusivement sur les contrats publics d'Ohanna-Agent afin de présenter :

- l'état courant des capacités ;
- la santé des services et des nœuds ;
- la topologie de l'infrastructure ;
- l'historique des périodes de fonctionnement ;
- les observations reçues en temps réel.

La définition statique répond à la question **« qu'est-ce qui existe ? »**. Les observations répondent à la question **« comment cela fonctionne-t-il ? »**.

---

## Fonctionnalités

### Dashboard

La vue d'ensemble regroupe :

- les indicateurs principaux ;
- les alertes actives ;
- l'état global du runtime ;
- la topologie de l'infrastructure ;
- la timeline des périodes métier.

### Topologie dynamique

La topologie n'est plus codée en dur dans Vision.

Au démarrage, Vision expose un état vide jusqu'à la réception du snapshot Agent. Après synchronisation, il affiche :

- les équipements ;
- les liaisons ;
- les nœuds supervisés ;
- les adresses ;
- les services associés ;
- l'état de santé ;
- le panneau de détails.

Les positions sont transmises sous forme de cellules logiques `column` / `row`. Vision reste seul responsable de leur conversion en coordonnées graphiques, des espacements et des dimensions du canvas.

### Timeline

La timeline repose sur les périodes métier calculées par le backend.

Le navigateur ne regroupe jamais les observations. Chaque ligne représente un nœud et chaque segment une période d'état produite par le `TimelineEngine`.

### Observations

Les observations reçues en temps réel présentent notamment :

- la date ;
- la capacité ;
- le service ;
- le nœud ;
- l'état ;
- la latence ;
- les métadonnées.

### Temps réel

Le WebSocket actualise automatiquement :

- les KPI ;
- la topologie ;
- la timeline ;
- la liste des observations.

La réception d'un nouveau snapshot émet également l'événement `infrastructure.updated`.

---

## Intégration avec Ohanna-Agent

Le contrat principal est :

```text
Ohanna-Agent
    ├── PUT  /api/infrastructure
    └── POST /api/observations
             ↓
Ohanna-Vision
    ├── validation stricte
    ├── projection de topologie
    ├── stockage des observations
    ├── calcul de santé
    └── timeline métier
```

Vision accepte un snapshot complet par :

```http
PUT /api/infrastructure
```

Réponse attendue :

```text
200 OK
```

Les observations sont reçues par :

```http
POST /api/observations
```

L'Agent attend que Vision accepte le snapshot avant de démarrer les observations. Il retente la synchronisation toutes les 10 secondes et renouvelle le snapshot toutes les 5 minutes. Si Vision devient indisponible, les observations sont suspendues jusqu'à la resynchronisation.

Le détail du contrat et des scénarios d'exploitation se trouve dans [`INTEGRATION.md`](INTEGRATION.md).

---

## Architecture

Le frontend est volontairement modulaire :

```text
app.js
        │
        ▼
ApplicationController
        │
        ├── DashboardController
        ├── NavigationController
        ├── TopologyController
        ├── TimelineController
        ├── ObservationsController
        ├── DeviceDetailsController
        └── WebSocketController
```

Les données partagées sont centralisées dans `application_state.js`.

Le frontend reste un moteur de rendu. La validation, les projections, la santé et la timeline sont calculées côté backend.

---

## API principales

| Méthode | Endpoint | Rôle |
|---|---|---|
| `PUT` | `/api/infrastructure` | Remplacer le snapshot courant |
| `POST` | `/api/observations` | Ingérer une observation |
| `GET` | `/api/topology` | Lire la topologie projetée |
| `GET` | `/api/timeline` | Lire les périodes métier |
| `GET` | `/api/runtime` | Lire l'état du runtime |
| WebSocket | `/ws` | Recevoir les mises à jour temps réel |

La documentation OpenAPI est disponible sur `/docs` lorsque son exposition est activée dans la configuration.

---

## Technologies

- Python 3.13
- FastAPI
- Pydantic
- JavaScript ES Modules
- HTML5
- CSS modulaire
- WebSocket

---

## Structure

```text
src/
    ohanna_vision/
        topology/
        web/
            api/
            routers/
            static/

tests/
docs/
scripts/
```

Le frontend est organisé par responsabilités dans `web/static/styles/`.

---

## Développement

Installer le projet et ses dépendances de développement :

```bash
pip install -e ".[dev]"
```

Lancer le serveur :

```bash
uvicorn ohanna_vision.web.bootstrap:build_application --factory --reload
```

Ou utiliser la CLI :

```bash
ohanna-vision --config config/vision.yaml
```

Accéder au tableau de bord :

```text
http://127.0.0.1:8000/ui/
```

---

## Tests et qualité

```bash
python -m pytest
python -m ruff check .
```

État validé pour la v1.1.0 :

```text
745 tests passent
```

Les scénarios d'intégration réels ont également été validés :

1. Vision démarre avant Agent ;
2. Agent démarre avant Vision ;
3. Vision disparaît puis redémarre ;
4. Agent s'arrête proprement pendant une attente de synchronisation.

---

## État actuel

La version **1.1.0** introduit la synchronisation complète de l'infrastructure avec Ohanna-Agent.

Vision démarre sans topologie métier locale, reçoit la définition officielle de l'Agent, la valide, la projette sur sa grille horizontale puis commence à afficher les observations associées.

Les prochaines évolutions concernent principalement l'administration contrôlée de l'infrastructure, l'historique avancé et la supervision multi-agents.
