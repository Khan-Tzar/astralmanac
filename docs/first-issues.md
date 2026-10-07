# Seed "good first issues"

Open these as GitHub issues after publishing — they give newcomers an obvious,
well-scoped way in, and they grow the project's value directly.

## 1. Add an ISS current-position data source
**good first issue** · Add `astralmanac/fetchers/iss.py` using the key-free
`http://api.open-notify.org/iss-now.json` endpoint, register it in `ALL`.
A worked example is already in the README's "Adding a data source" section.

## 2. Add a People-in-Space data source
**good first issue** · `http://api.open-notify.org/astros.json` (key-free)
lists everyone currently in space. One item per person, or one summary item.

## 3. Add NASA NeoWs (near-Earth object feed) as a keyed source
**good first issue** · Mirror `apod.py`: `requires_key = True`, read
`NASA_API_KEY`, fetch `https://api.nasa.gov/neo/rest/v1/feed`.

## 4. Add a `?since=` filter to `/api/items`
**good first issue** · Accept an ISO date and return only items with
`event_time >= since`. Add a test.

## 5. Add a per-source "stale" badge to the dashboard
Show when a source's `last_ok` is older than, say, 2× the fetch interval, so a
silently-failing source is visible. (The data is already in `/api/status`.)

## 6. Package a GitHub Action that publishes to PyPI on tag
Infrastructure task: a release workflow building the sdist/wheel and uploading
on a `v*` tag.
