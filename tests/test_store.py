from astralmanac import store


def _item(ext, **kw):
    base = {"external_id": ext, "title": "t", "event_time": "2026-01-01T00:00:00+00:00",
            "url": "http://x", "payload": {"a": 1}, "fetched_at": "2026-01-02T00:00:00+00:00"}
    base.update(kw)
    return base


def test_upsert_is_idempotent():
    store.upsert_items("s1", [_item("a"), _item("b")])
    store.upsert_items("s1", [_item("a", title="updated")])
    rows = store.query_items(source="s1")
    assert len(rows) == 2  # 'a' updated in place, not duplicated
    a = next(r for r in rows if r["external_id"] == "a")
    assert a["title"] == "updated"


def test_query_filters_by_source_and_limits():
    store.upsert_items("s1", [_item("a")])
    store.upsert_items("s2", [_item("c")])
    assert len(store.query_items(source="s1")) == 1
    assert len(store.query_items(limit=1)) == 1


def test_record_run_and_status():
    store.upsert_items("s1", [_item("a")])
    store.record_run("s1", ok=True, item_count=1)
    rows = {r["source"]: r for r in store.status()}
    assert rows["s1"]["stored_items"] == 1
    assert rows["s1"]["last_ok"] is not None
