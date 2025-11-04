from typing import Dict, Optional
from services.auth.password_hasher import PasswordHasher

from models.user import User

USERS = [
    User(id="1", email="admin@example.com", password_hash=PasswordHasher.hash("hash123"), first_name="Admin", last_name="Root", address="Paris", is_admin=True),
    User(id="2", email="user@example.com", password_hash=PasswordHasher.hash("hash456"), first_name="Jean", last_name="Dupont", address="Lyon"),
]

class UserRepository:
    """
    Gère le stockage et la récupération des utilisateurs.
    
    Implémentation en mémoire avec indexation par ID et email.
    """
    
    def __init__(self):
        self._by_id: Dict[str, User] = {}
        self._by_email: Dict[str, User] = {}
        for user in USERS:
            self.add(user)

    def add(self, user: User):
        """Ajoute un utilisateur au repository."""
        self._by_id[user.id] = user
        self._by_email[user.email.lower()] = user

    def get(self, user_id: str) -> Optional[User]:
        """Récupère un utilisateur par son ID."""
        return self._by_id.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par son email."""
        return self._by_email.get(email.lower())
