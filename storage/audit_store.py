# audit_store.py - Audit logging (SQLite / persistent store) 
# storage/audit_store.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import os, json
import datetime

Base = declarative_base()

class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True)
    ts = Column(String, default=lambda: datetime.datetime.utcnow().isoformat())
    input_hash = Column(String, index=True)
    payload = Column(JSON)

class AuditStore:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(db_url, echo=False, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def log(self, record: dict) -> int:
        session = self.Session()
        a = Audit(input_hash=record.get("input_hash"), payload=record)
        session.add(a)
        session.commit()
        id_ = a.id
        session.close()
        return id_