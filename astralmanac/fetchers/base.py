# astralmanac/fetchers/base.py
"""The fetcher contract.

A fetcher pulls one data source and turns it into Astralmanac items. Subclasses
implement :meth:`fetch`, which returns a list of item dicts; the base class
handles the parts every source shares — the HTTP session, recording the run,
and the rule that a source which needs a key stays dormant until it has one.

Adding a new source is deliberately a small, self-contained job: subclass
``Fetcher``, implement ``fetch``, and register it. That is the whole extension
surface, and it is why "add a data source" makes a good first contribution.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import requests

from .. import config, store


class Fetcher(ABC):
    #: Short, stable, lowercase identifier used as the ``source`` tag and in URLs.
    source: str = ""
    #: One-line human description, shown in the dashboard.
    description: str = ""
    #: True if this source needs an API key it does not currently have. Such a
    #: fetcher is skipped rather than run, so the app works with zero config.
    requires_key: bool = False

    def __init__(self):
        if not self.source:
            raise ValueError(f"{type(self).__name__} must set a 'source'")
        self.session = requests.Session()
        self.session.headers["User-Agent"] = config.USER_AGENT

    def get_json(self, url, **kwargs):
        kwargs.setdefault("timeout", config.REQUEST_TIMEOUT_SECONDS)
        resp = self.session.get(url, **kwargs)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def now_iso():
        return datetime.now(timezone.utc).isoformat()

    @abstractmethod
    def fetch(self):
        """Return a list of item dicts. Each item must have an ``external_id``
        and a ``payload``; ``title``, ``event_time`` (ISO 8601) and ``url`` are
        optional but power the dashboard's sorting and display."""
        raise NotImplementedError

    def available(self):
        """Whether this fetcher can run now. The default rule: dormant if it
        needs a key and none is set. Override for other preconditions."""
        return not self.requires_key

    def run(self):
        """Fetch and store, never raising. A source being down must not take the
        rest of the hub with it, so failures are recorded and swallowed. Returns
        the number of items written, or None if it did not run."""
        if not self.available():
            return None
        fetched_at = self.now_iso()
        try:
            items = self.fetch()
            for it in items:
                it.setdefault("payload", {})
                it["fetched_at"] = fetched_at
            n = store.upsert_items(self.source, items)
            store.record_run(self.source, ok=True, item_count=n)
            return n
        except Exception as exc:  # noqa: BLE001 - best effort by design
            store.record_run(self.source, ok=False, error=f"{type(exc).__name__}: {exc}"[:300])
            return None
