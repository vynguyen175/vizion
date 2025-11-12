from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text

from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base


# USER TABLE
class User(Base):
    __tablename__ = "users"
    analyses = relationship("AnalysisHistory", back_populates="user", cascade="all, delete-orphan")
    
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
    analyses = relationship("AnalysisHistory", back_populates="dataset", cascade="all, delete-orphan")

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


class AnalysisHistory(Base):
    # Stores analysis results for each dataset
    # Links to the Dataset table through dataset_id.
    __tablename__="analysis_history"

    id=Column(String, primary_key=True)
    dataset_id = Column(String, ForeignKey("datasets.id"))
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    summary = Column(Text, nullable=True)  # JSON or text summary of analysis results
    insights = Column(Text, nullable=True)  # JSON or text insights derived from analysis

    # Relationships
    dataset = relationship("Dataset", back_populates="analyses")
    user = relationship("User", back_populates="analyses")