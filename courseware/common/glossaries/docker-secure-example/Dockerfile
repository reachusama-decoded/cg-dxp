# A multi-stage build: stage 1 installs dependencies with the tools that needs; stage 2 ships only the result.
# The final image has no compiler, no pip cache, no requirements file, no source for anything but the app.

# ---------- stage 1: build ----------
# Pinned tag; add @sha256:... after the tag when the build must be bit-for-bit reproducible.
FROM python:3.11-slim AS builder

# Build-time settings: no .pyc files, no pip cache in the layer, no "upgrade pip" nag.
ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependencies go into a self-contained virtualenv at a fixed path, so stage 2 can copy one folder.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the requirements file alone first: this layer is cached until the requirements change,
# so a change to the app's code does not reinstall every package.
WORKDIR /build
COPY app/requirements.txt .
RUN pip install -r requirements.txt

# ---------- stage 2: run ----------
FROM python:3.11-slim

# Who owns this image, for the registry and for whoever finds it running in six months.
LABEL org.opencontainers.image.title="portfolio-api" \
      org.opencontainers.image.description="Secure-container example for the Data Creators course" \
      org.opencontainers.image.source="courseware/common/glossaries/docker-secure-example"

# Unbuffered output so logs reach `docker logs` immediately; the venv on PATH so "python" and "uvicorn" resolve to it.
ENV PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"

# An unprivileged user with a fixed UID (stable across rebuilds, useful for volume permissions) and no login shell.
RUN useradd --uid 10001 --create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Only the installed packages from stage 1 and the application code; nothing from the build context but app/.
# --chown makes the files belong to the app user so a read-only root filesystem still works.
COPY --from=builder --chown=app:app /opt/venv /opt/venv
COPY --chown=app:app app/main.py ./main.py

# Where the data is expected at run time (a mount), and the one port the service listens on.
VOLUME ["/data"]
EXPOSE 8000

# Drop to the unprivileged user before anything runs.
USER app

# The platform asks this every 30 seconds; after three failures the container is reported unhealthy.
# Uses only the standard library, so it works even if the app's dependencies are broken.
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]

# ENTRYPOINT is the fixed program; CMD its default arguments, replaceable on `docker run`.
ENTRYPOINT ["uvicorn", "main:app"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
