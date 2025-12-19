import logging
import re
import requests
import xml.etree.ElementTree as ET

from datetime import datetime
from zoneinfo import ZoneInfo

from ..common import model


TIMEZONE = ZoneInfo("Europe/London")
USER_AGENT = "uk.beh.rail-disruptions/0.2.0"

logger = logging.getLogger(__name__)


class NRDisruptionsClient():
  """Client for the National Rail Disruptions API."""


  def __init__(self, base_url: str):
    self.base_url = base_url


  def get_toc_service_indicators(self) -> list[model.TocServiceIndicator]:
    """Get service indicators for Train Operating Companies."""
    xml_str = requests.get(f"{self.base_url}/service-indicators.xml", headers={"user-agent": USER_AGENT}).text
    xml_str = re.sub(' xmlns="[^"]+"', "", xml_str)
    xml_root = ET.fromstring(xml_str)
    indicators = []
    for toc_xml in xml_root:
      incidents = []
      for incident_xml in toc_xml.findall("ServiceGroup"):
        incidents.append(model.IncidentWithoutDetails(
          id=incident_xml.find("CurrentDisruption").text,
          url=incident_xml.find("CustomURL").text,
        ))
      indicators.append(model.TocServiceIndicator(
        operator=model.TrainOperatingCompany(
          code=toc_xml.find("TocCode").text,
          name=toc_xml.find("TocName").text,
        ),
        status=toc_xml.find("StatusDescription").text,
        incidents=incidents
      ))
    return indicators


  def get_incident_details(self) -> dict[str, model.Incident]:
    """Get all current incidents."""
    incidents = {}

    xml_str = requests.get("https://nrkbproxy.beh.uk/incidents.xml", headers={"user-agent": "not-requests"}).text
    xml_str = re.sub(' xmlns="[^"]+"', "", xml_str)
    xml_str = re.sub(' xmlns:com="[^"]+"', "", xml_str)
    xml_str = re.sub("<com:", "<", xml_str)
    xml_str = re.sub("</com:", "</", xml_str)
    xml_root = ET.fromstring(xml_str)

    for xml_incident in xml_root:
      id = xml_incident.find("IncidentNumber").text # TODO: consider generating our own IDs (ULIDs?) and using this ID as a secondary ID

      # parse incident status
      if xml_incident.find("ClearedIncident") == "true":
        incident_status = model.IncidentStatus.CLEARED
      else:
        incident_status = model.IncidentStatus.ACTIVE

      # parse affected operators
      affected_operators = []
      for xml_operator in xml_incident.find("Affects").find("Operators"):
        affected_operators.append(model.TrainOperatingCompany(
          code=xml_operator.find("OperatorRef").text,
          name=xml_operator.find("OperatorName").text,
        ))

      # parse expiry / end ts
      end_xml = xml_incident.find("ValidityPeriod").find("EndTime")
      if end_xml is not None:
        end_ts = datetime.fromisoformat(end_xml.text).astimezone(TIMEZONE)
      else:
        end_ts = None

      incidents[id] = model.Incident(
        id=id,
        summary=xml_incident.find("Summary").text,
        description=xml_incident.find("Description").text, # TODO: verify that this HTML is safe
        status=incident_status,
        affectedOperators=affected_operators,
        startTs=datetime.fromisoformat(xml_incident.find("ValidityPeriod").find("StartTime").text).astimezone(TIMEZONE),
        endTs=end_ts,
        createdTs=datetime.fromisoformat(xml_incident.find("CreationTime").text).astimezone(TIMEZONE),
        lastUpdatedTs=datetime.fromisoformat(xml_incident.find("ChangeHistory").find("LastChangedDate").text).astimezone(TIMEZONE),
        nrUrl=next(filter(lambda x: x.find("Label").text == "Incident detail page", xml_incident.find("InfoLinks"))).find("Uri").text,
      )

    return incidents
