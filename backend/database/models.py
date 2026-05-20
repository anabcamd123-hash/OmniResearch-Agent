from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TaskRecord(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, unique=True)
    status = Column(String)
    retries = Column(Integer, default=0)
