from astralmanac import store
from astralmanac.fetchers import ALL, all_fetchers
from astralmanac.fetchers.base import Fetcher


class _GoodFetcher(Fetcher):
    source = "good"
    description = "test"

    def fetch(self):
        return [{"external_id": "1", "title": "ok", "payload": {"v": 1}}]


class _FailingFetcher(Fetcher):
    source = "bad"
    description = "test"

    def fetch(self):
        raise RuntimeError("boom")


class _KeyedFetcher(Fetcher):
    source = "keyed"
    description = "test"
    requires_key = True

    def available(self):
        return False

    def fetch(self):  # pragma: no cover - never called while dormant
        raise AssertionError("dormant fetcher should not run")


def test_good_fetcher_writes_items():
    assert _GoodFetcher().run() == 1
    assert len(store.query_items(source="good")) == 1


def test_failing_fetcher_is_swallowed_and_recorded():
    assert _FailingFetcher().run() is None
    row = {r["source"]: r for r in store.status()}["bad"]
    assert "boom" in (row["last_error"] or "")


def test_dormant_fetcher_does_not_run():
    assert _KeyedFetcher().run() is None


def test_registry_sources_are_unique_and_nonempty():
    sources = [f.source for f in all_fetchers()]
    assert all(sources)
    assert len(sources) == len(set(sources))
    assert len(ALL) >= 3
