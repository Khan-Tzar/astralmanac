# astralmanac/web/app.py
"""The web layer: a small Flask app that only ever reads the store.

It never calls an upstream API during a request — that is the scheduler's job.
A request just queries SQLite, so the dashboard and the JSON API are fast and
cannot be rate-limited by anyone upstream.
"""
import json

from flask import Flask, Response, render_template, request

from .. import config, store
from ..fetchers import all_fetchers


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def index():
        source = request.args.get("source") or None
        sources = [{"id": f.source, "description": f.description,
                    "available": f.available()} for f in all_fetchers()]
        items = store.query_items(source=source, limit=100)
        for it in items:
            it["payload"] = json.loads(it["payload"])
        return render_template("index.html", items=items, sources=sources,
                               selected=source, status=store.status())

    @app.route("/api/items")
    def api_items():
        source = request.args.get("source") or None
        try:
            limit = min(int(request.args.get("limit", 100)), 1000)
        except ValueError:
            limit = 100
        items = store.query_items(source=source, limit=limit)
        for it in items:
            it["payload"] = json.loads(it["payload"])
        return _json({"source": source, "count": len(items), "items": items})

    @app.route("/api/sources")
    def api_sources():
        return _json([{"id": f.source, "description": f.description,
                       "available": f.available(), "requires_key": f.requires_key}
                      for f in all_fetchers()])

    @app.route("/api/status")
    def api_status():
        return _json({"sources": store.status()})

    @app.route("/healthz")
    def healthz():
        return _json({"status": "ok"})

    return app


def _json(obj):
    return Response(json.dumps(obj, ensure_ascii=False, indent=2),
                    mimetype="application/json")


def run(host=None, port=None):
    store.init_db()
    app = create_app()
    app.run(host=host or config.HOST, port=port or config.PORT)
