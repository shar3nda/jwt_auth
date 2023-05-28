from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

SQLALCHEMY_DATABASE_URL = (
    "postgresql+psycopg://db_user:VerySecureUserPassword@localhost/restaurant"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(engine, autocommit=False, autoflush=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
