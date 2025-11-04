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

    # --- Nouvelles fonctionnalités de profil ---
    def change_email(self, user_id: str, current_password: str, new_email: str) -> User:
        """Change l'adresse email de l'utilisateur après vérification du mot de passe.

        Raises:
            ValueError: si l'utilisateur est introuvable, mot de passe invalide,
                       ou email déjà utilisé.
        """
        user = self.users.get(user_id)
        if not user:
            raise ValueError("Utilisateur introuvable.")

        if not PasswordHasher.verify(current_password, user.password_hash):
            raise ValueError("Mot de passe actuel invalide.")

        new_email_norm = (new_email or "").strip()
        if not new_email_norm:
            raise ValueError("Nouvel email requis.")

        other = self.users.get_by_email(new_email_norm)
        if other and other.id != user.id:
            raise ValueError("Email déjà utilisé.")

        if hasattr(self.users, 'update_email'):
            self.users.update_email(user.id, new_email_norm)
            updated = self.users.get(user.id)
        else:
            user.email = new_email_norm
            self.users.add(user)
            updated = user
        return updated

    def change_password(self, user_id: str, current_password: str, new_password: str) -> None:
        """Change le mot de passe de l'utilisateur.

        Raises:
            ValueError: si l'utilisateur est introuvable, si le mot de passe actuel est invalide,
                       ou si le nouveau mot de passe ne respecte pas les contraintes minimales.
        """
        user = self.users.get(user_id)
        if not user:
            raise ValueError("Utilisateur introuvable.")

        if not PasswordHasher.verify(current_password, user.password_hash):
            raise ValueError("Mot de passe actuel invalide.")

        if not new_password or len(new_password) < 8:
            raise ValueError("Le nouveau mot de passe doit contenir au moins 8 caractères.")

        new_hash = PasswordHasher.hash(new_password)
        if hasattr(self.users, 'update_password'):
            self.users.update_password(user.id, new_hash)
        else:
            user.password_hash = new_hash
            self.users.add(user)
