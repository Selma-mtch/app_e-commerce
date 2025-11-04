from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from models.user import User
from models.db_models import UserDB


class UserRepositoryDB:
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def add(self, user: User):
        with self._session_factory() as s:
            row = s.get(UserDB, user.id)
            if row:
                row.email = user.email
                row.password_hash = user.password_hash
                row.first_name = user.first_name
                row.last_name = user.last_name
                row.address = user.address
                row.is_admin = user.is_admin
            else:
                s.add(UserDB(
                    id=user.id,
                    email=user.email,
                    password_hash=user.password_hash,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    address=user.address,
                    is_admin=user.is_admin
                ))
            s.commit()

    def get(self, user_id: str) -> Optional[User]:
        with self._session_factory() as s:
            r = s.get(UserDB, user_id)
            if not r:
                return None
            return User(
                id=r.id,
                email=r.email,
                password_hash=r.password_hash,
                first_name=r.first_name,
                last_name=r.last_name,
                address=r.address,
                is_admin=r.is_admin,
            )

    def get_by_email(self, email: str) -> Optional[User]:
        with self._session_factory() as s:
            r = s.scalars(select(UserDB).where(UserDB.email == email)).first()
            if not r:
                return None
            return User(
                id=r.id,
                email=r.email,
                password_hash=r.password_hash,
                first_name=r.first_name,
                last_name=r.last_name,
                address=r.address,
                is_admin=r.is_admin,
            )

    # --- Mises à jour spécifiques ---
    def update_email(self, user_id: str, new_email: str) -> None:
        with self._session_factory() as s:
            row = s.get(UserDB, user_id)
            if not row:
                return
            row.email = new_email
            s.commit()

    def update_password(self, user_id: str, new_hash: str) -> None:
        with self._session_factory() as s:
            row = s.get(UserDB, user_id)
            if not row:
                return
            row.password_hash = new_hash
            s.commit()

    def list_all(self) -> list[User]:
        with self._session_factory() as s:
            rows = s.scalars(select(UserDB)).all()
            return [
                User(
                    id=r.id,
                    email=r.email,
                    password_hash=r.password_hash,
                    first_name=r.first_name,
                    last_name=r.last_name,
                    address=r.address,
                    is_admin=r.is_admin,
                )
                for r in rows
            ]
