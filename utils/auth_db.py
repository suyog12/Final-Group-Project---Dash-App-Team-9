from datetime import datetime
from hashlib import sha256
from typing import Optional
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

from .db import SessionLocal, User

class AuthError(Exception):
    pass

def _hash_username(username: str) -> str:
    return sha256((username or "").strip().lower().encode("utf-8")).hexdigest()

def create_user(username: str, password: str, dob_str: str) -> None:
    """Create user with hashed username + hashed password. dob_str: 'MM-DD-YYYY'."""
    if not SessionLocal:
        raise AuthError("Database not configured.")
    if not username or not password or not dob_str:
        raise AuthError("Username, password, and DOB are required.")
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
    except ValueError:
        raise AuthError("DOB must be MM-DD-YYYY.")

    with SessionLocal() as db:
        u = User(
            username_hash=_hash_username(username),
            password_hash=generate_password_hash(password),
            dob=dob,
        )
        db.add(u)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise AuthError("Account already exists.")

def verify_user(username: str, password: str) -> bool:
    if not SessionLocal:
        return False
    uname_h = _hash_username(username)
    with SessionLocal() as db:
        u = db.query(User).filter(User.username_hash == uname_h).first()
        return bool(u and check_password_hash(u.password_hash, password))

def get_profile(username: str) -> Optional[dict]:
    if not SessionLocal:
        return None
    uname_h = _hash_username(username)
    with SessionLocal() as db:
        u = db.query(User).filter(User.username_hash == uname_h).first()
        if not u:
            return None
        return {
            "username_hash": u.username_hash,
            "dob": u.dob.isoformat(),
            "created_at": u.created_at.isoformat(),
        }
