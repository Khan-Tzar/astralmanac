# astralmanac/fetchers/launches.py
"""Upcoming rocket launches, from the Launch Library 2 API (key-free)."""
from .base import Fetcher

API = "https://ll.thespacedevs.com/2.2.0/launch/upcoming/"


class LaunchesFetcher(Fetcher):
    source = "launches"
    description = "Upcoming rocket launches (Launch Library 2)"

    def fetch(self):
        data = self.get_json(API, params={"limit": 50, "mode": "list"})
        items = []
        for launch in data.get("results", []):
            items.append({
                "external_id": launch["id"],
                "title": launch.get("name"),
                "event_time": launch.get("net"),  # No Earlier Than, ISO 8601
                "url": "https://thespacedevs.com/llapi",
                "payload": launch,
            })
        return items
