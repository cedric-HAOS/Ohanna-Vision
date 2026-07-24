# Administration graphique

Ohana-Vision 1.2.0 permet d'administrer le DHCP et l'architecture sans modifier
directement les fichiers YAML. Vision présente les formulaires et transmet les
changements à l'API locale authentifiée d'Ohana-Agent. Agent valide et écrit
seul la configuration.

## Ouvrir la configuration

1. Ouvrir `http://ADRESSE_DU_SERVEUR:8000`.
2. Choisir **Configuration** dans la barre latérale.
3. Choisir **Baux DHCP** ou **Architecture**.

## Cartographier les équipements

La vue Architecture représente chaque équipement dans une cellule de grille.

1. Activer le mode **Déplacer**.
2. Faire glisser un équipement vers la cellule souhaitée.
3. Si la cellule est occupée, les deux équipements échangent leur position.
4. Cliquer sur **Appliquer l'architecture** pour rendre les positions
   persistantes.

Les coordonnées enregistrées restent les cellules logiques `column` et `row`.
Le navigateur calcule seul les coordonnées d'affichage.

## Gérer les services

1. Cliquer sur l'équipement qui héberge le service.
2. Vérifier son adresse IP.
3. Dans **Services associés**, choisir un service ou cliquer sur
   **Ajouter un service**.
4. Renseigner le type, le port, l'implémentation, l'activation et la criticité.
5. Enregistrer le brouillon puis appliquer l'architecture.

Un service est rattaché au nœud de l'équipement sélectionné. Un équipement doit
donc avoir une adresse IP avant de pouvoir héberger un service.

## Créer ou modifier une liaison

1. Activer le mode **Relier**.
2. Cliquer sur l'équipement source.
3. Cliquer sur l'équipement de destination.
4. Compléter la technologie, le sens, le débit et le libellé dans l'inspecteur.
5. Enregistrer puis appliquer l'architecture.

Cliquer directement sur une ligne existante ouvre le même inspecteur. La source
et la destination peuvent être changées : un équipement peut ainsi être relié
à la box, à un commutateur déterminé, à un point d'accès ou à tout autre
équipement déclaré.

## Sécurité et validation

- le jeton Agent n'est jamais envoyé au navigateur ;
- toute application complète demande confirmation ;
- Agent refuse les références inconnues, les positions dupliquées et les
  liaisons invalides ;
- les écritures sont atomiques et la configuration précédente est préservée en
  cas d'échec.
