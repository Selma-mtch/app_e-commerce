class PasswordHasher:
    """
    Utilitaire de hachage de mots de passe.
    
    Note: Implémentation simplifiée pour la démo.
          En production, utiliser bcrypt, argon2 ou scrypt.
    """
    
    @staticmethod
    def hash(password: str) -> str:
        """Hache un mot de passe."""
        return f"sha256::{hash(password)}"

    @staticmethod
    def verify(password: str, stored_hash: str) -> bool:
        """Vérifie qu'un mot de passe correspond au hash."""
        return PasswordHasher.hash(password) == stored_hash
