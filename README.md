# PushUp API

Backend FastAPI/Typer pour la plateforme PushUp : architecture hexagonale (`core` + `services` + `infra`), configuration typée via Pydantic Settings et persistance PostgreSQL/Alembic. Cette base expose dès aujourd’hui la gestion des comptes utilisateurs (inscription + authentification JWT) ainsi que le catalogue d’exercices (CRUD complet).

## Pile technique

- **Langage** : Python 3.14 (géré via [`uv`](https://docs.astral.sh/uv/)).
- **Frameworks** : FastAPI (API), Typer (CLI), SQLAlchemy + Alembic (base), `python-cq` pour le bus commandes/requêtes.
- **Qualité** : Ruff, Mypy, Pytest (+ `pytest-env`/`pytest-asyncio`), couverture `pytest-cov`.
- **Conteneurisation** : `docker-compose` fournit PostgreSQL (image officielle).

## Pré-requis

1. Installer `uv` ≥ 0.4 : `curl -LsSf https://astral.sh/uv/install.sh | sh`.
2. Disposer de Docker Desktop (ou Docker Engine) pour Postgres.
3. Facultatif : `make` disponible sur l’environnement.

## Installation

```bash
cd /mnt/c/dev/pushup_hub/PushUp-api
uv sync
# créez ensuite votre fichier .env (inspiré de l'exemple ci-dessous)
```

### Variables d’environnement

`Settings` s’appuie sur `pydantic-settings` avec le séparateur `__` pour les sous-clés. Exemple de `.env` :

```dotenv
PROFILE=default
DEBUG=true
ALLOWED_HOSTS=["http://127.0.0.1:3000","http://localhost:3000"]
SECRET_KEY=change-me
DB__HOST=localhost
DB__PORT=5432
DB__NAME=pushup_api
DB__USER=root
DB__PASSWORD=root
```

## Démarrage

### Tout-en-un (Docker)

```bash
docker-compose up --build     # API + PostgreSQL
# API disponible sur http://127.0.0.1:8000
```

### Développement local

```bash
docker compose up -d          # Postgres seul
make dev                      # uvicorn main:app --reload --loop uvloop
# API disponible sur http://127.0.0.1:8000
```

CLI Typer (gestion base) :

```bash
uv run main.py --help
uv run main.py db create      # crée la base configurée
uv run main.py db drop
```

## Gestion des fonctionnalités

- **Utilisateurs**
  - `POST /users` : inscription, hash Argon2, validation email, noms optionnels.
  - `POST /auth/login` : authentification email+mot de passe, émission JWT.
  - `GET /users/me` : profil courant (JWT nécessaire).

- **Exercices**
  - `GET /exercises` / `GET /exercises/{id}` : lecture catalogue.
  - `POST /exercises` : création (auth requise).
  - `PUT /exercises/{id}` : mise à jour (auth requise).
  - `DELETE /exercises/{id}` : suppression (auth requise).

## Base de données

- `make create-db` / `make drop-db`
- `make makemigrations` puis `make migrate`
- `make init-db` : drop + create + migrate
- `make init-test-db` : prépare la base `pushup_api_test`

## Qualité & tests

```bash
make lint         # ruff format + ruff check --fix
make mypy         # typage strict
make pytest       # tests + couverture
make before-commit
```

### Jeux de tests

- Services utilisateurs : hashage Argon2, unicité email, tokens JWT.
- Exercices : commandes/queries CQRS et routes FastAPI (via `httpx.AsyncClient`).

## Structure rapide

```
src/
├─ core/                 # domaine (auth, users, exercises)
├─ services/             # services techniques (db, uuid, hasher, jwt…)
├─ infra/
│   ├─ api/              # builders + routes FastAPI
│   ├─ adapters/         # implémentations SQLAlchemy (User/Exercise)
│   ├─ cli/              # commandes Typer (db create/drop…)
│   ├─ db/               # tables + migrations Alembic
│   └─ queries/          # handlers CQRS de lecture
└─ settings.py           # configuration typée
```

## Scénarios de test rapides

1. **Inscription + login**
   - `POST /users` avec email+mot de passe.
   - `POST /auth/login` → récupérer `access_token`.
   - Appeler `GET /users/me` avec header `Authorization: Bearer <token>`.
2. **CRUD exercices**
   - Créer un exercice authentifié.
   - Mettre à jour puis supprimer l’enregistrement.
   - Vérifier que `GET /exercises` reflète les changements.

Ce socle est volontairement minimaliste mais entièrement fonctionnel : il sert de fondation pour étendre PushUp (programmation d’entraînements, historiques, etc.) en conservant les conventions du template d’origine.

