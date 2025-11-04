from dataclasses import dataclass
from flask_login import UserMixin

@dataclass
class User(UserMixin):
    """
    Représente un utilisateur de la plateforme.
    
    Attributes:
        id: Identifiant unique
        email: Adresse email (utilisée pour la connexion)
        password_hash: Hash du mot de passe
        first_name: Prénom
        last_name: Nom
        address: Adresse de livraison
        is_admin: Indique si l'utilisateur a des droits d'administration
    """
    id: str
    email: str
    password_hash: str
    first_name: str
    last_name: str
    address: str
    is_admin: bool = False

    def update_profile(self, **fields):
        """
        Met à jour les champs du profil utilisateur.
        
        Args:
            **fields: Champs à mettre à jour (first_name, last_name, address)
        
        Note:
            Les champs id, email, is_admin et password_hash ne peuvent pas être modifiés
        """
        for k, v in fields.items():
            if hasattr(self, k) and k not in {"id", "email", "is_admin", "password_hash"}:
                setattr(self, k, v)

    # UserMixin fournit déjà get_id(); si besoin de surcharger :
    # def get_id(self) -> str:
    #     return str(self.id)
