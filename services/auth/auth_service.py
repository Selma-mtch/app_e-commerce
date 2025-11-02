import uuid
from models.user import User
from services.auth.password_hasher import PasswordHasher
from services.auth.session_manager import SessionManager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from repositories.user_repository import UserRepository

class AuthService:
    """
    Service d'authentification et d'inscription.
    """
    
    def __init__(self, users: 'UserRepository', sessions: SessionManager):
        self.users = users
        self.sessions = sessions

    def register(self, email: str, password: str, first_name: str, 
                 last_name: str, address: str, is_admin: bool = False) -> User:
        """
        Inscrit un nouvel utilisateur.
        
        Args:
            email: Adresse email
            password: Mot de passe en clair
            first_name: Prénom
            last_name: Nom
            address: Adresse de livraison
            is_admin: Droits d'administration
            
        Returns:
            L'utilisateur créé
            
        Raises:
            ValueError: Si l'email est déjà utilisé
        """
        if self.users.get_by_email(email):
            raise ValueError("Email déjà utilisé.")
        
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=PasswordHasher.hash(password),
            first_name=first_name,
            last_name=last_name,
            address=address,
            is_admin=is_admin
        )
        self.users.add(user)
        return user

    def login(self, email: str, password: str) -> str:
        """
        Authentifie un utilisateur.
        
        Args:
            email: Adresse email
            password: Mot de passe
            
        Returns:
            Token de session
            
        Raises:
            ValueError: Si les identifiants sont invalides
        """
        user = self.users.get_by_email(email)
        if not user or not PasswordHasher.verify(password, user.password_hash):
            raise ValueError("Identifiants invalides.")
        return self.sessions.create_session(user.id)

    def logout(self, token: str):
        """Déconnecte un utilisateur."""
        self.sessions.destroy_session(token)
