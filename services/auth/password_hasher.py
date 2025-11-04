import bcrypt


class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    @staticmethod
    def verify(password: str, stored_hash: str) -> bool:
        if stored_hash.startswith("sha256::"):
            try:
                return f"sha256::{hash(password)}" == stored_hash
            except Exception:
                return False
        try:
            return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
        except Exception:
            return False
