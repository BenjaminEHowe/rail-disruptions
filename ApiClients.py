import uplink

@uplink.headers({
    "User-Agent": "uk.beh.rail-disruptions/0.1.0"
})
class NRDisruptionsClient(uplink.Consumer):
  """Client for the National Rail Disruptions API"""
  authToken: str

  @uplink.returns.json
  @uplink.get("tocs/serviceIndicators")
  def get_toc_service_indicators(self):
    """Get service indicators for Train Operating Companies"""

  @uplink.returns.json
  @uplink.get("disruptions/incidents/{incident_number}")
  def get_incident_details(self, incident_number: uplink.Path):
    """Get details about an incident"""
