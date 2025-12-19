README - Base de données (Postgres + Alembic)
===========================================

Ce fichier décrit comment démarrer une base Postgres locale, se connecter avec pgAdmin, et gérer les migrations Alembic pour ce projet.

1) Pré-requis
- Python (venv recommandé)
- Docker
- pgAdmin (optionnel : application Windows ou conteneur Docker)

2) Lancer Postgres (Docker)
Recommandé : lancer un conteneur Postgres et exposer le port 5432 vers l'hôte.

```bash
docker run -d --name pgdev \
  -e POSTGRES_USER=app \
  -e POSTGRES_PASSWORD=pass \
  -e POSTGRES_DB=shop \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:15
```

3) Lancer pgAdmin
- Option A (Windows app) : configurer un serveur avec Host `localhost`, Port `5432`, DB `shop`, User `app`, Password `pass`.
- Option B (Docker) : lancer pgAdmin sur le même réseau Docker que `pgdev` :

```bash
docker network create pg-network || true
docker network connect pg-network pgdev || true
docker run -d --name pgadmin --network pg-network -p 5050:80 \
  -e PGADMIN_DEFAULT_EMAIL=you@example.com \
  -e PGADMIN_DEFAULT_PASSWORD=admin \
  dpage/pgadmin4
# ouvrir http://localhost:5050 (you@example.com / admin)
```

Dans pgAdmin (Create Server) :
- General → Name: `shop-local` ou `shop-docker`
- Connection → Host: `localhost` (si pgAdmin app Windows) ou `pgdev` (si pgAdmin conteneur), Port: `5432`, Maintenance DB: `shop`, Username: `app`, Password: `pass`, SSL mode: `Disable`.

4) Installer Alembic et dépendances Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt || true
pip install alembic psycopg[binary]
```

Ajoute `alembic` et `psycopg[binary]` dans `requirements.txt` si tu veux les versionner.

5) Configurer la variable d'environnement

```bash
export DATABASE_URL="postgresql+psycopg://app:pass@localhost:5432/shop"
```

6) Générer et appliquer les migrations

- Générer la migration initiale (autogenerate) :

```bash
alembic revision --autogenerate -m "initial schema"
```

- Appliquer la migration :

```bash
alembic upgrade head
```

Remarque : `alembic/env.py` du projet importe désormais `models.db_models` pour que l'autogenerate détecte les tables.

7) Vérifier les tables (sans installer psql localement)

```bash
docker exec pgdev psql -U app -d shop -c "\dt"
```

8) CI / Déploiement
- Exécuter `alembic upgrade head` dans le pipeline avant de démarrer l'app en production.
- Ne pas utiliser `Base.metadata.create_all()` en production ; gère le schéma avec Alembic.

9) Sauvegarde & sécurité (rapide)
- Préférer une base managée (RDS, Supabase) en prod pour snapshots/backup automatiques.
- Ne pas stocker secrets dans le dépôt ; utiliser variables d'environnement ou vault.
- Limiter l'accès réseau à la DB (firewall / VPC).

10) Problèmes fréquents
- Erreur "authentication failed for user postgres" : vérifie l'utilisateur (ici `app`).
- Erreur "failed to resolve host 'pgdev'" : utiliser `localhost` depuis pgAdmin Windows, ou exécuter pgAdmin dans le même réseau Docker et utiliser `pgdev`.

11) Commandes utiles rapides

```bash
# lister conteneurs
docker ps
# logs postgres
docker logs pgdev --tail 50
# créer role postgres si nécessaire
docker exec pgdev psql -U app -d shop -c "CREATE ROLE postgres WITH LOGIN PASSWORD 'newpass' SUPERUSER;"
```

Fait par l'outil d'assistance : migrations initiales générées dans `alembic/versions/` et appliquées localement.
