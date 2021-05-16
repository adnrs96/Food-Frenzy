from app_frenzy.config import get_app_frenzy_settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


settings = get_app_frenzy_settings()

engine = create_engine(settings.DATABASE_CONN_STR, echo=settings.DEBUG)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, future=True
)

AppFrenzyBase = declarative_base()
