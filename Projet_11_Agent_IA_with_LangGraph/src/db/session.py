from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import DATABASE_URL
from src.db.models import Base

# Le moteur SQLAlchemy utilise maintenant DATABASE_URL défini dans src/config.py (pointant vers /tmp/)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Crée les tables en BDD au démarrage."""
    Base.metadata.create_all(bind=engine)