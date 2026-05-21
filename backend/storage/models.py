from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Float,
)

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TaskRecord(Base):

    __tablename__ = "tasks"

    id = Column(
        Integer, primary_key=True
    )

    task_id = Column(
        String, unique=True
    )

    objective = Column(Text)

    status = Column(String)

    result = Column(Text, nullable=True)

    duration = Column(Float, nullable=True)

    retry_count = Column(
        Integer, default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class WorkflowRecord(Base):

    __tablename__ = "workflows"

    id = Column(
        Integer, primary_key=True
    )

    workflow_id = Column(
        String, unique=True
    )

    objective = Column(Text)

    status = Column(String)

    total_tasks = Column(Integer)

    completed_tasks = Column(Integer)

    token_usage = Column(
        Integer, default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class TokenUsage(Base):

    __tablename__ = "token_usage"

    id = Column(
        Integer, primary_key=True
    )

    task_id = Column(String)

    agent = Column(String)

    prompt_tokens = Column(Integer)

    completion_tokens = Column(Integer)

    total_tokens = Column(Integer)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class LogRecord(Base):

    __tablename__ = "logs"

    id = Column(
        Integer, primary_key=True
    )

    message = Column(Text)

    level = Column(
        String, default="INFO"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


class MemoryRecord(Base):

    __tablename__ = "memories"

    id = Column(
        Integer, primary_key=True
    )

    content = Column(
        Text, nullable=False
    )

    source = Column(
        Text, default="agent"
    )

    memory_type = Column(
        Text, default="general"
    )

    embedding_ready = Column(
        Integer, default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
