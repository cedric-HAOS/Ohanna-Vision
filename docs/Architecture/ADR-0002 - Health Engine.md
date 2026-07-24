# ADR-0002 — Health Engine

## Statut

Accepté

## Date

10 juillet 2026

---

# Contexte

Le Projection Engine transforme une collection d'observations en une représentation cohérente de l'infrastructure.

Cette représentation décrit uniquement le dernier état connu des capacités, des services, des nœuds et de l'infrastructure.

Par exemple :

```text
DNS Resolve

Status : unavailable

Dernière observation : 10:42:18
```

Cette information est factuelle.

Elle décrit ce qui a été observé.

En revanche, elle ne permet pas de répondre aux questions suivantes :

* cette panne est-elle grave ?
* faut-il alerter l'utilisateur ?
* la maison fonctionne-t-elle encore correctement ?
* cette capacité est-elle critique ?
* l'absence de nouvelles observations est-elle acceptable ?
* quel est l'impact sur le reste de l'infrastructure ?

Ces questions relèvent de l'interprétation métier.

Il est donc nécessaire d'introduire un moteur spécialisé chargé d'évaluer la santé de l'infrastructure.

---

# Décision

Ohana-Vision introduit un composant indépendant appelé **Health Engine**.

Le Health Engine reçoit une projection de l'infrastructure.

Il produit une évaluation métier de cette projection.

Il ne modifie jamais la projection.

Il ne modifie jamais les observations.

Il calcule uniquement leur signification.

---

# Principe fondamental

La projection décrit ce qui est.

La santé décrit ce que cela signifie.

Cette distinction constitue l'un des principes fondamentaux de Ohana-Vision.

---

# Position dans l'architecture

```text
                 Observations
                       │
                       ▼
               ObservationStore
                       │
                       ▼
               Projection Engine
                       │
                       ▼
            InfrastructureState
                       │
                       ▼
                 Health Engine
                       │
                       ▼
                 Health Report
                       │
                       ▼
              Dashboard / API
```

---

# Responsabilités

Le Health Engine est responsable de :

* évaluer chaque capacité ;
* appliquer les règles de criticité ;
* détecter les observations obsolètes ;
* propager les impacts vers les services ;
* propager les impacts vers les nœuds ;
* calculer la santé globale ;
* expliquer les raisons d'une dégradation.

Il n'est pas responsable de construire les projections.

Il n'est pas responsable de stocker les observations.

---

# Projection versus Santé

La projection représente un état.

Par exemple :

```text
DNS

Status = unavailable
```

La santé représente l'interprétation de cet état.

Par exemple :

```text
DNS

Status = unavailable

Criticalité = critique

Impact = infrastructure indisponible
```

Ces deux informations ne doivent jamais être confondues.

---

# Criticité

Toutes les capacités n'ont pas la même importance.

Par exemple :

```text
DNS Resolve
```

est généralement beaucoup plus critique que :

```text
Température CPU
```

Le Health Engine prend donc en compte un niveau de criticité indépendant de l'état projeté.

Les niveaux actuellement définis sont :

* Low
* Normal
* High
* Critical

La criticité influence la propagation des problèmes.

Elle ne modifie jamais les observations.

---

# Obsolescence

Une capacité peut sembler saine simplement parce qu'aucune nouvelle observation n'a été reçue.

Par exemple :

```text
Dernière observation :

il y a 2 heures
```

Selon le type de capacité, cette situation peut être acceptable ou anormale.

Chaque capacité peut donc définir une durée maximale d'absence d'observation.

Au-delà de cette durée, la capacité devient :

```text
STALE
```

Le statut STALE représente une information différente d'une panne.

Il signifie que l'état réel est désormais inconnu.

---

# Propagation

Le Health Engine applique des règles de propagation.

Ces règles déterminent l'impact d'un problème sur les niveaux supérieurs.

Exemple :

```text
Capability

↓

Service

↓

Node

↓

Infrastructure
```

La propagation est indépendante de la projection.

Elle peut évoluer sans modifier le Projection Engine.

---

# Health Report

Le résultat produit par le Health Engine est un Health Report.

Il contient :

* la santé des capacités ;
* la santé des services ;
* la santé des nœuds ;
* la santé globale.

Il ne remplace jamais la projection.

Il la complète.

---

# Pourquoi séparer Projection et Health ?

Cette séparation apporte plusieurs avantages.

## Simplicité

Chaque moteur possède une responsabilité unique.

---

## Évolutivité

Les règles métier peuvent évoluer sans modifier les projections.

---

## Recalcul

Une nouvelle politique de santé peut être appliquée sur une projection existante.

Aucune reconstruction de l'historique n'est nécessaire.

---

## Testabilité

Les règles métier deviennent simples à tester.

Chaque politique peut être validée indépendamment.

---

# Politique de santé

Les règles appliquées par le Health Engine sont regroupées dans des politiques.

Une politique peut définir :

* la criticité ;
* le délai d'obsolescence ;
* les règles futures de dépendance ;
* les règles futures de redondance.

Le moteur reste indépendant des politiques.

---

# Pourquoi un moteur dédié ?

Il serait possible de calculer directement la santé dans le Projection Engine.

Cette approche est rejetée.

Elle mélangerait :

* les faits ;
* leur représentation ;
* leur interprétation.

Ces trois responsabilités doivent rester indépendantes.

---

# Dépendances futures

Le Health Engine évoluera progressivement.

Les prochaines versions introduiront :

## Dépendances

Exemple :

```text
Home Assistant

↓

MQTT

↓

DNS
```

Une panne DNS pourra alors affecter Home Assistant.

---

## Redondance

Exemple :

```text
DNS-01

DNS-02
```

Si un seul serveur est indisponible, la capacité pourra rester saine.

---

## Maintenance

Certaines capacités pourront être volontairement indisponibles.

Le moteur devra distinguer :

* une panne ;
* une maintenance planifiée.

---

## Pondération

Toutes les capacités critiques n'auront pas nécessairement le même poids.

Des règles plus fines pourront être ajoutées.

---

## Politiques personnalisées

Chaque installation pourra définir ses propres règles de santé.

Le moteur restera identique.

Seules les politiques évolueront.

---

# Séparation des responsabilités

L'architecture distingue désormais quatre responsabilités.

## Observation

Les faits.

---

## Projection

La représentation actuelle.

---

## Santé

L'interprétation métier.

---

## Présentation

L'affichage destiné à l'utilisateur.

Chaque niveau dépend uniquement du précédent.

---

# Conséquences

Toutes les interfaces utilisateur utiliseront le Health Report.

Le Dashboard n'interprétera jamais directement les projections.

L'API REST exposera le résultat du Health Engine.

Les politiques de santé pourront évoluer indépendamment du stockage et de la projection.

---

# Alternatives étudiées

## Calculer la santé dans Projection Engine

Rejeté.

Le moteur de projection doit uniquement construire une représentation.

---

## Ajouter un champ Health dans InfrastructureState

Rejeté.

InfrastructureState représente uniquement une projection.

Il ne doit pas contenir de logique métier.

---

## Modifier les observations

Rejeté.

Les observations constituent la source de vérité.

Elles ne doivent jamais être enrichies par des informations calculées.

---

# Décisions futures

Cet ADR sera complété par plusieurs décisions :

* ADR — History Engine
* ADR — Dependency Engine
* ADR — Statistics Engine
* ADR — Incident Engine
* ADR — Availability Engine

Tous utiliseront les projections produites par le Projection Engine.

Le Health Engine restera responsable uniquement de l'évaluation métier.

---

# Règle fondamentale

Une projection décrit l'infrastructure.

Le Health Engine en évalue la santé.

La santé n'est jamais une propriété intrinsèque de l'infrastructure.

Elle est le résultat d'une interprétation métier appliquée à une projection.

Cette distinction garantit la simplicité, la modularité et l'évolutivité de l'architecture de Ohana-Vision.
