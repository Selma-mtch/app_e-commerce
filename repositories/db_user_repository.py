from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from models.user import User
from models.db_models import UserDB, AddressDB
from web.utils.address import parse_address_fields, build_address_string


class UserRepositoryDB:
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory

    def add(self, user: User):
        with self._session_factory() as s:
            addr_id = self._upsert_address(s, user)
            row = s.get(UserDB, user.id)
            if row:
                row.email = user.email
                row.password_hash = user.password_hash
                row.first_name = user.first_name
                row.last_name = user.last_name
                row.address_id = addr_id
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
                    address_id=addr_id,
                    is_admin=user.is_admin
                ))
            s.commit()

    def get(self, user_id: str) -> Optional[User]:
        with self._session_factory() as s:
            r = s.get(UserDB, user_id)
            if not r:
                return None
            addr = s.get(AddressDB, r.address_id) if r.address_id else None
            address_str = self._address_to_string(addr, legacy=r.address)
            return User(
                id=r.id,
                email=r.email,
                password_hash=r.password_hash,
                first_name=r.first_name,
                last_name=r.last_name,
                address=address_str,
                address_id=r.address_id,
                is_admin=r.is_admin,
            )

    def get_by_email(self, email: str) -> Optional[User]:
        with self._session_factory() as s:
            r = s.scalars(select(UserDB).where(UserDB.email == email)).first()
            if not r:
                return None
            addr = s.get(AddressDB, r.address_id) if r.address_id else None
            address_str = self._address_to_string(addr, legacy=r.address)
            return User(
                id=r.id,
                email=r.email,
                password_hash=r.password_hash,
                first_name=r.first_name,
                last_name=r.last_name,
                address=address_str,
                address_id=r.address_id,
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
            result = []
            for r in rows:
                addr = s.get(AddressDB, r.address_id) if r.address_id else None
                address_str = self._address_to_string(addr, legacy=r.address)
                result.append(User(
                    id=r.id,
                    email=r.email,
                    password_hash=r.password_hash,
                    first_name=r.first_name,
                    last_name=r.last_name,
                    address=address_str,
                    address_id=r.address_id,
                    is_admin=r.is_admin,
                ))
            return result

    # --- Helpers ---
    def _upsert_address(self, session, user: User) -> str | None:
        """Crée ou met à jour l'adresse liée à l'utilisateur, retourne l'id."""
        if not user.address:
            return None
        fields = parse_address_fields(user.address)
        address_id = user.address_id or user.id
        row = session.get(AddressDB, address_id)
        if row:
            row.street = fields["street"]
            row.line2 = fields["line2"] or None
            row.postal_code = fields["postal_code"]
            row.city = fields["city"]
            row.country = fields["country"] or "France"
        else:
            session.add(AddressDB(
                id=address_id,
                street=fields["street"],
                line2=fields["line2"] or None,
                postal_code=fields["postal_code"],
                city=fields["city"],
                country=fields["country"] or "France",
            ))
        return address_id

    def _address_to_string(self, addr: AddressDB | None, legacy: str | None = None) -> str:
        if addr:
            return build_address_string(
                addr.street,
                addr.line2 or "",
                addr.postal_code,
                addr.city,
                addr.country or "France",
            )
        return legacy or ""
