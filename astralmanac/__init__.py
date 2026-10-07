"""Astralmanac — a self-hostable hub for public space & astronomy data.

Harvests multiple space data sources into one local SQLite store on a gentle
schedule, and serves a dashboard and JSON API that only ever read that store.
Boring on purpose: one container, one file, no external database.
"""
__version__ = "0.1.0"
