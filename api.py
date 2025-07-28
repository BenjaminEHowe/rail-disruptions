import uplink
import uplink.auth


@uplink.headers({
    "User-Agent": "uk.beh.rail-disruptions/0.1.0"
})
class NRDisruptionsClient(uplink.Consumer):
  """Client for the National Rail Disruptions API"""

  def __init__(self, base_url: str, api_key: str):
    super().__init__(base_url=base_url, auth=uplink.auth.ApiTokenHeader("x-apikey", api_key))

  @uplink.returns.json
  @uplink.get("tocs/serviceIndicators")
  def get_toc_service_indicators(self):
    """Get service indicators for Train Operating Companies"""

  @uplink.returns.json
  @uplink.get("disruptions/incidents/{incident_number}")
  def get_incident_details(self, incident_number: uplink.Path):
    """Get details about an incident"""
