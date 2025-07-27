import uplink.auth

import ApiClients
import secrets


incidentDetails = {}


if __name__ == "__main__":
    nrDisruptions = ApiClients.NRDisruptionsClient(
        base_url="https://api1.raildata.org.uk/1010-disruptions-experience-api-11_0/",
        auth=uplink.auth.ApiTokenHeader("x-apikey", secrets.nrApiKey),
    )
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
