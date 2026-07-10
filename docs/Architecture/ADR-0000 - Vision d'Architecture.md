# ADR-0000 — Vision d’Architecture

## Statut

Accepté

## Date

10 juillet 2026

## Contexte

Ohanna-Vision est l’interface web de l’écosystème Ohanna.

Le projet naît après la mise en place des premières fondations d’Ohanna-Agent, capable de produire des observations structurées sur l’infrastructure et les capacités qu’elle doit garantir.

Ces observations peuvent décrire, par exemple :

* la disponibilité d’un service DNS ;
* le fonctionnement d’un serveur DHCP ;
* l’accès à Internet ;
* l’état d’un broker MQTT ;
* la disponibilité de Home Assistant ;
* l’état d’une capacité Z-Wave ;
* la réussite d’une sauvegarde ;
* la latence ou les informations techniques associées à une vérification.

Ohanna-Agent transforme l’exécution de contrôles techniques en observations structurées.

Cependant, ces observations restent destinées à une exploitation logicielle. Elles ne constituent pas, à elles seules, une interface compréhensible pour l’utilisateur.

Il est nécessaire de disposer d’un composant capable de :

* présenter l’état actuel des capacités ;
* conserver et afficher leur historique ;
* synthétiser la santé globale de l’infrastructure ;
* expliquer les dégradations ;
* permettre certaines opérations d’administration ;
* rester disponible indépendamment de Home Assistant.

Ohanna-Vision répond à ce besoin.

Cette décision définit son rôle, ses limites et sa place dans l’architecture globale de l’écosystème Ohanna.

---

# Décision

Ohanna-Vision sera conçu comme une application web indépendante, responsable de la visualisation, de l’historisation et de l’administration de l’écosystème Ohanna.

Ohanna-Vision ne supervisera jamais directement l’infrastructure.

Il ne réalisera pas lui-même les contrôles DNS, DHCP, MQTT, NTP, Internet, Home Assistant ou Z-Wave.

Il utilisera les observations, les états et les opérations exposés par Ohanna-Agent.

La séparation fondamentale est la suivante :

> Ohanna-Agent observe et agit sur l’infrastructure.
> Ohanna-Vision présente, explique et administre l’infrastructure par l’intermédiaire d’Ohanna-Agent.

---

# Responsabilité principale

La responsabilité principale d’Ohanna-Vision est de transformer les informations produites par Ohanna-Agent en une représentation compréhensible de l’infrastructure.

Cette représentation doit permettre à l’utilisateur de comprendre rapidement :

* quelles capacités sont disponibles ;
* quelles capacités sont dégradées ;
* quelles capacités sont indisponibles ;
* quelles informations sont inconnues ou obsolètes ;
* depuis quand un état est observé ;
* quels services ou nœuds sont concernés ;
* quelles conséquences une dégradation peut avoir ;
* quelles actions d’administration sont disponibles.

Ohanna-Vision privilégie les capacités rendues par l’infrastructure plutôt que les machines et les logiciels qui les implémentent.

---

# Position dans l’écosystème Ohanna

L’écosystème est organisé autour de plusieurs projets indépendants.

## Ohanna-House

Ohanna-House constitue la documentation de référence de l’infrastructure.

Il décrit notamment :

* l’architecture cible ;
* les équipements ;
* les services ;
* l’adressage ;
* les procédures ;
* les décisions d’architecture ;
* les capacités attendues.

Ohanna-House décrit l’infrastructure.

Il ne l’observe pas et ne l’administre pas.

---

## Ohanna-Agent

Ohanna-Agent est le moteur d’exécution de l’écosystème.

Il est responsable de :

* charger la description déclarative de l’infrastructure ;
* charger les plugins ;
* exécuter les observations ;
* interroger les services et les équipements ;
* produire des résultats techniques ;
* générer des observations normalisées ;
* maintenir l’état opérationnel nécessaire à son fonctionnement ;
* exposer les opérations d’administration autorisées ;
* exécuter les actions sur l’infrastructure ;
* publier les événements nécessaires aux autres composants.

Ohanna-Agent est le seul composant autorisé à communiquer directement avec l’infrastructure pour les fonctions de supervision et d’administration prises en charge par l’écosystème.

---

## Ohanna-Vision

Ohanna-Vision est l’interface web de l’écosystème.

Il est responsable de :

* recevoir ou consulter les observations produites par Ohanna-Agent ;
* afficher l’état actuel des capacités ;
* conserver et présenter l’historique ;
* afficher les changements d’état ;
* construire une vue synthétique de l’infrastructure ;
* proposer une interface d’administration ;
* transmettre les demandes d’administration à Ohanna-Agent ;
* afficher le résultat des actions exécutées par Ohanna-Agent.

Ohanna-Vision ne doit contenir aucune implémentation spécifique permettant d’administrer directement un serveur DNS, DHCP, MQTT ou tout autre équipement.

---

## Ohanna-CLI

Ohanna-CLI pourra fournir une interface en ligne de commande utilisant les mêmes contrats qu’Ohanna-Vision.

Il pourra notamment permettre :

* de consulter l’état d’une capacité ;
* de lire les dernières observations ;
* de lancer un diagnostic ;
* d’exécuter une opération d’administration ;
* de gérer les plugins ;
* d’automatiser certaines opérations.

Ohanna-CLI et Ohanna-Vision doivent utiliser les mêmes interfaces publiques d’Ohanna-Agent.

Aucune logique métier importante ne devra être exclusivement implémentée dans l’un de ces clients.

---

## Ohanna-SDK

Ohanna-SDK facilitera la création, la validation et les tests des plugins compatibles avec Ohanna-Agent.

Il pourra fournir :

* les contrats de plugins ;
* les modèles communs ;
* des outils de validation ;
* des environnements de test ;
* des simulateurs ;
* des exemples de plugins ;
* des outils de packaging.

Ohanna-SDK ne sera ni une interface utilisateur ni un moteur d’exécution de production.

---

# Architecture logique

L’architecture logique cible est la suivante :

```text
                         Utilisateur
                              │
                 ┌────────────┴────────────┐
                 │                         │
          Ohanna-Vision               Ohanna-CLI
                 │                         │
                 └────────────┬────────────┘
                              │
                  Contrats publics Ohanna
                              │
                       Ohanna-Agent
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
     Observations       Administration        Plugins
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
                       Infrastructure
```

Ohanna-Vision est un client d’Ohanna-Agent.

Il ne doit pas devenir une seconde implémentation du moteur Ohanna.

---

# Architecture interne d’Ohanna-Vision

Ohanna-Vision sera organisé autour de plusieurs responsabilités logiques.

## Interface web

L’interface web présente les informations à l’utilisateur.

Elle est responsable de :

* l’affichage du tableau de bord ;
* la navigation ;
* la représentation des états ;
* l’affichage de l’historique ;
* les formulaires d’administration ;
* la visualisation des résultats d’actions ;
* la gestion des erreurs visibles par l’utilisateur.

L’interface web ne contient pas la logique d’exécution des opérations d’infrastructure.

---

## Backend de Vision

Le backend de Vision fournit les fonctions nécessaires à l’interface web.

Il pourra notamment être responsable de :

* recevoir les observations ;
* valider leur format ;
* conserver les observations ;
* construire l’état courant ;
* calculer les informations de présentation ;
* gérer les sessions utilisateur ;
* appliquer les règles d’autorisation ;
* transmettre les commandes à Ohanna-Agent ;
* suivre l’exécution des opérations ;
* fournir les API utilisées par le frontend.

Le backend de Vision ne remplace pas le cœur d’Ohanna-Agent.

---

## Stockage

Ohanna-Vision pourra disposer de son propre stockage.

Ce stockage sera utilisé pour les données nécessaires à la consultation et à la présentation, notamment :

* l’historique des observations ;
* les changements d’état ;
* les informations de session ;
* les préférences d’affichage ;
* les informations nécessaires à l’audit des actions ;
* les vues calculées destinées au tableau de bord.

Ce stockage ne doit pas devenir la source de vérité de la configuration opérationnelle d’Ohanna-Agent.

La configuration qui détermine les contrôles, les services, les capacités et les plugins exécutés reste sous la responsabilité d’Ohanna-Agent.

---

# Deux flux distincts

L’architecture distingue deux types d’échanges entre Ohanna-Agent et Ohanna-Vision.

## Flux d’observation

Le flux d’observation transporte des faits produits par Ohanna-Agent.

Il est principalement orienté d’Ohanna-Agent vers Ohanna-Vision.

Exemples :

* résultat d’une résolution DNS ;
* disponibilité d’un service ;
* latence mesurée ;
* changement d’état ;
* démarrage ou arrêt d’un plugin ;
* résultat d’un diagnostic ;
* progression d’une action.

Les observations reçues doivent être conservées sans altération de leur signification.

Ohanna-Vision peut calculer des vues, des agrégats et des états de présentation à partir de ces observations, mais ne doit pas réécrire les faits originaux.

---

## Flux d’administration

Le flux d’administration transporte une intention de l’utilisateur vers Ohanna-Agent.

Exemples :

* consulter les baux DHCP actifs ;
* créer une réservation DHCP statique ;
* modifier une réservation ;
* supprimer une réservation ;
* demander le renouvellement d’un bail ;
* modifier la configuration autorisée d’un plugin ;
* installer un plugin ;
* mettre à jour un plugin ;
* désactiver un plugin ;
* lancer une observation à la demande ;
* demander un diagnostic ;
* déclencher une action de maintenance.

Ohanna-Vision collecte et valide les informations saisies par l’utilisateur au niveau de l’interface.

Ohanna-Agent reste responsable de :

* vérifier que l’opération est supportée ;
* valider les règles métier ;
* vérifier les autorisations nécessaires ;
* exécuter l’opération ;
* gérer les erreurs ;
* produire un résultat ;
* générer les observations ou événements associés.

---

# Administration fondée sur les capacités des plugins

Toutes les fonctions d’administration ne sont pas disponibles pour tous les plugins.

Chaque plugin pourra déclarer les fonctions qu’il expose.

Un plugin DHCP pourra, par exemple, exposer :

* la lecture des baux actifs ;
* la lecture des réservations ;
* la création d’une réservation ;
* la modification d’une réservation ;
* la suppression d’une réservation.

Un plugin DNS pourra exposer :

* la consultation des serveurs configurés ;
* la gestion de certaines entrées locales ;
* le vidage d’un cache ;
* le lancement d’un test de résolution.

Un plugin de gestion de plugins pourra exposer :

* la liste des plugins installés ;
* l’installation d’un paquet ;
* la validation d’un paquet ;
* l’activation ;
* la désactivation ;
* la mise à jour ;
* la suppression.

Ohanna-Vision ne doit pas supposer qu’une action existe.

Il doit découvrir ou recevoir les opérations réellement supportées par Ohanna-Agent et ses plugins.

Cela évite de coder dans Vision une dépendance forte envers une implémentation particulière de DHCP, DNS ou de tout autre service.

---

# Contrats versionnés

Les échanges entre Ohanna-Agent et Ohanna-Vision doivent reposer sur des contrats explicites et versionnés.

Ces contrats concernent notamment :

* les observations ;
* les états ;
* les capacités ;
* les nœuds ;
* les services ;
* les plugins ;
* les commandes ;
* les résultats d’actions ;
* les erreurs ;
* les événements ;
* les fonctions d’administration disponibles.

Une évolution interne d’Ohanna-Agent ou d’Ohanna-Vision ne doit pas modifier implicitement ces contrats.

Toute modification incompatible devra faire l’objet :

* d’une décision documentée ;
* d’une nouvelle version du contrat ;
* d’une stratégie de migration ;
* d’une période de compatibilité lorsque cela est raisonnable.

---

# État courant et historique

Une observation est un fait ponctuel.

L’état courant est une projection construite à partir des observations.

L’historique est la succession des faits et des transitions dans le temps.

Ohanna-Vision doit distinguer ces trois notions.

## Observation

Une observation décrit ce qui a été mesuré à un instant donné.

Elle peut contenir :

* sa source ;
* sa date ;
* le nœud concerné ;
* le service concerné ;
* la capacité observée ;
* le statut ;
* le résultat ;
* une latence ;
* un message ;
* des métadonnées.

---

## État courant

L’état courant représente la dernière connaissance disponible pour une capacité, un service ou un nœud.

Il peut être :

* sain ;
* dégradé ;
* indisponible ;
* inconnu ;
* obsolète.

Un état obsolète signifie qu’une information précédemment connue n’a pas été renouvelée dans le délai attendu.

---

## Historique

L’historique conserve les observations nécessaires à l’analyse.

Il doit permettre de répondre à des questions telles que :

* quand la dégradation a-t-elle commencé ;
* combien de temps a-t-elle duré ;
* combien de fois s’est-elle produite ;
* quel service était concerné ;
* quelle observation a précédé le changement ;
* quelle action a permis le retour à la normale.

Ohanna-Vision pourra conserver à la fois :

* les observations brutes ;
* les transitions d’état ;
* les incidents calculés ;
* les actions d’administration et leurs résultats.

---

# Santé globale

Ohanna-Vision présentera une santé globale de l’infrastructure.

Cette santé ne devra pas être une moyenne arithmétique des états.

Elle devra prendre en compte :

* la criticité des capacités ;
* les dépendances ;
* l’état des capacités indispensables ;
* l’ancienneté des observations ;
* les états inconnus ;
* les éventuelles redondances ;
* les conséquences d’une indisponibilité.

La santé globale est une information de synthèse destinée à l’utilisateur.

Elle ne remplace pas les observations ni les calculs métier réalisés par Ohanna-Agent.

Lorsque la santé globale repose sur des règles définies par Ohanna-Agent, Vision doit les restituer plutôt que les réimplémenter.

Lorsque Vision ajoute une règle purement destinée à la présentation, celle-ci doit rester identifiable et documentée.

---

# Fonctionnement sans Home Assistant

Ohanna-Vision doit fonctionner indépendamment de Home Assistant.

Cette indépendance est une exigence d’architecture.

Elle garantit que l’état de l’infrastructure reste consultable lorsque :

* Home Assistant est indisponible ;
* Home Assistant redémarre ;
* le serveur principal est en maintenance ;
* une intégration Home Assistant est défaillante ;
* le réseau domotique rencontre un incident.

Ohanna-Vision ne doit donc pas dépendre :

* de l’interface de Home Assistant ;
* de sa base de données ;
* de ses entités ;
* de ses automatisations ;
* de son mécanisme d’authentification pour son fonctionnement essentiel.

Une intégration avec Home Assistant pourra exister, mais elle restera complémentaire.

---

# Sécurité et autorisations

La consultation et l’administration ne présentent pas le même niveau de risque.

L’architecture doit permettre de distinguer au minimum :

* la consultation ;
* le diagnostic ;
* la modification de configuration ;
* l’installation ou la mise à jour d’un plugin ;
* l’exécution d’une action d’administration ;
* les opérations critiques.

Les actions sensibles devront être :

* authentifiées ;
* autorisées ;
* validées ;
* tracées ;
* associées à un utilisateur ou à une identité technique ;
* accompagnées d’un résultat explicite.

L’interface ne doit pas masquer les conséquences d’une action.

Une opération destructive ou susceptible d’interrompre une capacité devra être clairement identifiable.

---

# Audit des actions

Toute action d’administration exécutée depuis Ohanna-Vision doit pouvoir être auditée.

Le journal d’audit devra permettre de connaître :

* l’identité à l’origine de l’action ;
* la date de la demande ;
* l’opération demandée ;
* les paramètres pertinents ;
* le composant ciblé ;
* l’acceptation ou le refus de la demande ;
* le résultat de l’exécution ;
* les erreurs éventuelles ;
* la durée de l’opération.

Les secrets, mots de passe, jetons et autres données sensibles ne doivent jamais apparaître en clair dans l’historique d’audit.

---

# Gestion des plugins

Ohanna-Vision pourra fournir une interface permettant de gérer les plugins d’Ohanna-Agent.

Cette interface pourra prendre en charge :

* la consultation des plugins disponibles ;
* la consultation des plugins installés ;
* l’affichage de leur version ;
* l’affichage de leur état ;
* le téléversement d’un paquet ;
* la validation du paquet ;
* l’installation ;
* l’activation ;
* la désactivation ;
* la mise à jour ;
* la suppression ;
* l’affichage des erreurs de chargement.

Le téléversement d’un plugin vers Ohanna-Vision ne constitue pas son installation.

Vision transmet le paquet et la demande à Ohanna-Agent.

Ohanna-Agent est responsable de :

* vérifier le format ;
* vérifier la compatibilité ;
* vérifier l’intégrité ;
* appliquer les règles de sécurité ;
* installer le plugin ;
* gérer son cycle de vie ;
* retourner le résultat.

L’installation de code tiers est une opération critique et devra être traitée comme telle.

---

# Déploiement

Ohanna-Vision doit pouvoir être déployé indépendamment d’Ohanna-Agent.

Les deux projets peuvent être installés :

* sur la même machine ;
* dans deux conteneurs distincts ;
* sur deux machines différentes ;
* selon toute autre topologie respectant les contrats de communication.

Aucune hypothèse ne doit imposer qu’Ohanna-Agent et Ohanna-Vision partagent :

* le même processus ;
* le même système de fichiers ;
* la même base de données ;
* le même cycle de mise à jour ;
* la même version applicative.

Cette indépendance permet :

* des mises à jour séparées ;
* des redémarrages indépendants ;
* une meilleure isolation ;
* une évolution progressive ;
* un déploiement adapté à la taille de l’infrastructure.

---

# Résilience

Une indisponibilité temporaire d’Ohanna-Vision ne doit pas interrompre les observations réalisées par Ohanna-Agent.

Une indisponibilité temporaire d’Ohanna-Agent ne doit pas empêcher Vision d’afficher l’historique déjà reçu.

Dans ce cas, Vision doit clairement indiquer :

* que la connexion avec Ohanna-Agent est interrompue ;
* que les informations affichées peuvent être anciennes ;
* la date de la dernière donnée reçue ;
* les fonctions d’administration devenues indisponibles.

Les observations en attente de transmission pourront être conservées par Ohanna-Agent ou par un mécanisme de transport adapté.

Le mécanisme exact sera défini dans une décision d’architecture ultérieure.

---

# Technologies

Cette décision ne choisit pas encore les technologies d’implémentation.

Elle ne détermine pas :

* le framework frontend ;
* le framework backend ;
* la base de données ;
* le protocole temps réel ;
* le mécanisme d’authentification ;
* le format de packaging ;
* la méthode de déploiement.

Ces choix devront être évalués dans des ADR séparés.

Ils devront respecter les responsabilités définies dans ce document.

---

# Principes d’architecture

## Séparation des responsabilités

Chaque composant doit conserver une responsabilité claire.

Ohanna-Agent observe et exécute.

Ohanna-Vision présente et transmet les intentions de l’utilisateur.

---

## Indépendance des clients

Ohanna-Vision ne doit pas disposer de privilèges ou d’API privées impossibles à utiliser par Ohanna-CLI.

Les fonctions publiques de l’écosystème doivent être accessibles par des contrats communs.

---

## Absence de dépendance inverse

Ohanna-Agent ne doit pas dépendre du fonctionnement d’Ohanna-Vision.

Il doit pouvoir continuer à observer l’infrastructure lorsque Vision est arrêté.

---

## Configuration sous autorité de l’Agent

Vision peut proposer une interface de modification.

Ohanna-Agent reste responsable de la validation, de l’application et de la persistance de sa configuration opérationnelle.

---

## Administration déclarée

Une fonction d’administration doit être explicitement déclarée par Ohanna-Agent ou par un plugin.

Vision ne doit pas déduire arbitrairement les opérations possibles.

---

## Traçabilité

Toute donnée affichée et toute action exécutée doivent pouvoir être reliées à une source identifiable.

---

## Compatibilité

Les échanges entre les projets doivent être versionnés afin de permettre leur évolution indépendante.

---

## Lisibilité

L’interface doit privilégier la compréhension de l’infrastructure plutôt que l’accumulation de données techniques.

---

# Ce qu’Ohanna-Vision ne doit pas devenir

Ohanna-Vision ne doit pas devenir :

* un second moteur de supervision ;
* un ordonnanceur de contrôles techniques ;
* un ensemble de scripts d’administration directs ;
* un remplaçant d’Ohanna-Agent ;
* un remplaçant de Home Assistant ;
* une base de données de configuration concurrente ;
* une interface fortement liée à une seule implémentation de service ;
* une collection de pages spécifiques codées indépendamment pour chaque équipement.

Une évolution qui introduirait l’une de ces responsabilités devra être réévaluée par une décision d’architecture.

---

# Conséquences positives

Cette décision apporte les bénéfices suivants :

* les responsabilités d’Agent et de Vision restent distinctes ;
* l’infrastructure n’est administrée que par un composant contrôlé ;
* Vision peut évoluer sans modifier les plugins d’Agent ;
* Agent peut fonctionner sans interface web ;
* une interface en ligne de commande pourra réutiliser les mêmes contrats ;
* les actions peuvent être sécurisées et auditées ;
* le tableau de bord reste indépendant de Home Assistant ;
* l’architecture supporte l’historisation ;
* les plugins peuvent exposer progressivement de nouvelles fonctions ;
* le frontend ne dépend pas directement des technologies de l’infrastructure.

---

# Conséquences négatives

Cette décision introduit également plusieurs contraintes :

* les contrats entre Agent et Vision devront être conçus avec soin ;
* les versions devront être compatibles ;
* l’administration nécessitera une API sécurisée ;
* les actions asynchrones devront être suivies ;
* les erreurs devront être représentées de manière cohérente ;
* une politique d’authentification et d’autorisation sera nécessaire ;
* l’installation de plugins demandera des protections importantes ;
* certaines données pourront être dupliquées entre Agent et Vision ;
* les responsabilités de calcul de santé devront être précisément définies ;
* le développement initial sera plus structuré qu’une interface directement connectée aux services.

Ces contraintes sont acceptées, car elles protègent la cohérence et l’évolutivité de l’écosystème.

---

# Alternatives étudiées

## Connecter directement Ohanna-Vision aux équipements

Cette solution permettrait à Vision de consulter ou modifier directement les services DNS, DHCP, MQTT ou Home Assistant.

Elle est rejetée.

Elle entraînerait :

* une duplication de la logique des plugins ;
* des accès directs multiples à l’infrastructure ;
* une sécurité plus difficile à maîtriser ;
* une forte dépendance du frontend envers les équipements ;
* une impossibilité de réutiliser simplement les fonctions dans Ohanna-CLI ;
* une confusion entre observation, administration et présentation.

---

## Intégrer Ohanna-Vision dans Ohanna-Agent

Cette solution consisterait à ajouter directement l’interface web dans le dépôt et le processus d’Ohanna-Agent.

Elle est rejetée.

Elle couplerait :

* les cycles de développement ;
* les versions ;
* les dépendances ;
* les redémarrages ;
* les technologies frontend et backend ;
* les responsabilités opérationnelles.

Une interface défaillante ne doit pas compromettre l’exécution de l’Agent.

---

## Utiliser Home Assistant comme interface principale

Cette solution consisterait à présenter les observations et les actions uniquement dans Home Assistant.

Elle est rejetée comme architecture principale.

Home Assistant pourra consommer certaines informations, mais il ne doit pas être indispensable pour consulter ou administrer l’infrastructure.

Le système de supervision doit rester accessible lorsque Home Assistant est indisponible.

---

## Faire de Vision la source de vérité de toute la configuration

Cette solution consisterait à stocker toute la configuration dans la base de données de Vision, puis à la transmettre à Agent.

Elle est rejetée pour la première architecture.

Elle rendrait Ohanna-Agent dépendant de Vision et empêcherait son fonctionnement autonome.

Vision pourra aider à modifier la configuration, mais Agent restera propriétaire de sa configuration opérationnelle.

---

# Décisions à venir

Cette décision devra être complétée par des ADR consacrés notamment :

* au contrat d’observation ;
* au contrat d’administration ;
* au protocole de communication avec Ohanna-Agent ;
* au modèle d’état courant ;
* au modèle d’historique ;
* au calcul de la santé globale ;
* à l’architecture frontend ;
* à l’architecture backend ;
* au choix du stockage ;
* au mécanisme temps réel ;
* à l’authentification ;
* aux autorisations ;
* à l’audit ;
* à la gestion et à la signature des plugins ;
* au déploiement ;
* à la stratégie de compatibilité entre versions.

---

# Règle finale

Toute évolution d’Ohanna-Vision devra respecter la règle suivante :

> Ohanna-Vision peut présenter l’infrastructure et demander son administration, mais il ne doit jamais contourner Ohanna-Agent pour l’observer ou la modifier.

Cette règle constitue la frontière fondamentale entre les responsabilités des deux projets.
