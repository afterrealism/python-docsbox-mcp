# syntax=docker/dockerfile:1.7
# Multi-stage build for python-docsbox-mcp.
# Final image runs as a non-root user on a slim Python base.

ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim AS build
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /src
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY corpus ./corpus
RUN pip install --upgrade pip build \
 && python -m build --wheel --outdir /dist .

FROM python:${PYTHON_VERSION}-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PY_DOCSBOX_BIND=0.0.0.0:7811
RUN groupadd --system --gid 10001 docsbox \
 && useradd  --system --uid 10001 --gid docsbox --home-dir /home/docsbox --create-home docsbox \
 && apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl tini \
 && rm -rf /var/lib/apt/lists/*

COPY --from=build /dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl \
 && rm /tmp/*.whl

USER docsbox
WORKDIR /home/docsbox
EXPOSE 7811
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -fsS http://127.0.0.1:7811/health || exit 1
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python-docsbox-mcp"]
