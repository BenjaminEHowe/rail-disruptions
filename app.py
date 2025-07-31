import flask
import os

import api


app = flask.Flask(__name__)

incidentDetails = {}
nrDisruptions = api.NRDisruptionsClient(
  base_url=os.environ.get("NR_API_BASE_URL"),
  api_key=os.environ.get("NR_API_KEY"),
)
serviceIndicators = nrDisruptions.get_toc_service_indicators()
serviceIndicators.sort(key=lambda x: x.operator.name.lower())
for serviceIndicator in serviceIndicators:
  for incident in serviceIndicator.incidents:
    if incident.id not in incidentDetails:
      incidentDetails[incident.id] = nrDisruptions.get_incident_details(incident.id)


@app.route("/")
def all_operators():
  return flask.render_template(
    "all_operators.html",
    incidentDetails=incidentDetails,
    serviceIndicators=serviceIndicators,
  )
