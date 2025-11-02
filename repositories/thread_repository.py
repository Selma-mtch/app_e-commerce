from ast import Dict, List
from typing import Optional

from models.support import MessageThread


class ThreadRepository:
    """
    Gère les fils de discussion du service client.
    """
    
    def __init__(self):
        self._by_id: Dict[str, MessageThread] = {}

    def add(self, thread: MessageThread):
        """Crée un nouveau fil de discussion."""
        self._by_id[thread.id] = thread

    def get(self, thread_id: str) -> Optional[MessageThread]:
        """Récupère un fil par son ID."""
        return self._by_id.get(thread_id)

    def list_by_user(self, user_id: str) -> list[MessageThread]:
        """Liste tous les fils d'un utilisateur."""
        return [t for t in self._by_id.values() if t.user_id == user_id]