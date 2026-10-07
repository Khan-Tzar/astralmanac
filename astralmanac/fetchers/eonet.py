# astralmanac/fetchers/eonet.py
"""Natural events on Earth (wildfires, storms, volcanoes...), from NASA EONET (key-free)."""
from .base import Fetcher

API = "https://eonet.gsfc.nasa.gov/api/v3/events"


class EonetFetcher(Fetcher):
    source = "natural_events"
    description = "Natural events on Earth (NASA EONET)"

    def fetch(self):
        data = self.get_json(API, params={"status": "open", "limit": 200})
        items = []
        for ev in data.get("events", []):
            geoms = ev.get("geometry") or []
            latest = geoms[-1] if geoms else {}
            items.append({
                "external_id": ev["id"],
                "title": ev.get("title"),
                "event_time": latest.get("date"),
                "url": (ev.get("sources") or [{}])[0].get("url"),
                "payload": ev,
            })
        return items
