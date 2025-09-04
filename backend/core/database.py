from supabase import create_client, Client
from core.config import settings

# For MVP, we're using Supabase only, not SQLAlchemy
# Uncomment below if you need SQLAlchemy later:
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# engine = create_engine(settings.database_url)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

def get_database():
    """Legacy function for SQLAlchemy - not used in MVP"""
    raise NotImplementedError("Using Supabase instead of SQLAlchemy")

def get_supabase() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_key)