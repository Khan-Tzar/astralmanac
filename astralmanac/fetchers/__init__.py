# astralmanac/fetchers/__init__.py
"""The fetcher registry.

To add a data source: write a ``Fetcher`` subclass in this package and add it to
``ALL`` below. That is the whole wiring — everything else (scheduling, storage,
the dashboard, the API) picks it up automatically.
"""
from .apod import ApodFetcher
from .base import Fetcher
from .close_approaches import CloseApproachesFetcher
from .eonet import EonetFetcher
from .iss import IssFetcher
from .launches import LaunchesFetcher

#: Every fetcher the app knows about. Order is cosmetic (dashboard ordering).
ALL = [
    LaunchesFetcher,
    CloseApproachesFetcher,
    EonetFetcher,
    IssFetcher,
    ApodFetcher,
]


def all_fetchers():
    """Instantiated fetchers, one per registered class."""
    return [cls() for cls in ALL]


def get(source):
    """The fetcher instance for a given source id, or None."""
    for f in all_fetchers():
        if f.source == source:
            return f
    return None


__all__ = ["Fetcher", "ALL", "all_fetchers", "get"]
