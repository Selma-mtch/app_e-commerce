"""Script de lancement de l'application web."""

from web import create_app

app = create_app('development')
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🛒 E-COMMERCE - APPLICATION WEB")
    print("="*60)
    print("\n📍 URLs disponibles:")
    print("   - Page d'accueil:    http://127.0.0.1:5000/")
    print("   - Catalogue:         http://127.0.0.1:5000/catalog/products")
    print("   - Connexion:         http://127.0.0.1:5000/auth/login")
    print("   - Inscription:       http://127.0.0.1:5000/auth/register")
    print("   - Admin (démo):      admin@shop.local / admin")
    print("\n" + "="*60 + "\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True)