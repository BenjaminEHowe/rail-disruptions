# Rail Disruptions
Experiments with the [National Rail Disruptions API](https://raildata.org.uk/dashboard/dataProduct/P-4b85a789-5f14-4763-841a-b3ada659a51a/overview).

## Environment variables
The following environment variables need to be set in order to run the application:
- `NR_API_BASE_URL`: the base URL for the National Rail Disruptions API, usually `https://api1.raildata.org.uk/1010-disruptions-experience-api-11_0/`.
- `NR_API_KEY`: an API key for the National Rail Disruptions API (available from Rail Data Marketplace).

## Development
To start the application in development, run a command like:
```bash
NR_API_BASE_URL=https://api1.raildata.org.uk/1010-disruptions-experience-api-11_0/ NR_API_KEY=secret flask run
```

... and then navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).
