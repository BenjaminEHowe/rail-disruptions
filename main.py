import os

import api
import model

incidentDetails = {}


if __name__ == "__main__":
    nrDisruptions = api.NRDisruptionsClient(
        base_url=os.environ.get("NR_API_BASE_URL"),
        api_key=os.environ.get("NR_API_KEY"),
    )
    print("Data provided by National Rail (https://www.nationalrail.co.uk/) and the Rail Delivery Group (https://www.raildeliverygroup.com/)")
    operatorServiceIndicators = nrDisruptions.get_toc_service_indicators()
    operatorServiceIndicators.sort(key=lambda x: x.operator.name.lower())
    for serviceIndicator in operatorServiceIndicators:
        print(f"{serviceIndicator.operator.name} ({serviceIndicator.operator.code}): {serviceIndicator.status}")
        if len(serviceIndicator.incidents):
            for incident in serviceIndicator.incidents:
                if incident.id not in incidentDetails:
                    incidentDetails[incident.id] = nrDisruptions.get_incident_details(incident.id)
                details = incidentDetails[incident.id]
                summary = details.summary
                if details.status == model.IncidentStatus.CLEARED:
                    summary = f"CLEARED: {summary}"
                print(f"  {summary} ({incident.url})")
                print(f"    Incident started {details.startTs.strftime("%d/%m/%Y, %H:%M:%S")}")
                print(f"    Last updated {details.lastUpdatedTs.strftime("%d/%m/%Y, %H:%M:%S")}")
