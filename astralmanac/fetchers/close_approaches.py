# astralmanac/fetchers/close_approaches.py
"""Near-Earth asteroid close approaches, from JPL's SSD/CNEOS CAD API (key-free)."""
from .base import Fetcher

API = "https://ssd-api.jpl.nasa.gov/cad.api"


class CloseApproachesFetcher(Fetcher):
    source = "close_approaches"
    description = "Asteroid close approaches to Earth (JPL CNEOS)"

    def fetch(self):
        # Approaches within the next 60 days, sorted by date.
        data = self.get_json(API, params={"date-min": "now", "date-max": "+60", "sort": "date"})
        fields = data.get("fields", [])
        idx = {name: i for i, name in enumerate(fields)}
        items = []
        for row in data.get("data", []):
            des = row[idx["des"]]
            cd = row[idx["cd"]]  # close-approach date/time
            items.append({
                "external_id": f"{des}@{cd}",
                "title": f"{des.strip()} — {row[idx['dist']]} au",
                "event_time": _cd_to_iso(cd),
                "url": "https://cneos.jpl.nasa.gov/ca/",
                "payload": {name: row[i] for name, i in idx.items()},
            })
        return items


def _cd_to_iso(cd):
    """JPL CAD dates look like '2026-Oct-07 13:45'. Convert to ISO 8601, or
    return the original string if the format is unexpected."""
    from datetime import datetime
    for fmt in ("%Y-%b-%d %H:%M", "%Y-%b-%d"):
        try:
            return datetime.strptime(cd.strip(), fmt).isoformat()
        except ValueError:
            continue
    return cd
