from __future__ import annotations
from typing import Optional
import uuid
import time

from models.support import MessageThread, Message

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from repositories.thread_repository import ThreadRepository
    from repositories.user_repository import UserRepository

class CustomerService:
    """
    Service client : gestion des fils de discussion et messages.
    
    Permet aux utilisateurs de contacter le support et aux agents
    de répondre aux demandes.
    
    Attributes:
        threads: Repository des fils de discussion
        users: Repository des utilisateurs
    """
    
    def __init__(self, threads: ThreadRepository, users: UserRepository):
        """
        Initialise le service client.
        
        Args:
            threads: Repository pour stocker les fils de discussion
            users: Repository pour valider les utilisateurs
        """
        self.threads = threads
        self.users = users

    def open_thread(self, user_id: str, subject: str, 
                    order_id: Optional[str] = None) -> MessageThread:
        """
        Ouvre un nouveau fil de discussion.
        
        Args:
            user_id: ID de l'utilisateur qui crée le fil
            subject: Sujet de la discussion
            order_id: ID de la commande concernée (optionnel)
            
        Returns:
            Le fil de discussion créé
            
        Raises:
            ValueError: Si l'utilisateur n'existe pas
            
        Example:
            >>> thread = cs.open_thread(user_id, "Problème de livraison", order_id)
        """
        user = self.users.get(user_id)
        if not user:
            raise ValueError("Utilisateur introuvable.")
        
        thread = MessageThread(
            id=str(uuid.uuid4()),
            user_id=user_id,
            order_id=order_id,
            subject=subject
        )
        self.threads.add(thread)
        return thread

    def post_message(self, thread_id: str, author_user_id: Optional[str], 
                     body: str) -> Message:
        """
        Poste un message dans un fil de discussion.
        
        Args:
            thread_id: ID du fil de discussion
            author_user_id: ID de l'auteur (None = agent support)
            body: Contenu du message
            
        Returns:
            Le message créé
            
        Raises:
            ValueError: Si le fil est introuvable, fermé ou l'auteur invalide
            
        Example:
            >>> # Message d'un client
            >>> msg = cs.post_message(thread_id, user_id, "J'ai un problème...")
            >>> # Réponse d'un agent support
            >>> response = cs.post_message(thread_id, None, "Nous allons vous aider")
        """
        thread = self.threads.get(thread_id)
        if not thread:
            raise ValueError("Fil de discussion introuvable.")
        if thread.closed:
            raise ValueError("Le fil de discussion est fermé.")
        
        # Vérifier que l'auteur existe (si ce n'est pas un agent support)
        if author_user_id is not None:
            author = self.users.get(author_user_id)
            if not author:
                raise ValueError("Auteur inconnu.")
        
        message = Message(
            id=str(uuid.uuid4()),
            thread_id=thread_id,
            author_user_id=author_user_id,
            body=body,
            created_at=time.time()
        )
        thread.messages.append(message)
        return message

    def close_thread(self, thread_id: str, admin_user_id: str) -> MessageThread:
        """
        Ferme un fil de discussion (réservé aux administrateurs).

        Args:
            thread_id: ID du fil à fermer
            admin_user_id: ID de l'administrateur
            
        Returns:
            Le fil de discussion fermé
            
        Raises:
            PermissionError: Si l'utilisateur n'est pas administrateur
            ValueError: Si le fil est introuvable
            
        Example:
            >>> thread = cs.close_thread(thread_id, admin_id)
        """
        admin = self.users.get(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants.")

        thread = self.threads.get(thread_id)
        if not thread:
            raise ValueError("Fil de discussion introuvable.")

        thread.closed = True
        return thread

    def list_user_threads(self, user_id: str) -> list[MessageThread]:
        """
        Liste tous les fils de discussion d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des fils de discussion
            
        Example:
            >>> threads = cs.list_user_threads(user_id)
            >>> for thread in threads:
            ...     print(f"{thread.subject}: {len(thread.messages)} messages")
        """
        return self.threads.list_by_user(user_id)

    def get_thread(self, thread_id: str) -> Optional[MessageThread]:
        """
        Récupère un fil de discussion par son ID.

        Args:
            thread_id: ID du fil
            
        Returns:
            Le fil de discussion ou None
        """
        return self.threads.get(thread_id)