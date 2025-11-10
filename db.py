import os 
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()
# get the database url from environment variable or use default sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///vizion.db")

# database engine - main connection to the database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
                       )

# session factory - creates new sessions for interacting with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# base class for declarative models
Base = declarative_base()

# Helper function to get a new database session
def get_session():
    return SessionLocal()