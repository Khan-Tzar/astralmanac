# astralmanac/fetchers/apod.py
"""NASA Astronomy Picture of the Day. Requires a NASA api.nasa.gov key, so this
fetcher stays dormant until NASA_API_KEY is set — the reference example of a
keyed source in an otherwise key-free default set."""
from .. import config
from .base import Fetcher

API = "https://api.nasa.gov/planetary/apod"


class ApodFetcher(Fetcher):
    source = "apod"
    description = "NASA Astronomy Picture of the Day (needs NASA_API_KEY)"
    requires_key = True

    def available(self):
        return bool(config.NASA_API_KEY)

    def fetch(self):
        data = self.get_json(API, params={"api_key": config.NASA_API_KEY, "count": 1})
        entry = data[0] if isinstance(data, list) else data
        return [{
            "external_id": entry["date"],
            "title": entry.get("title"),
            "event_time": entry.get("date"),
            "url": entry.get("url"),
            "payload": entry,
        }]
