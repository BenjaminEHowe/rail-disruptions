from dataclasses import dataclass
from enum import StrEnum


class IncidentStatus(StrEnum):
  ACTIVE = "Active"
  CLEARED = "Cleared"

@dataclass(frozen=True)
class TrainOperatingCompany:
  """A Train Operating Company."""
  code: str
  name: str

@dataclass(frozen=True)
class Incident:
  """An incident with helpful details."""
  id: str
  version: str
  summary: str
  description: str
  status: IncidentStatus
  affectedOperators: list[TrainOperatingCompany]

@dataclass(frozen=True)
class IncidentWithoutDetails:
  """An incident without any details -- use the ID to retrieve the details."""
  id: str
  url: str

@dataclass(frozen=True)
class TocServiceIndicator:
  """A Service Indicator for a Train Operating Company."""
  operator: TrainOperatingCompany
  status: str
  incidents: list[IncidentWithoutDetails]
