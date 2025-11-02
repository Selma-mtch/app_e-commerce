from ast import Dict
from typing import Optional
import uuid


class SessionManager:
    """
    Gère les sessions utilisateur en mémoire.
    
    En production, utiliser Redis ou une solution similaire.
    """
    
    def __init__(self):
        self._sessions: Dict[str, str] = {}  # token -> user_id

    def create_session(self, user_id: str) -> str:
        """
        Crée une nouvelle session pour un utilisateur.
        
        Returns:
            Token de session
        """
        token = str(uuid.uuid4())
        self._sessions[token] = user_id
        return token

    def destroy_session(self, token: str):
        """Détruit une session existante."""
        self._sessions.pop(token, None)

    def get_user_id(self, token: str) -> Optional[str]:
        """Récupère l'ID utilisateur associé à un token."""
        return self._sessions.get(token)
