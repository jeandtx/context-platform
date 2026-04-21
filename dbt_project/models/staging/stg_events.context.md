# Contexte Métier — stg_events

## Objectifs

- **Finalité** : Fournir une table brute de tous les événements sportifs qui se produisent pendant les matchs, permettant l'analyse détaillée du déroulement du jeu.
- **Grain** : Une ligne par événement unique (action ou situation) dans un match donné.

## Transformations

- **Source** : Données brutes depuis `raw_events` contenant tous les événements de match avec contexte spatio-temporel et tactique.
- **Transformation** :
    - Aucune transformation majeure n'est effectuée à ce stade.
    - Les colonnes sont recopiées telles quelles (pas de renommage, filtre ou agrégation).
    - Les données conservent leur structure originale pour permettre une analyse flexible en aval.
- **Exclusions** : Aucune exclusion.

## Champs attendus

| Champ                   | Format    | Nomenclature           | Règles/Tests                                                      |
| ----------------------- | --------- | ---------------------- | ----------------------------------------------------------------- |
| ID d'événement          | Entier    | `event_id`             | Obligatoire, unique par match                                     |
| ID de match             | Entier    | `match_id`             | Obligatoire, référence externe                                    |
| Index d'événement       | Entier    | `event_index`          | Obligatoire, ordre chronologique croissant par match              |
| Type d'événement (ID)   | Entier    | `event_type_id`        | Obligatoire, référence à la classification d'événements           |
| Type d'événement (nom)  | Texte     | `event_type_name`      | Obligatoire (ex: pass, shot, dribble, foul, substitution)         |
| Période                 | Entier    | `period`               | Obligatoire (1, 2 pour temps réglem., 3+ pour prolongations)      |
| Minute                  | Entier    | `minute`               | Obligatoire, minute de jeu                                        |
| Seconde                 | Entier    | `second`               | Obligatoire, seconde dans la minute                               |
| Timestamp               | Datetime  | `timestamp`            | Obligatoire, date/heure précise de l'événement                    |
| ID équipe               | Entier    | `team_id`              | Généralement fourni, peut être NULL pour certains événements      |
| Nom équipe              | Texte     | `team_name`            | Généralement fourni, NULL possible                                |
| ID joueur               | Entier    | `player_id`            | Optionnel, NULL si événement collectif ou sans joueur spécifique  |
| Nom joueur              | Texte     | `player_name`          | Optionnel, NULL possible                                          |
| Position joueur (ID)    | Entier    | `position_id`          | Optionnel, NULL possible                                          |
| Position joueur (nom)   | Texte     | `position_name`        | Optionnel (ex: Goalkeeper, Defender, Midfielder, Forward)         |
| Localisation X          | Numérique | `location_x`           | Optionnel, système de coordonnées à clarifier (voir Incertitudes) |
| Localisation Y          | Numérique | `location_y`           | Optionnel, système de coordonnées à clarifier                     |
| ID équipe en possession | Entier    | `possession_team_id`   | Optionnel, peut être NULL                                         |
| Équipe en possession    | Texte     | `possession_team_name` | Optionnel, contexte du jeu                                        |
| ID motif de jeu         | Entier    | `play_pattern_id`      | Optionnel, identifiant numérique du motif de jeu                  |
| Motif de jeu            | Texte     | `play_pattern_name`    | Optionnel (ex: Regular Play, Throw In, Corner Kick, etc.)         |
| Durée de l'événement    | Numérique | `duration`             | Optionnel, durée en secondes de l'action                          |
| Séquence de possession  | Entier    | `possession`           | Optionnel, numéro de séquence de possession dans le match         |
| Sous pression           | Booléen   | `under_pressure`       | Optionnel, NULL possible                                          |
| Hors caméra             | Booléen   | `off_camera`           | Optionnel, NULL possible                                          |
| Hors jeu                | Booléen   | `out`                  | Optionnel, NULL possible                                          |
| Counter-press           | Booléen   | `counterpress`         | Optionnel, NULL possible                                          |
| Détails passe           | Struct    | `pass`                 | Optionnel, NULL si l'événement n'est pas une passe                |
| Détails tir             | Struct    | `shot`                 | Optionnel, NULL si l'événement n'est pas un tir                   |
| Détails conduite        | Struct    | `carry`                | Optionnel, NULL si l'événement n'est pas une conduite de balle    |
| Détails dribble         | Struct    | `dribble`              | Optionnel, NULL si l'événement n'est pas un dribble               |
| Détails duel            | Struct    | `duel`                 | Optionnel, NULL si l'événement n'est pas un duel                  |
| Détails dégagement      | Struct    | `clearance`            | Optionnel, NULL si l'événement n'est pas un dégagement            |
| Détails blocage         | Struct    | `block`                | Optionnel, NULL si l'événement n'est pas un blocage               |
| Détails interception    | Struct    | `interception`         | Optionnel, NULL si l'événement n'est pas une interception         |
| Détails gardien         | Struct    | `goalkeeper`           | Optionnel, NULL si l'événement n'implique pas le gardien          |
| Détails faute commise   | Struct    | `foul_committed`       | Optionnel, NULL si l'événement n'est pas une faute commise        |
| Détails faute obtenue   | Struct    | `foul_won`             | Optionnel, NULL si l'événement n'est pas une faute obtenue        |
| Détails mauvais comport.| Struct    | `bad_behaviour`        | Optionnel, NULL si l'événement n'est pas un carton                |
| Détails réception balle | Struct    | `ball_receipt`         | Optionnel, NULL si l'événement n'est pas une réception de balle   |
| Détails récupération    | Struct    | `ball_recovery`        | Optionnel, NULL si l'événement n'est pas une récupération         |
| Détails mauvais contrôle| Struct    | `miscontrol`           | Optionnel, NULL si l'événement n'est pas un mauvais contrôle      |
| Détails substitution    | Struct    | `substitution`         | Optionnel, NULL si l'événement n'est pas une substitution         |
| Tactics                 | Struct    | `tactics`              | Optionnel, structure à clarifier (JSON, texte libre, structured)  |

## Tests de logique métier

1. **Vérification du grain** :
    - Chaque ligne doit correspondre à un événement unique, identifié par `event_id` au sein d'un match (`match_id`).
    - Les événements d'un même match doivent être ordonnés par `event_index` croissant.
2. **Validation des données** :
    - `event_id`, `match_id`, `event_type_id`, `period`, `minute`, `second`, `timestamp` doivent être NOT NULL.
    - `event_type_name` doit correspondre à une valeur attendue (pass, shot, dribble, foul, substitution, etc.).
    - Les coordonnées `location_x` et `location_y` doivent respecter le système de coordonnées défini.
3. **Tests unitaires suggérés** :
    - Vérifier que chaque match contient des événements, ordonnés par `event_index`.
    - Valider que les valeurs booléennes ne contiennent que TRUE, FALSE ou NULL (pas d'autres valeurs).
    - Tester l'absence de trous importants dans les données (ex: progression normale du `minute` dans le temps).
    - Vérifier que les équipes et joueurs référencés existent dans les tables de référence.

## Notes

- **Incertitudes** :
    - Le système de coordonnées pour `location_x` et `location_y` n'est pas spécifié (normalisé 0–100, mètres, pixels ?).
    - Le champ `tactics` contient-il des données structurées (JSON) ou du texte libre ?
    - Tous les événements disposent-ils systématiquement d'une position (x, y) ?
    - Certaines actions (ex: pass) comportent-elles toujours des informations complètes, ou certaines peuvent-elles être vides selon le type d'événement ?
    - Les valeurs booléennes sont-elles toujours renseignées ou peuvent-elles être NULL ?
    - La fraîcheur et couverture des données : tous les matchs et tous les événements sont-ils présents ?
- **Validation** : À compléter par [Nom du validateur] et [Date].
