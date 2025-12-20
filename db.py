import os 
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Try to get DATABASE_URL from Streamlit secrets first, then environment variable
try:
    DATABASE_URL = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", "sqlite:///vizion.db"))
except:
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