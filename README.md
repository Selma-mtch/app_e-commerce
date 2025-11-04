# 🛒 Projet E‑commerce (Web + Services)

Application e‑commerce en Python/Flask avec architecture en couches, dépôts mémoire ou SQLAlchemy, authentification sécurisée (bcrypt), CSRF activé et interface web Bootstrap.

## Sommaire

- Fonctionnalités
- Démarrage rapide (dev/local)
- Configuration (env vars)
- Base de données
- Déploiement (Render)
- Tests & CI
- Sécurité
- Structure

## Fonctionnalités

Client
- Inscription / Connexion (bcrypt)
- Catalogue produits (recherche)
- Panier (boutons HTMX qui mettent à jour le compteur)
- Checkout + réservation de stock + paiement simulé
- Suivi et annulation des commandes
- Support (tickets/messages)

Admin
- Catalogue administrable (activer/désactiver)
- Retrait d’un produit inactif des paniers
- Commandes: valider, expédier, livrer, rembourser (règles d’état)
- Support: lister/voir/clore tickets

Compte utilisateur
- Modifier adresse, email (avec mot de passe), mot de passe (min 8)

## Démarrage rapide (dev/local)

Prérequis: Python 3.10+

```bash
git clone <repo>
cd ecommerce
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Lancer l’app web (lit APP_CONFIG, PORT)
python run_web.py
# http://127.0.0.1:5000 par défaut
```

Notes dev
- En développement, des données de démo peuvent être activées; elles sont idempotentes (pas de doublons si la base contient déjà des produits).
- En production, le seed de démo est désactivé.
- Image produit par défaut: `static/img/default-product.svg`.

## Configuration (variables d’environnement)

- `APP_CONFIG` = `development` | `production` | `testing` (défaut: development)
- `SECRET_KEY` (obligatoire en production)
- `DATABASE_URL` (PostgreSQL/SQLite, ex: `postgresql+psycopg://…`)
- `PORT` (honoré par `run_web.py` et Gunicorn)
- `DB_AUTO_CREATE` (crée les tables si besoin; activé par défaut en prod)
- `LOAD_SAMPLE_DATA` (False en production par défaut)

## Base de données

- Si `DATABASE_URL` est défini, l’app utilise SQLAlchemy (`db/core.py`).
- Normalisation Postgres: `postgres://` → `postgresql+psycopg://`.
- Repositories DB: transactions via `sessionmaker.begin()` (évite les erreurs `SessionTransaction.execute`).

## Déploiement (Render)

Start command recommandé (Gunicorn):

```bash
gunicorn 'web.app:create_app("production")' --bind 0.0.0.0:$PORT --workers ${WEB_CONCURRENCY:-2}
```

Variables conseillées:
- `APP_CONFIG=production`
- `SECRET_KEY=<valeur aléatoire longue>`
- `DATABASE_URL=<URL Postgres>` (ajouter `?sslmode=require` si nécessaire)

Santé/port
- L’appli se lie à `$PORT`; Render détecte et publie automatiquement le service.

## Tests & CI

Lancer localement:
```bash
pytest -q
```

CI GitHub Actions: `.github/workflows/python-tests.yml` exécute les tests sur chaque `push` et `pull_request` (Python 3.10).

### Cas de tests réalisés

- Authentification
  - Inscription d’un utilisateur
  - Rejet email dupliqué
  - Connexion valide / invalide
  - Changement d’email (succès et erreurs: mot de passe actuel invalide, email déjà pris)
  - Changement de mot de passe (succès et erreurs: confirmation différente, mot de passe trop court)
- Catalogue
  - Liste des produits actifs
  - Recherche par nom/description
  - Accès aux produits inactifs: non‑admin redirigé, admin autorisé
- Panier
  - Ajout requiert d’être connecté
  - Ajout après connexion (flux complet)
  - Requête HTMX: retour du badge compteur sans erreur
  - Produit inexistant: gestion côté HTMX (200 avec badge) et non‑HTMX (redirigé)
- Commandes
  - Checkout depuis le panier (création de commande)
  - Paiement carte (succès)
  - Rollback si une réservation de stock échoue
  - Checkout interdit si panier vide (redirigé)
- Backoffice Admin
  - Accès interdit aux non‑admins
  - Création de produit (formulaire)
  - Basculer actif/inactif: retrait du produit de tous les paniers
  - Cycle commande: valider → expédier → livrer; remboursement refusé après livraison
  - Toggle sur produit inexistant: pas de crash
- Support
  - Création d’un ticket et listage
  - Accès restreint: un utilisateur ne peut pas accéder aux tickets d’autrui
- CSRF
  - POST sans token (ex. add‑to‑cart): message d’avertissement + redirection (pas de 500)
- Intégration DB (prod‑like)
  - Changement d’email/mot de passe persistant via dépôt SQLAlchemy (tests dédiés)

## Sécurité

- Mots de passe: `bcrypt` (voir `services/auth/password_hasher.py`).
- CSRF: activé (Flask‑WTF) avec gestion d’erreur (message + redirection).
- Sessions: gestion en mémoire (démo). Pour une prod réelle, utiliser Redis pour les sessions.

Réinitialiser/créer un admin (si changement de hash)
- Mettre à jour `users.password_hash` avec un hash `bcrypt` (ou créer un nouvel utilisateur et `is_admin=true`).

## Structure (extrait)

```
web/                 # Application Flask (routes, templates, statiques)
services/            # Logique métier (auth, catalogue, commandes…)
repositories/        # Accès données (mémoire + SQLAlchemy)
models/              # Modèles de domaine
tests/               # Suite PyTest
run_web.py           # Lancement local, bind sur $PORT en conteneur
```

---

Contributions bienvenues (PEP8, types, tests). Ouvrez une PR si vous souhaitez améliorer la couverture, ajouter une route `/health` ou un backend de sessions (Redis).
