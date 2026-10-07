#!/usr/bin/env python3
"""
Simple People-in-Space data source.
Fetches the current list of astronauts from the Open Notify API.
"""

import json
import sys
from urllib.request import urlopen, Request

API_URL = "http://api.open-notify.org/astros.json"


def get_people_in_space():
    """Return a list of astronaut names currently in space."""
    req = Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    if data.get("message") != "success":
        raise RuntimeError("API did not return success")
    return [person["name"] for person in data.get("people", [])]


if __name__ == "__main__":
    try:
        astronauts = get_people_in_space()
        print("People currently in space:")
        for name in astronauts:
            print(f"- {name}")
    except Exception as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)