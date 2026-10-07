FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY astralmanac ./astralmanac
RUN pip install --no-cache-dir .

ENV ASTRALMANAC_DB=/data/astralmanac.db
VOLUME ["/data"]
EXPOSE 8000

# Default: serve the dashboard + API. The scheduler runs as a second service
# (see docker-compose.yml) so one container does one job.
CMD ["astralmanac", "serve"]
