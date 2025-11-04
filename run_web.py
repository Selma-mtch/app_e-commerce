"""Script de lancement de l'application web.

Ce module expose ``app`` pour les serveurs WSGI (gunicorn) et permet
un lancement en local via ``python run_web.py``.
"""

import os
from web import create_app


# Choix de la config via variable d'environnement (production/development/testing)
CONFIG_NAME = os.getenv('APP_CONFIG', 'development')
app = create_app(CONFIG_NAME)


if __name__ == '__main__':
    # Détecter le port d'environnement (Render/Heroku: $PORT)
    port = int(os.getenv('PORT', '5000'))
    # Écoute publique en environnement conteneurisé, sinon local uniquement
    host = os.getenv('HOST', '0.0.0.0' if os.getenv('PORT') else '127.0.0.1')
    debug = os.getenv('FLASK_DEBUG', '1' if CONFIG_NAME != 'production' else '0') == '1'

    print("\n" + "="*60)
    print("🛒 E-COMMERCE - APPLICATION WEB")
    print("="*60)
    print(f"\nConfig: {CONFIG_NAME} | Host: {host} | Port: {port} | Debug: {debug}")
    print("\n📍 URLs disponibles:")
    print(f"   - Page d'accueil:    http://{host}:{port}/")
    print(f"   - Catalogue:         http://{host}:{port}/catalog/products")
    print(f"   - Connexion:         http://{host}:{port}/auth/login")
    print(f"   - Inscription:       http://{host}:{port}/auth/register")
    print("\n" + "="*60 + "\n")

    app.run(host=host, port=port, debug=debug)
