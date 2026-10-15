# astralmanac/fetchers/iss.py
"""Current position of the International Space Station, from Open Notify (key-free).

One request per fetch. Each fetch is keyed by the API's own timestamp, so the
store keeps one row per sampled position — over time, a sparse ground track.
Open Notify serves this endpoint over plain HTTP only.
"""
from datetime import datetime, timezone

from .base import Fetcher

API = "http://api.open-notify.org/iss-now.json"


class IssFetcher(Fetcher):
    source = "iss"
    description = "Current position of the ISS"

    def fetch(self):
        data = self.get_json(API)
        if data.get("message") != "success":
            raise RuntimeError(f"Open Notify answered {data.get('message')!r}")
        ts = int(data["timestamp"])
        pos = data.get("iss_position") or {}
        lat, lon = float(pos["latitude"]), float(pos["longitude"])
        ns, ew = ("N" if lat >= 0 else "S"), ("E" if lon >= 0 else "W")
        return [{
            "external_id": str(ts),
            "title": f"ISS over {abs(lat):.2f}°{ns}, {abs(lon):.2f}°{ew}",
            "event_time": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
            "url": f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=4/{lat}/{lon}",
            "payload": data,
        }]
