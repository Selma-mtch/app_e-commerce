from typing import Dict, List, Optional

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

    # Optionnel: support d'ajout de message pour compat DB
    def add_message(self, thread_id: str, message):
        th = self._by_id.get(thread_id)
        if th:
            th.messages.append(message)

    def list_all(self) -> list[MessageThread]:
        """Liste tous les tickets."""
        return list(self._by_id.values())
