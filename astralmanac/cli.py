# astralmanac/cli.py
"""Command line entry point: ``astralmanac <command>``."""
import argparse
import logging
import sys

from . import scheduler, store
from .fetchers import all_fetchers, get


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(prog="astralmanac", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("initdb", help="Create the SQLite store.")
    sub.add_parser("sources", help="List registered data sources.")
    p_fetch = sub.add_parser("fetch", help="Fetch once, then exit.")
    p_fetch.add_argument("source", nargs="?", help="Only this source (default: all).")
    p_sched = sub.add_parser("schedule", help="Fetch on an interval, forever.")
    p_sched.add_argument("--interval", type=int, default=None, help="Seconds between passes.")
    p_serve = sub.add_parser("serve", help="Run the web dashboard + API.")
    p_serve.add_argument("--host", default=None)
    p_serve.add_argument("--port", type=int, default=None)

    args = parser.parse_args(argv)

    if args.command == "initdb":
        store.init_db()
        print(f"Store ready at {store.config.DB_PATH}")
    elif args.command == "sources":
        for f in all_fetchers():
            state = "ready" if f.available() else "dormant (needs key)"
            print(f"  {f.source:18} {state:22} {f.description}")
    elif args.command == "fetch":
        store.init_db()
        if args.source:
            f = get(args.source)
            if f is None:
                print(f"Unknown source: {args.source}", file=sys.stderr)
                return 2
            n = f.run()
            print(f"{args.source}: {'skipped/failed' if n is None else str(n) + ' items'}")
        else:
            for src, n in scheduler.run_once().items():
                print(f"{src}: {'skipped/failed' if n is None else str(n) + ' items'}")
    elif args.command == "schedule":
        scheduler.run_forever(interval=args.interval)
    elif args.command == "serve":
        from .web.app import run
        run(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
