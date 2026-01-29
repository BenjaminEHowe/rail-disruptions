import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Optional

from model import Base
from model import Incident
from model import IncidentVersion
from model import RawData


connection_string = os.environ.get("SQLALCHEMY_CONNECTION_STRING") or "sqlite:///sqlite.db"
engine = create_engine(connection_string)
Base.metadata.create_all(engine)


def get_session():
  return Session(engine)


def insert_raw_data(raw_data: RawData):
  with Session(engine) as session:
    session.add(raw_data)
    session.commit()


def select_incident_where_nr_id(nr_id: str, session: Session = get_session()) -> Optional[Incident]:
  with session:
    return session.query(Incident).where(Incident.nr_id == nr_id).first()


def select_incident_version_where_incident_id_and_updated(incident_id: str, incident_version_id: str, session: Session = get_session()) -> Optional[IncidentVersion]:
  incident_version_id_prefix, incident_version_ulid = incident_version_id.split("_")
  incident_version_id_like = incident_version_id_prefix + "_" + incident_version_ulid[:10] + "%"
  with (session):
    return session.query(IncidentVersion).where(IncidentVersion.incident_id == incident_id).filter(IncidentVersion.id.like(incident_version_id_like)).first()


def select_latest_raw_data() -> Optional[RawData]:
  with Session(engine) as session:
    return session.query(RawData).order_by(RawData.retrieved.desc()).first()


def select_oldest_unparsed_raw_data() -> Optional[RawData]:
  with Session(engine) as session:
    return session.query(RawData).where(RawData.parsed == False).order_by(RawData.retrieved.asc()).first()
