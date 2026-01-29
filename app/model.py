from datetime import datetime
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.dialects.mysql import TEXT
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.functions import now
from typing import Optional
from ulid import ULID


def generate_id(
  prefix: Optional[str],
  ts: datetime,
):
  identifier = str(ULID.from_datetime(ts))
  if prefix:
    return f"{prefix}_{identifier}"
  else:
    return identifier


class Base(DeclarativeBase):
  pass


class Incident(Base):
  __tablename__ = "incident"

  @staticmethod
  def generate_id(ts: datetime) -> str:
    return generate_id("inc", ts)

  id: Mapped[str] = mapped_column(String(len("inc_") + 26), primary_key=True)
  nr_id: Mapped[str] = mapped_column(String(32), index=True)
  planned: Mapped[bool]
  cleared: Mapped[bool]
  created_ts: Mapped[datetime]
  start_ts: Mapped[datetime]
  end_ts: Mapped[datetime | None]
  nr_link: Mapped[str] = mapped_column(String(2048))

  def __repr__(self) -> str:
    return f"Incident(id={self.id!r}, nr_id={self.nr_id!r}, nr_link={self.nr_link!r})"


class IncidentVersion(Base):
  __tablename__ = "incident_version"

  @staticmethod
  def generate_id(ts: datetime) -> str:
    return generate_id("incv", ts)

  id: Mapped[str] = mapped_column(String(len("incv_") + 26), primary_key=True)
  incident_id: Mapped[str] = mapped_column(String(len("inc_") + 26), index=True)
  priority: Mapped[int]
  summary: Mapped[str] = mapped_column(String(2048))
  affected_operators: Mapped[str] = mapped_column(String(255))
  description_html: Mapped[str] = mapped_column(String(65536).with_variant(TEXT, "mysql", "mariadb"))
  routes_html: Mapped[str] = mapped_column(String(2048))
  updated_ts: Mapped[datetime]

  def __repr__(self) -> str:
    return f"IncidentVersion(id={self.id!r})"


class RawData(Base):
  __tablename__ = 'raw_data'

  id: Mapped[str] = mapped_column(String(30), primary_key=True, default=lambda:generate_id("raw", datetime.now()))
  retrieved: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, server_default=now())
  hash: Mapped[str] = mapped_column(String(64))
  parsed: Mapped[bool] = mapped_column(Boolean, default=False)
  data: Mapped[str] = mapped_column(String(67108864).with_variant(LONGTEXT, "mysql", "mariadb"))

  def __repr__(self) -> str:
    return f"RawData(id={self.id!r})"
