from datetime import datetime
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql.functions import now
from typing import Optional
from ulid import ULID


def generate_id(
  prefix: Optional[str],
):
  identifier = str(ULID())
  if prefix:
    return f"{prefix}_{identifier}"
  else:
    return identifier


class Base(DeclarativeBase):
  pass


class RawData(Base):
  __tablename__ = 'raw_data'

  id: Mapped[str] = mapped_column(String(30), primary_key=True, default=lambda:generate_id("raw"))
  retrieved: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = now())
  hash: Mapped[str] = mapped_column(String(64))
  parsed: Mapped[bool] = mapped_column(Boolean, default=False)
  data: Mapped[str] = mapped_column(String(67108864).with_variant(LONGTEXT, "mysql", "mariadb"))
