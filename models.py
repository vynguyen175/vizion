from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text

from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base


# USER TABLE
class User(Base):
    __tablename__ = "users"

    # Columns
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    datasets = relationship("Dataset", back_populates="owner")


# DATASET TABLE
class Dataset(Base):
    __tablename__ = "datasets"

    # Columns
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False) 
    storage_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    row_count= Column(Integer)
    column_count= Column(Integer)
    status = Column(String, default="Uploaded")  
    # Keeps track of the file's progress (e.g. "Uploaded", "Analyzed", "Cleaned")

    # Relationships
    owner = relationship("User", back_populates="datasets")