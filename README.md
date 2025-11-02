# 🛒 Projet E-commerce

Application de gestion de boutique en ligne développée en Python avec une architecture en couches.

## 📋 Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure du projet](#structure-du-projet)
- [Tests](#tests)
- [Documentation](#documentation)
- [Contribution](#contribution)

## ✨ Fonctionnalités

### Pour les clients
- ✅ Inscription et authentification
- ✅ Navigation dans le catalogue de produits
- ✅ Gestion du panier d'achat
- ✅ Passage de commande avec validation de stock
- ✅ Paiement par carte bancaire
- ✅ Suivi des commandes
- ✅ Demande d'annulation
- ✅ Service client avec système de tickets

### Pour les administrateurs
- ✅ Validation des commandes
- ✅ Gestion des expéditions
- ✅ Marquage des livraisons
- ✅ Remboursements
- ✅ Gestion du service client

## 🏗️ Architecture

Le projet suit une **architecture en couches** pour une meilleure maintenabilité :

```
┌─────────────────────────────────┐
│     Services (Logique métier)   │
├─────────────────────────────────┤
│   Repositories (Accès données)  │
├─────────────────────────────────┤
│      Models (Structures données)│
└─────────────────────────────────┘
```

### Principes appliqués
- **Separation of Concerns** : Chaque couche a une responsabilité unique
- **Dependency Injection** : Les services reçoivent leurs dépendances
- **Single Responsibility** : Une classe = une responsabilité
- **Type Hints** : Typage statique pour plus de robustesse

## 📦 Installation

### Prérequis
- Python 3.10 ou supérieur

### Installation basique
```bash
# Cloner le repository
git clone https://github.com/votre-username/ecommerce.git
cd ecommerce

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances (quand elles seront ajoutées)
pip install -r requirements.txt
```

## 🚀 Utilisation

### Lancer la démonstration
```bash
python main.py
```

Cette commande exécute un scénario complet :
1. Création de produits
2. Inscription d'utilisateurs
3. Ajout au panier
4. Passage de commande
5. Paiement
6. Expédition
7. Service client

### Exemple d'utilisation programmatique

```python
from ecommerce.models import User, Product
from ecommerce.repositories import UserRepository, ProductRepository
from ecommerce.services import AuthService, CatalogService

# Initialisation
users = UserRepository()
products = ProductRepository()
sessions = SessionManager()
auth = AuthService(users, sessions)

# Inscription
user = auth.register(
    email="client@example.com",
    password="secure_password",
    first_name="Jean",
    last_name="Dupont",
    address="123 Rue de Paris"
)

# Connexion
token = auth.login("client@example.com", "secure_password")
```

## 📁 Structure du projet

```
ecommerce/
├── models/              # Modèles de données
│   ├── user.py
│   ├── product.py
│   ├── order.py
│   ├── invoice.py
│   ├── payment.py
│   ├── delivery.py
│   └── support.py
│
├── repositories/        # Couche d'accès aux données
│   ├── user_repository.py
│   ├── product_repository.py
│   ├── cart_repository.py
│   ├── order_repository.py
│   ├── invoice_repository.py
│   ├── payment_repository.py
│   └── thread_repository.py
│
├── services/           # Logique métier
│   ├── auth/
│   │   ├── password_hasher.py
│   │   ├── session_manager.py
│   │   └── auth_service.py
│   ├── catalog_service.py
│   ├── cart_service.py
│   ├── order_service.py
│   ├── billing_service.py
│   ├── delivery_service.py
│   ├── payment_gateway.py
│   └── customer_service.py
│
└── main.py            # Point d'entrée
```

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Avec couverture de code
pytest --cov=ecommerce --cov-report=html

# Tests spécifiques
pytest tests/test_services.py
```

## 📚 Documentation

### Génération de la documentation
```bash
cd docs
make html
```

La documentation sera disponible dans `docs/_build/html/index.html`

### Classes principales

#### Models
- **User** : Représente un utilisateur
- **Product** : Un produit du catalogue
- **Order** : Une commande avec ses états
- **Invoice** : Facture générée
- **Payment** : Transaction de paiement
- **Delivery** : Information de livraison

#### Services
- **AuthService** : Authentification et inscription
- **OrderService** : Gestion complète des commandes
- **CartService** : Gestion du panier
- **CustomerService** : Support client

## 🔒 Sécurité

⚠️ **Note importante** : Cette version utilise un hash simplifié pour les mots de passe.

**En production, vous DEVEZ** :
- Utiliser `bcrypt`, `argon2` ou `scrypt` pour les mots de passe
- Implémenter HTTPS
- Ajouter une protection CSRF
- Valider toutes les entrées utilisateur
- Utiliser une vraie base de données avec transactions
- Implémenter un rate limiting
- Logger les actions sensibles

## 🛣️ Roadmap

- [ ] API REST avec FastAPI
- [ ] Base de données PostgreSQL
- [ ] Frontend React
- [ ] Intégration Stripe réelle
- [ ] Système de notifications par email
- [ ] Gestion des stocks en temps réel
- [ ] Statistiques et dashboard admin
- [ ] Système de recommandations
- [ ] Multi-devises et multi-langues

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Guidelines
- Suivre PEP 8
- Ajouter des tests pour les nouvelles fonctionnalités
- Documenter avec des docstrings
- Utiliser le type hinting

## 👥 Auteurs

- Votre Nom - [@votre_twitter](https://twitter.com/votre_twitter)

## 🙏 Remerciements

- Architecture inspirée des principes Clean Architecture
- Domain-Driven Design (DDD)