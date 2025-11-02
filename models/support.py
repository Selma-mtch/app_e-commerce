from ast import List
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Message:
    """
    Message dans un fil de discussion du service client.
    
    Attributes:
        id: Identifiant unique du message
        thread_id: Référence du fil de discussion
        author_user_id: ID de l'auteur (None = agent support)
        body: Contenu du message
        created_at: Timestamp de création
    """
    id: str
    thread_id: str
    author_user_id: Optional[str]
    body: str
    created_at: float


@dataclass
class MessageThread:
    """
    Fil de discussion avec le service client.
    
    Attributes:
        id: Identifiant unique du fil
        user_id: Référence de l'utilisateur
        order_id: Référence de la commande concernée (optionnel)
        subject: Sujet de la discussion
        messages: Liste des messages
        closed: Indique si le fil est fermé
    """
    id: str
    user_id: str
    order_id: Optional[str]
    subject: str
    messages: list[Message] = field(default_factory=list)
    closed: bool = False
