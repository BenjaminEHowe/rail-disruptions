import xml.etree.ElementTree as ET
import logging
import re

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from datetime import timezone
from flask import Flask
from typing import Optional

from database import get_session
from database import select_incident_where_nr_id
from database import select_incident_version_where_incident_id_and_updated
from database import select_oldest_unparsed_raw_data
from model import Incident
from model import IncidentVersion


flask_app = Flask(__name__)
logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


@flask_app.route("/")
def status():
  oldest_unparsed_raw_data = select_oldest_unparsed_raw_data()
  if oldest_unparsed_raw_data is not None:
    oldest_unparsed_raw_data_id = oldest_unparsed_raw_data.id
    oldest_unparsed_raw_data_retrieved = oldest_unparsed_raw_data.retrieved
  else:
    oldest_unparsed_raw_data_id = None
    oldest_unparsed_raw_data_retrieved = None
  return {
    "oldest_unparsed_raw_data_id": oldest_unparsed_raw_data_id,
    "oldest_unparsed_raw_data_retrieved": oldest_unparsed_raw_data_retrieved,
  }


def get_affected_operators_str(element: ET.Element) -> str:
  operators_str = ""
  for operator_element in element:
    operators_str += operator_element.find("OperatorRef").text + ", "
  return operators_str[:-2]


def get_datetime_utc(element: ET.Element) -> Optional[datetime]:
  if element is None:
    return None
  return datetime.fromisoformat(element.text).astimezone(timezone.utc)


def get_datetime_utc_or_none(element: ET.Element) -> datetime | None:
  if element is None:
    return None
  return get_datetime_utc(element)


def get_text_or_none(element: ET.Element) -> str | None:
  if element is None:
    return None
  return element.text


def parse_incident(element: ET.Element) -> Incident:
  created_ts = get_datetime_utc(element.find("CreationTime"))
  return Incident(
    id=Incident.generate_id(created_ts),
    nr_id=element.find("IncidentNumber").text,
    planned=(element.find("Planned").text == "true"),
    cleared=(get_text_or_none(element.find("ClearedIncident")) == "true"),
    created_ts=created_ts,
    start_ts=get_datetime_utc_or_none(element.find("ValidityPeriod").find("StartTime")),
    end_ts=get_datetime_utc_or_none(element.find("ValidityPeriod").find("EndTime")),
    nr_link=element.find("InfoLinks")[0].find("Uri").text,
  )


def parse_incident_version(
    incident_id: str,
    element: ET.Element
) -> IncidentVersion:
  updated_ts = get_datetime_utc(element.find("ChangeHistory").find("LastChangedDate"))
  return IncidentVersion(
    id=IncidentVersion.generate_id(updated_ts),
    incident_id=incident_id,
    priority=int(element.find("IncidentPriority").text),
    summary=element.find("Summary").text,
    affected_operators=get_affected_operators_str(element.find("Affects").find("Operators")),
    description_html=element.find("Description").text,
    routes_html=element.find("Affects").find("RoutesAffected").text,
    updated_ts=updated_ts,
  )


def parse_oldest_data():
  oldest_unparsed_raw_data = select_oldest_unparsed_raw_data()
  if oldest_unparsed_raw_data is None:
    return

  logger.info(f"Parsing data {oldest_unparsed_raw_data.id}")
  xml_str = oldest_unparsed_raw_data.data
  xml_str = re.sub(' xmlns="[^"]+"', "", xml_str)
  xml_str = re.sub(' xmlns:com="[^"]+"', "", xml_str)
  xml_str = re.sub("<com:", "<", xml_str)
  xml_str = re.sub("</com:", "</", xml_str)
  xml_root = ET.fromstring(xml_str)
  for xml_incident in xml_root:
    current_incident = parse_incident(xml_incident)
    incident_id = current_incident.id
    with get_session() as session:
      existing_incident = select_incident_where_nr_id(current_incident.nr_id, session)
      if existing_incident is None:
        session.add(current_incident)
      else:
        incident_id = existing_incident.id
        if existing_incident.cleared != current_incident.cleared:
          existing_incident.cleared = current_incident.cleared
        if existing_incident.start_ts != current_incident.start_ts:
          existing_incident.start_ts = current_incident.start_ts
        if existing_incident.end_ts != current_incident.end_ts:
          existing_incident.end_ts = current_incident.end_ts

      # (maybe!) add new incident version
      incident_version = parse_incident_version(incident_id, xml_incident)
      if existing_incident is None:
        session.add(incident_version)
      else:
        existing_version = select_incident_version_where_incident_id_and_updated(incident_id, incident_version.id, session)
        if existing_version is None:
          session.add(incident_version)

      oldest_unparsed_raw_data.parsed = True
      session.add(oldest_unparsed_raw_data)

      session.commit()


logging.basicConfig(level=logging.INFO)
parse_oldest_data()
scheduler.start()
scheduler.add_job(parse_oldest_data, "interval", seconds=10)

if __name__ == "__main__":
  flask_app.run()
