# Vision

## Pourquoi Ohanna-Vision existe

Une infrastructure fiable ne se résume pas à une succession de services en fonctionnement.

Elle doit être compréhensible.

Au fil du temps, les observations produites par les systèmes deviennent nombreuses, techniques et difficiles à interpréter.

Un serveur répond.

Un service DNS résout un nom.

Une sauvegarde s'exécute.

Un broker MQTT accepte une connexion.

Ces informations sont indispensables, mais elles ne répondent pas à la question essentielle :

> L'infrastructure est-elle capable de fournir les services attendus ?

Ohanna-Agent répond à cette question en observant les capacités de l'infrastructure.

Ohanna-Vision existe pour rendre cette réponse visible.

Son objectif n'est pas de produire davantage d'informations techniques.

Son objectif est de transformer les observations en une représentation claire, synthétique et exploitable de l'état réel de l'infrastructure.

---

# Notre vision

Nous considérons qu'un système de supervision ne doit pas seulement afficher des métriques.

Il doit raconter l'état de l'infrastructure.

Une personne doit pouvoir ouvrir Ohanna-Vision et comprendre immédiatement :

- quelles capacités sont disponibles ;
- lesquelles sont dégradées ;
- depuis quand ;
- pourquoi ;
- quelles conséquences cela entraîne.

L'information doit rester simple même lorsque l'infrastructure devient complexe.

---

# La place d'Ohanna-Vision

Ohanna-Vision n'observe jamais directement l'infrastructure.

Il ne remplace pas Ohanna-Agent.

Il ne dialogue pas avec les équipements.

Il ne réalise aucun diagnostic réseau.

Il reçoit les observations produites par Ohanna-Agent.

À partir de ces observations, il construit une représentation cohérente de l'état de l'infrastructure.

Cette séparation garantit que les responsabilités de chaque projet restent parfaitement définies.

---

# Les principes fondamentaux

## Les observations sont des faits

Une observation décrit un événement mesuré.

Elle n'est ni interprétée ni modifiée.

Ohanna-Vision conserve les observations telles qu'elles sont produites.

---

## La santé est calculée

L'état d'une capacité est une information calculée.

Il résulte d'un ensemble d'observations successives.

Une observation ne représente donc pas, à elle seule, la santé d'un service.

---

## Les capacités sont plus importantes que les machines

Une machine peut tomber en panne sans que la capacité disparaisse.

Inversement, plusieurs machines peuvent fonctionner alors que la capacité n'est plus disponible.

Ohanna-Vision présente les capacités de l'infrastructure avant les équipements qui les composent.

---

## L'historique est essentiel

Comprendre un incident nécessite de connaître son évolution.

Ohanna-Vision conserve l'historique des observations afin de permettre l'analyse des changements d'état dans le temps.

---

## L'interface doit rester lisible

Le rôle d'Ohanna-Vision n'est pas d'afficher toutes les données disponibles.

Il est de présenter les informations réellement utiles à la compréhension de l'état de l'infrastructure.

Chaque écran doit privilégier la simplicité, la cohérence et la rapidité de lecture.

---

# Ce qu'Ohanna-Vision n'est pas

Ohanna-Vision n'est pas un logiciel de supervision classique.

Il n'est pas un moteur de collecte.

Il n'est pas un ordonnanceur.

Il n'exécute aucun test réseau.

Il n'interroge pas directement les services.

Il ne remplace pas Home Assistant.

Il ne remplace pas Ohanna-Agent.

---

# Les objectifs du projet

À terme, Ohanna-Vision devra permettre de :

- visualiser l'état global de l'infrastructure ;
- afficher la santé de chaque capacité ;
- consulter l'historique des observations ;
- suivre les changements d'état ;
- comprendre rapidement les causes d'une dégradation ;
- fournir une interface utilisable même lorsque Home Assistant est indisponible.

---

# Notre ambition

Ohanna-Agent garantit les capacités de l'infrastructure.

Ohanna-Vision les rend visibles.

Ensemble, ils constituent une plateforme capable de mesurer, comprendre et expliquer l'état réel d'une infrastructure domestique.

---

# L'administration de l'infrastructure

Comprendre l'infrastructure est une première étape.

Pouvoir l'administrer depuis la même interface constitue son prolongement naturel.

À terme, Ohanna-Vision deviendra également le point d'entrée de l'administration des composants de l'écosystème Ohanna.

Selon les capacités exposées par Ohanna-Agent et ses plugins, Ohanna-Vision pourra notamment permettre :

- consulter les baux DHCP actifs ;
- gérer les réservations DHCP statiques ;
- visualiser les équipements connus ;
- modifier certaines configurations des plugins ;
- installer ou mettre à jour des plugins ;
- consulter les journaux d'exécution ;
- lancer des observations ou des diagnostics à la demande ;
- déclencher certaines actions d'administration.

Ohanna-Vision ne réalise pas directement ces opérations.

Il s'appuie sur les API exposées par Ohanna-Agent, qui reste le seul responsable de l'exécution des actions sur l'infrastructure.

Cette architecture garantit qu'une même logique métier peut être utilisée aussi bien par l'interface web que par une interface en ligne de commande ou toute autre application.