from sqlalchemy import (
    Column, String, Integer, Float,
    Text, DateTime, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

DATABASE_URL = "sqlite:///omniresearch.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


class TaskRecord(Base):
    __tablename__ = "tasks"
    id = Column(
        Integer, primary_key=True,
        autoincrement=True
    )
    task_id = Column(String, unique=True)
    task_type = Column(String)
    status = Column(String)
    retries = Column(Integer, default=0)
    duration = Column(Float, nullable=True)
    output = Column(Text, nullable=True)
    created_at = Column(
        DateTime, default=datetime.now
    )


class WorkflowRecord(Base):
    __tablename__ = "workflows"
    id = Column(
        Integer, primary_key=True,
        autoincrement=True
    )
    workflow_id = Column(String, unique=True)
    status = Column(String)
    total_tasks = Column(Integer)
    completed_tasks = Column(Integer)
    token_usage = Column(Integer, default=0)
    created_at = Column(
        DateTime, default=datetime.now
    )


class LogRecord(Base):
    __tablename__ = "logs"
    id = Column(
        Integer, primary_key=True,
        autoincrement=True
    )
    message = Column(Text)
    level = Column(String, default="INFO")
    created_at = Column(
        DateTime, default=datetime.now
    )


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
