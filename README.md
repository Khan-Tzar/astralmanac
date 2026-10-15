# Astralmanac

**A self-hostable almanac of public space & astronomy data.**

Astralmanac harvests several public space data sources on a gentle schedule into
one small local store, and serves them as a clean dashboard and a JSON API. It
is deliberately boring to run: one container, one SQLite file, no external
database, and — in the default configuration — no API keys at all.

Point it at the sky's data firehoses once, and from then on you query *your*
copy: fast, offline-friendly, and never rate-limited by anyone upstream.

```
┌── scheduler ──┐      harvest on an interval      ┌─────────────┐
│  fetchers:    │  ───────────────────────────▶    │  astralmanac │
│  launches     │                                   │   .db (SQLite)│
│  close_appr.  │                                   └──────┬──────┘
│  natural_evts │      read-only, never upstream          │
└───────────────┘                                   ┌──────▼──────┐
                                                     │  web: /  + /api │
                                                     └─────────────┘
```

## What it collects (out of the box, key-free)

| Source | What | Upstream |
|---|---|---|
| `launches` | Upcoming rocket launches | Launch Library 2 |
| `close_approaches` | Near-Earth asteroid close approaches | JPL CNEOS / SSD |
| `natural_events` | Wildfires, storms, volcanoes… on Earth | NASA EONET |
| `iss` | Current position of the International Space Station | Open Notify |
| `apod` | Astronomy Picture of the Day *(needs a free NASA key)* | api.nasa.gov |

The default four need **no key and no account**. `apod` is the reference
example of a keyed source: it stays dormant until you set `NASA_API_KEY`.

## Quickstart

### Docker (recommended)

```bash
git clone https://github.com/Khan-Tzar/astralmanac.git
cd astralmanac
docker compose up -d --build
# dashboard: http://localhost:8000
```

The `scheduler` service fills the store on its first pass (within a minute);
the `web` service serves it. To activate NASA-keyed sources:

```bash
NASA_API_KEY=your_key docker compose up -d
```

### Local (Python 3.10+)

```bash
pip install -e .
astralmanac initdb
astralmanac fetch           # harvest every available source once
astralmanac serve           # http://localhost:8000
# or keep it fresh in the background:
astralmanac schedule
```

## The JSON API

Everything the dashboard shows is available as JSON (served from the local
store, so it is instant):

- `GET /api/items?source=<id>&limit=<n>` — stored items, newest first
- `GET /api/sources` — the registered sources and whether each is active
- `GET /api/status` — last run time and item count per source
- `GET /healthz` — liveness

## Adding a data source

A source is one small, self-contained file — which is exactly why it is the
best way to contribute. Subclass `Fetcher`, return a list of items, register it:

```python
# astralmanac/fetchers/iss.py
from .base import Fetcher

class IssFetcher(Fetcher):
    source = "iss"
    description = "Current position of the ISS"

    def fetch(self):
        data = self.get_json("http://api.open-notify.org/iss-now.json")
        return [{
            "external_id": str(data["timestamp"]),
            "title": "ISS position",
            "event_time": None,
            "url": "http://open-notify.org/",
            "payload": data,
        }]
```

Then add `IssFetcher` to `ALL` in `astralmanac/fetchers/__init__.py`. (This example now ships, slightly fuller, as
[`astralmanac/fetchers/iss.py`](astralmanac/fetchers/iss.py).) The
scheduler, store, dashboard and API pick it up automatically. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## Design

- **Fetchers never run during a web request.** The scheduler writes the store;
  the web layer only reads it. Upstream rate limits can never affect a visitor.
- **A failing source fails alone.** Each fetcher's run is best-effort: an
  exception is recorded against that source and swallowed, so one outage never
  stops the hub.
- **Zero-config by default.** The default sources are key-free; a keyed source
  is simply dormant until its key exists.

## License

[MIT](LICENSE).
