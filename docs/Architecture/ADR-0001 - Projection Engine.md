# ADR-0001 — Projection Engine

## Statut

Accepté

## Date

10 juillet 2026

---

# Contexte

Ohanna-Agent produit des observations décrivant l'état de l'infrastructure.

Une observation représente un fait mesuré à un instant donné.

Les observations sont :

* immuables ;
* horodatées ;
* indépendantes les unes des autres ;
* exploitables aussi bien en temps réel qu'en historique.

Cependant, une succession d'observations ne constitue pas une représentation directement exploitable par un utilisateur.

Par exemple :

```
08:00 DNS Healthy
08:05 DNS Healthy
08:10 DNS Healthy
08:15 DNS Degraded
08:20 DNS Degraded
08:25 DNS Healthy
```

L'utilisateur ne souhaite pas consulter cette liste.

Il souhaite connaître :

* l'état actuel du DNS ;
* depuis quand cet état est actif ;
* l'historique des transitions ;
* l'impact sur l'infrastructure.

Il est donc nécessaire de transformer une succession d'observations en une représentation cohérente de l'infrastructure.

---

# Décision

Ohanna-Vision introduit un composant central appelé **Projection Engine**.

Le Projection Engine est responsable de transformer une collection d'observations en une représentation métier de l'infrastructure.

Il constitue le cœur fonctionnel de Ohanna-Vision.

---

# Principe fondamental

Les observations représentent la vérité.

Les projections représentent des vues calculées de cette vérité.

Une projection peut être reconstruite à tout moment à partir des observations.

Les observations ne doivent jamais être modifiées pour satisfaire un besoin de présentation.

---

# Responsabilités

Le Projection Engine est responsable de :

* construire l'état courant des capacités ;
* construire les services ;
* construire les nœuds ;
* construire l'état global de l'infrastructure ;
* calculer les transitions d'état ;
* calculer la durée d'un état (`state_since`) ;
* préparer les informations utilisées par les vues.

Le Projection Engine ne conserve pas les observations.

Il les transforme.

---

# Position dans l'architecture

```
                 Observations
                       │
                       ▼
               ObservationStore
                       │
                history()
                       │
                       ▼
               Projection Engine
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
 CapabilityReducer ServiceReducer NodeReducer
        │              │              │
        └──────────────┼──────────────┘
                       ▼
          InfrastructureReducer
                       │
                       ▼
            InfrastructureState
                       │
                       ▼
              Dashboard / API / Views
```

Le Projection Engine constitue l'unique composant chargé de produire une représentation métier de l'infrastructure.

---

# Observation Store

L'Observation Store possède une responsabilité volontairement limitée.

Il est responsable de :

* recevoir les observations ;
* conserver l'historique brut ;
* fournir les observations au Projection Engine.

Il n'est pas responsable de :

* calculer la santé ;
* construire les états ;
* construire les tableaux de bord ;
* calculer les transitions.

Cette séparation simplifie considérablement son implémentation.

---

# Les Reducers

Le Projection Engine est composé de plusieurs composants spécialisés.

## CapabilityReducer

Construit un `CapabilityState` à partir des observations d'une capacité.

Il détermine notamment :

* le dernier état connu ;
* la date de début de cet état ;
* le dernier message ;
* la dernière latence ;
* les dernières métadonnées.

---

## ServiceReducer

Construit un `ServiceState` à partir des capacités.

---

## NodeReducer

Construit un `NodeState` à partir des services.

---

## InfrastructureReducer

Construit un `InfrastructureState` à partir des nœuds.

---

# Le Projection Engine orchestre

Le Projection Engine ne contient qu'un minimum de logique.

Il orchestre les différents reducers.

Son rôle est de coordonner les étapes de projection.

---

# Pourquoi utiliser une projection ?

Cette architecture présente plusieurs avantages.

## Recalcul complet

Une projection peut être reconstruite à partir de l'historique complet.

Aucune information métier n'est perdue.

---

## Historique

Il devient possible de reconstruire l'état de l'infrastructure à n'importe quel instant.

Exemples :

* aujourd'hui ;
* hier à 14h00 ;
* au début d'un incident ;
* avant une mise à jour.

---

## Plusieurs vues

Les mêmes observations peuvent produire plusieurs représentations.

Exemples :

* tableau de bord ;
* historique ;
* rapports ;
* statistiques ;
* API REST ;
* export.

Le Dashboard n'est qu'une projection parmi d'autres.

---

## Évolutivité

De nouvelles projections pourront être ajoutées sans modifier le stockage des observations.

Par exemple :

* Incident Engine ;
* Statistics Engine ;
* Reporting Engine ;
* Forecast Engine.

Toutes pourront utiliser les mêmes observations.

---

# Immutabilité

Le Projection Engine ne modifie jamais une observation.

Les observations constituent la source de vérité.

Toutes les représentations calculées sont jetables et peuvent être reconstruites.

---

# Séparation des responsabilités

L'architecture distingue clairement trois responsabilités.

## Observation

Les faits.

---

## Projection

La représentation métier.

---

## Présentation

L'affichage destiné à l'utilisateur.

Cette séparation permet de faire évoluer indépendamment :

* le stockage ;
* les règles métier ;
* les interfaces utilisateur.

---

# Conséquences

Cette décision implique que :

* toutes les vues de Ohanna-Vision sont construites par le Projection Engine ;
* les observations restent la seule source de vérité ;
* les états courants ne sont jamais modifiés directement ;
* toute projection peut être recalculée à partir des observations.

---

# Alternatives étudiées

## Construire directement le Dashboard

Cette approche est rejetée.

Elle mélangerait la logique métier et la présentation.

---

## Calculer les états dans Observation Store

Cette approche est rejetée.

Elle donnerait au Store plusieurs responsabilités.

Le stockage et la projection doivent rester indépendants.

---

## Modifier les observations

Cette approche est rejetée.

Une observation représente un fait.

Un fait ne doit jamais être réécrit.

---

# Décisions futures

Cette décision sera complétée par plusieurs ADR :

* Health Engine ;
* History Engine ;
* Statistics Engine ;
* Administration Engine ;
* Dashboard Engine.

Tous ces composants s'appuieront sur le Projection Engine.

---

# Règle fondamentale

Toute représentation affichée par Ohanna-Vision doit être le résultat d'une projection calculée à partir des observations.

Les observations constituent la vérité.

Les projections constituent leur représentation.

Cette distinction est l'un des principes fondateurs de l'architecture de Ohanna-Vision.
