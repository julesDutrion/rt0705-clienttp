# Client de vidéothèque

Application web Flask/Jinja2 présentant le catalogue de films et ses supports,
avec gestion des comptes et des emprunts via l'API Flask de vidéothèque.

## Fonctionnalités

- Consultation et filtrage du catalogue par titre, genre, réalisateur, langue,
  acteur et type de support.
- Consultation des supports physiques et numériques, de leur disponibilité et
  emprunt d'un support physique disponible par un utilisateur connecté.
- Inscription avec confirmation du mot de passe, connexion JWT et modification
  du compte personnel.
- Gestion des comptes, des rôles et des suppressions réservée à l'administrateur.
- Consultation des emprunts personnels et de leur historique; recherche globale
  ou par login, détails et retour réservés aux gestionnaires et administrateurs.
- Gestion des références du catalogue et des types de supports par les rôles
  autorisés.

## Prérequis

- Python 3.12 ou plus récent pour le développement local.
- Une instance accessible de l'API Flask de vidéothèque.
- Docker, uniquement pour construire et exécuter l'image.

## Installation et lancement en développement

Depuis la racine du dépôt :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r client/requirements.txt -r requirements-dev.txt
cp .env.example .env
```

Renseignez les valeurs dans `.env`, puis lancez le client :

```bash
python client/app.py
```

L'application est accessible par défaut à `http://127.0.0.1:5001`. `CLIENT_DEBUG`
ne doit rester activé qu'en développement.

## Configuration

| Variable | Valeur par défaut | Utilisation |
| --- | --- | --- |
| `API_BASE_URL` | `http://localhost:5000` | URL de base de l'API. |
| `API_TIMEOUT` | `5` | Délai maximal, en secondes, des requêtes API. |
| `CLIENT_HOST` | `127.0.0.1` | Adresse d'écoute du serveur de développement Flask. |
| `CLIENT_PORT` | `5001` | Port du serveur de développement Flask. |
| `CLIENT_DEBUG` | `false` | Active le mode debug Flask si la valeur est `true`. |
| `SECRET_KEY` | `dev-only-change-me` | Clé de signature des sessions Flask; définissez une valeur aléatoire et privée hors développement. |

Ne commitez jamais `.env` ni une vraie clé secrète. Dans Docker, l'URL de l'API
doit être joignable depuis le conteneur; `localhost` désigne le conteneur
lui-même.

## Contrat API utilisé

Les services du client utilisent les routes et formats confirmés par le
contrôleur API fourni :

- `POST /auth/login` avec `login` et `password`; la réponse contient `user` et
  `accessToken`.
- `POST /users` pour l'inscription, avec `login`, `email`, `password`,
  `confirmPassword` et `birthDate`.
- `GET /users`, `PUT /users/<idUser>/role` et `DELETE /users/<idUser>` pour les
  opérations d'administration; `GET` et `PUT /users/<idUser>` pour le compte.
- `GET /films` avec les filtres pris en charge par l'API, et
  `GET /films/<idFilm>` pour le détail.
- `GET /supports/film/<idFilm>` et `GET /support-types` pour les supports.
- `POST /loans` avec `idPhysicalSupport`, `GET /loans/me` et
  `GET /loans/me/<idLoan>` pour les emprunts personnels.
- `GET /loans`, `GET /loans/<idLoan>`, `GET /loans/user/<login>` et
  `PATCH /loans/<idLoan>/return` pour les gestionnaires et administrateurs.

Le jeton est transmis à l'API en `Authorization: Bearer <token>`. Les
permissions restent vérifiées par l'API; le client adapte aussi les pages et
les actions visibles aux rôles de la session.

## Tests

Les tests utilisent pytest et remplacent les appels HTTP pour ne pas dépendre
d'une API en fonctionnement :

```bash
./run_tests.sh
```

Le lanceur utilise `.venv/bin/python` s'il existe, sinon `python3`. Il accepte
les arguments pytest, par exemple pour lancer un fichier précis :

```bash
./run_tests.sh tests/test_api_client.py
```

## Image de production

Le Dockerfile utilise Gunicorn, et le contexte de construction est `client/` :

```bash
cp .env.example .env
# Configurez notamment API_BASE_URL et SECRET_KEY dans .env.
docker build -f Dockerfile -t videotheque-client client
docker run --rm --env-file .env -p 5001:5001 videotheque-client
```

Configurez un `SECRET_KEY` robuste et une `API_BASE_URL` accessible au
conteneur. En production, exposez le service derrière un proxy HTTPS et ne
publiez pas le fichier `.env`.

## Organisation du code

- `client/controllers/` : routes Flask, validation des rôles et rendu Jinja2.
- `client/services/` : orchestration des formulaires et appels à l'API.
- `client/models/` : DTO de l'API et sérialisation des données.
- `client/view/templates/` et `client/view/static/` : pages Jinja2, CSS et
  JavaScript des formulaires.
- `tests/` : tests pytest des routes, services, validations et erreurs.
