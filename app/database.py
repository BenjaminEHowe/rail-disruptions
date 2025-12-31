import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Optional

from model import Base
from model import RawData


connection_string = os.environ.get("SQLALCHEMY_CONNECTION_STRING") or "sqlite:///sqlite.db"
engine = create_engine(connection_string)
Base.metadata.create_all(engine)


def insert_raw_data(raw_data: RawData):
  with Session(engine) as session:
    session.add(raw_data)
    session.commit()


def select_latest_raw_data() -> Optional[RawData]:
  with Session(engine) as session:
    return session.query(RawData).order_by(RawData.id.desc()).first()
