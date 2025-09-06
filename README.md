# Rail Disruptions
Experiments with the [National Rail Disruptions API](https://raildata.org.uk/dashboard/dataProduct/P-4b85a789-5f14-4763-841a-b3ada659a51a/overview).

## Environment variables
The following environment variables may be set in customise how the application behaves:
- `NR_KB_PROXY_URL`: the base URL for an instance of [the National Rail KnowledgeBase Proxy](https://github.com/BenjaminEHowe/national-rail-knowledgebase-proxy), defaults to `https://nrkbproxy.beh.uk`.

## Development
To start the application in development, run a command like:
```bash
NR_KB_PROXY_URL=... flask run
```

... and then navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

To build the container image locally:
```bash
docker build -t rail-disruptions:local .
```

To run the container:
```bash
 docker run -p 5000:5000 -e NR_KB_PROXY_URL=... rail-disruptions:local
```
