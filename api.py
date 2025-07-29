import uplink
import uplink.auth

import model


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

    return model.Incident(
      id=json["id"],
      version=json["version"],
      summary=json["summary"],
      description=json["description"],
      status=incident_status,
      affectedOperators=affected_operators,
    )
