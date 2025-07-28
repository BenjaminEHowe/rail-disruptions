import os

import api


incidentDetails = {}


if __name__ == "__main__":
    nrDisruptions = api.NRDisruptionsClient(
        base_url=os.environ.get("NR_API_BASE_URL"),
        api_key=os.environ.get("NR_API_KEY"),
    )
    print("Data provided by National Rail (https://www.nationalrail.co.uk/) and the Rail Delivery Group (https://www.raildeliverygroup.com/)")
    operators = nrDisruptions.get_toc_service_indicators()
    operators.sort(key=lambda x: x["tocName"].lower())
    for operator in operators:
        print(f"{operator["tocName"]} ({operator["tocCode"]}): {operator["tocStatusDescription"]}")
        if "tocServiceGroup" in operator:
            incidents = operator["tocServiceGroup"]
            for incident in incidents:
                incidentId = incident["currentDisruption"]
                if incidentId not in incidentDetails:
                    incidentDetails[incidentId] = nrDisruptions.get_incident_details(incidentId)
                summary = incidentDetails[incidentId]["summary"]
                if incidentDetails[incidentId]["status"] == "Cleared":
                    summary = f"CLEARED: {summary}"
                print(f"  {summary} ({incident["customURL"]})")
