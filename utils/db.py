import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    print("[auth] WARNING: DATABASE_URL is not set. Auth will not work.")

# TLS for Aiven MySQL (PyMySQL)
ssl_args = {}
ca_path = os.getenv("MYSQL_CA_CERT")  # optional: pin to a CA cert file
if ca_path:
    # use a specific CA bundle (recommended if you want explicit verification)
    ssl_args = {"ca": ca_path}
# If no MYSQL_CA_CERT provided, PyMySQL will use system trust store.

connect_args = {"ssl": ssl_args} if DATABASE_URL.startswith("mysql+pymysql://") else {}

engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    echo=False,
    connect_args=connect_args
) if DATABASE_URL else None

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True) if engine else None
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username_hash = Column(String(64), nullable=False)      # sha256 hex (64 chars)
    password_hash = Column(String(255), nullable=False)     # PBKDF2 string (Werkzeug)
    dob = Column(Date, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("username_hash", name="uq_users_username_hash"),)

def init_db():
    if not engine:
        raise RuntimeError("DATABASE_URL not configured.")
    Base.metadata.create_all(bind=engine)
