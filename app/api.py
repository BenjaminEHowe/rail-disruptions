import logging
import uplink
import uplink.auth

from datetime import datetime
from zoneinfo import ZoneInfo

import model


TIMEZONE = ZoneInfo("Europe/London")

logger = logging.getLogger(__name__)


@uplink.headers({
    "User-Agent": "uk.beh.rail-disruptions/0.1.0"
})
class NRDisruptionsClient(uplink.Consumer):
  """Client for the National Rail Disruptions API."""


  def __init__(self, base_url: str, api_key: str):
    super().__init__(base_url=base_url, auth=uplink.auth.ApiTokenHeader("x-apikey", api_key))


  @uplink.returns.json
  @uplink.get("tocs/serviceIndicators")
  def _get_toc_service_indicators(self):
    """Get service indicators for Train Operating Companies (returns dictionary)."""


  def get_toc_service_indicators(self) -> list[model.TocServiceIndicator]:
    json = self._get_toc_service_indicators()
    indicators = []
    for item in json:
      incidents = []
      if "tocServiceGroup" in item:
        for incident in item["tocServiceGroup"]:
          incidents.append(model.IncidentWithoutDetails(
            id=incident["currentDisruption"],
            url=incident["customURL"],
          ))
      indicators.append(model.TocServiceIndicator(
        operator=model.TrainOperatingCompany(
          code=item["tocCode"],
          name=item["tocName"],
        ),
        status=item["tocStatusDescription"],
        incidents=incidents
      ))
    return indicators


  @uplink.returns.json
  @uplink.get("disruptions/incidents/{incident_number}")
  def _get_incident_details(self, incident_number: uplink.Path):
    """Get details about an incident (returns dictionary)."""


  def get_incident_details(self, incident_number: str) -> model.Incident:
    json = self._get_incident_details(incident_number)

    try:
      # parse incident status
      if json["status"] == "Active":
        incident_status = model.IncidentStatus.ACTIVE
      elif json["status"] == "Cleared":
        incident_status = model.IncidentStatus.CLEARED
      else:
        raise ValueError(f"Unable to parse incident {json["id"]}, unrecognised `status` of \"{json["status"]}\"")

      # parse affected operators
      affected_operators = []
      for operator in json["affectedOperators"]:
        affected_operators.append(model.TrainOperatingCompany(
          code=operator["tocCode"],
          name=operator["tocName"],
        ))

      # parse expiry timestamp
      if json["expiryDateTime"]:
        expiry_ts = datetime.fromisoformat(json["expiryDateTime"]).astimezone(TIMEZONE)
      else:
        expiry_ts = None

      return model.Incident(
        id=json["id"], # TODO: consider generating our own IDs (ULIDs?) and using this ID as a secondary ID
        summary=json["summary"],
        description=json["description"], # TODO: verify that this HTML is safe
        status=incident_status,
        affectedOperators=affected_operators,
        startTs=datetime.fromisoformat(json["startDateTime"]).astimezone(TIMEZONE),
        expiryTs=expiry_ts,
        createdTs=datetime.fromisoformat(json["createdDateTime"]).astimezone(TIMEZONE),
        lastUpdatedTs=datetime.fromisoformat(json["lastModifiedDateTime"]).astimezone(TIMEZONE),
        lastUpdatedBy=json["lastChangedBy"],
        nrUrl=next(filter(lambda x: x["label"] == "Incident detail page", json["disruptionLinks"]))["uri"],
      )
    except KeyError as e:
      logger.warning(f"Got KeyError when trying to decode details for incident {incident_number}:")
      logger.warning(json)
      raise e
