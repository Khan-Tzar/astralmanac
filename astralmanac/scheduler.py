# astralmanac/scheduler.py
"""Runs every available fetcher once, then sleeps and repeats.

This is intentionally a plain loop, not a cron daemon or a task queue: a single
long-running process that wakes on an interval is all a slow-moving dataset
needs, and it keeps the deployment to one container. Each fetcher's own
``run()`` never raises, so one bad source cannot stop the loop.
"""
import logging
import time

from . import config, store
from .fetchers import all_fetchers

logger = logging.getLogger("astralmanac.scheduler")


def run_once():
    """One pass over all fetchers. Returns {source: items_written_or_None}."""
    store.init_db()
    results = {}
    for f in all_fetchers():
        n = f.run()
        results[f.source] = n
        if n is None:
            logger.info("%s: skipped or failed", f.source)
        else:
            logger.info("%s: %d items", f.source, n)
    return results


def run_forever(interval=None):
    interval = interval or config.FETCH_INTERVAL_SECONDS
    logger.info("scheduler starting, interval=%ss", interval)
    while True:
        run_once()
        time.sleep(interval)
