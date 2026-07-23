# Intégration Ohanna-Agent ↔ Ohanna-Vision

## Responsabilités

Ohanna-Agent est la source de vérité de l'infrastructure.

Il charge et valide :

- les nœuds ;
- les services ;
- les équipements ;
- les liaisons ;
- les layouts ;
- les positions logiques sur grille.

Ohanna-Vision ne lit aucun fichier de configuration de l'Agent. Il reçoit un contrat JSON normalisé, le valide puis le projette dans ses modèles de topologie.

---

## Flux d'intégration

```text
infrastructure.yaml
        ↓
Ohanna-Agent
        ↓
VisionInfrastructureMapper
        ↓
PUT /api/infrastructure
        ↓
InfrastructureRequest
        ↓
InfrastructureMapper
        ↓
Topology
        ↓
GET /api/topology + WebSocket
```

Les observations suivent un canal distinct :

```text
Observation
    ↓
POST /api/observations
    ↓
Observation Store
    ↓
Projection / Health / Timeline
```

La séparation reste explicite :

- le snapshot décrit **ce qui existe** ;
- les observations décrivent **comment cela fonctionne**.

---

## Endpoint d'infrastructure

```http
PUT /api/infrastructure
Content-Type: application/json
```

Réponse de succès :

```http
200 OK
```

Exemple de réponse :

```json
{
  "accepted": true,
  "infrastructure_id": "ohanna-house",
  "node_count": 2,
  "service_count": 2
}
```

Le snapshot reçu remplace atomiquement le précédent.

---

## Structure du contrat

```json
{
  "schema_version": 1,
  "infrastructure_id": "ohanna-house",
  "name": "Ohanna House",
  "environment": "production",
  "metadata": {
    "version": "1.0",
    "tags": ["production", "home"]
  },
  "nodes": [],
  "services": [],
  "topology": {
    "devices": [],
    "links": [],
    "layouts": [],
    "metadata": {}
  }
}
```

Vision rejette notamment :

- un `schema_version` inconnu ;
- les identifiants dupliqués ;
- un service lié à un nœud absent ;
- un équipement lié à un nœud absent ;
- un lien vers un équipement absent ;
- une position vers un équipement absent ;
- deux équipements dans la même cellule ;
- les champs non prévus par le contrat.

---

## Grille de topologie

L'Agent transmet une intention de placement :

```json
{
  "column": 4,
  "row": 1
}
```

Il ne transmet jamais :

- `x` ou `y` ;
- les marges ;
- les espacements ;
- la taille du canvas ;
- les détails SVG.

Vision transforme la cellule logique en position graphique. Il reste ainsi propriétaire de la présentation horizontale et peut faire évoluer son responsive sans modifier le contrat métier.

---

## Synchronisation et résilience

L'Agent applique les temporisations de production suivantes :

```yaml
vision:
  infrastructure_retry_seconds: 10.0
  infrastructure_refresh_seconds: 300.0
```

Cycle de vie :

1. l'Agent démarre et tente d'envoyer le snapshot ;
2. tant que Vision ne répond pas `200`, le scheduler d'observation reste arrêté ;
3. après acceptation, les observations démarrent ;
4. le snapshot est renvoyé toutes les cinq minutes ;
5. si un refresh échoue, les observations sont suspendues ;
6. les tentatives reprennent toutes les dix secondes ;
7. le scheduler redémarre après resynchronisation.

Vision conserve actuellement le snapshot courant en mémoire. Le refresh périodique permet donc de récupérer automatiquement après son redémarrage.

---

## État initial

Avant réception du premier snapshot :

```text
GET /api/topology
```

retourne une topologie vide identifiée `unconfigured`.

L'interface affiche :

```text
En attente de la configuration transmise par Ohanna-Agent.
```

---

## Validation locale

Démarrer Vision :

```powershell
ohanna-vision --config .\config\vision.yaml
```

Puis démarrer Agent :

```powershell
ohanna-agent `
  --config .\config\shikamaru.yaml `
  --infrastructure .\config\infrastructure.yaml `
  --dns-config .\config\plugins\dns.yaml `
  --log-level DEBUG
```

Vérifier la projection :

```powershell
$topology = Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/topology"

[PSCustomObject]@{
  Topology = $topology.topology_id
  Devices  = $topology.devices.Count
  Links    = $topology.links.Count
  Layouts  = $topology.layouts.Count
}
```

Pour la configuration Ohanna-House validée :

```text
Topology : ohanna-house
Devices  : 9
Links    : 8
Layouts  : 1
```

---

## Scénarios validés

- Vision démarre avant Agent ;
- Agent démarre avant Vision ;
- Vision s'arrête puis redémarre ;
- Agent reçoit un arrêt pendant sa boucle de retry.

Dans les quatre cas, la synchronisation, la suspension et la reprise se comportent comme prévu.

---

## Intégration des assets graphiques

Les ressources de marque restent décrites dans [`BRAND-GUIDELINES.md`](BRAND-GUIDELINES.md).

Les fichiers statiques nécessaires sont inclus dans le package Python via `tool.setuptools.package-data`.
