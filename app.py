import apscheduler.schedulers.background
import flask
import logging
import os
import pprint

import api


app = flask.Flask(__name__)
logger = logging.getLogger(__name__)
nrDisruptions = api.NRDisruptionsClient(
  base_url=os.environ.get("NR_API_BASE_URL"),
  api_key=os.environ.get("NR_API_KEY"),
)
scheduler = apscheduler.schedulers.background.BackgroundScheduler()

# TODO: migrate the below state into a database
incidentDetails = {}
serviceIndicators = []


@app.route("/")
def all_operators():
  return flask.render_template(
    "all_operators.html",
    incidentDetails=incidentDetails,
    serviceIndicators=serviceIndicators,
  )


@app.route("/raw")
def raw_data():
  return flask.render_template(
    "raw.html",
    title="Raw Data",
    incidentDetails=pprint.pformat(list(incidentDetails.values()), indent=2, width=140),
    serviceIndicators=pprint.pformat(serviceIndicators, indent=2, width=140),
  )


def refresh_cached_data():
  global incidentDetails, serviceIndicators
  logger.info("Getting updated data from API")
  incidentDetails = {}
  serviceIndicators = nrDisruptions.get_toc_service_indicators()
  serviceIndicators.sort(key=lambda x: x.operator.name.lower())
  for serviceIndicator in serviceIndicators:
    for incident in serviceIndicator.incidents:
      if incident.id not in incidentDetails:
        incidentDetails[incident.id] = nrDisruptions.get_incident_details(incident.id)
  logger.info("Cached data updated successfully")


logging.basicConfig(level=logging.INFO)
refresh_cached_data()
scheduler.start()
scheduler.add_job(refresh_cached_data, "interval", minutes=5)
