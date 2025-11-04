from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from models.support import MessageThread, Message
from models.db_models import ThreadDB, MessageDB


class ThreadRepositoryDB:
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def add(self, thread: MessageThread):
        with self._session_factory.begin() as s:
            s.add(ThreadDB(
                id=thread.id,
                user_id=thread.user_id,
                order_id=thread.order_id,
                subject=thread.subject,
                closed=thread.closed,
            ))

    def get(self, thread_id: str) -> Optional[MessageThread]:
        with self._session_factory() as s:
            t = s.get(ThreadDB, thread_id)
            if not t:
                return None
            msgs = s.scalars(select(MessageDB).where(MessageDB.thread_id == thread_id).order_by(MessageDB.created_at.asc())).all()
            return MessageThread(
                id=t.id,
                user_id=t.user_id,
                order_id=t.order_id,
                subject=t.subject,
                messages=[Message(id=m.id, thread_id=m.thread_id, author_user_id=m.author_user_id, body=m.body, created_at=m.created_at) for m in msgs],
                closed=t.closed,
            )

    def list_by_user(self, user_id: str) -> list[MessageThread]:
        with self._session_factory() as s:
            rows = s.scalars(select(ThreadDB).where(ThreadDB.user_id == user_id)).all()
            return [MessageThread(id=t.id, user_id=t.user_id, order_id=t.order_id, subject=t.subject, messages=[], closed=t.closed) for t in rows]

    def add_message(self, thread_id: str, message: Message):
        with self._session_factory.begin() as s:
            s.add(MessageDB(
                id=message.id,
                thread_id=thread_id,
                author_user_id=message.author_user_id,
                body=message.body,
                created_at=message.created_at,
            ))

    def close(self, thread_id: str):
        with self._session_factory.begin() as s:
            t = s.get(ThreadDB, thread_id)
            if t:
                t.closed = True

    def list_all(self) -> list[MessageThread]:
        with self._session_factory() as s:
            rows = s.scalars(select(ThreadDB)).all()
            return [MessageThread(id=t.id, user_id=t.user_id, order_id=t.order_id, subject=t.subject, messages=[], closed=t.closed) for t in rows]
