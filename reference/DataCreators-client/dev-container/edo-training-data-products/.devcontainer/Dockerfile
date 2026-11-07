#syntax=cgregistry.capgroup.com/fix-container-certs:1.9
FROM flyway/flyway:11.8.0 AS flyway
FROM cgregistry-aws.capgroup.com/capgroup.com/python:3.13-dev

USER root

# Put certs in default locations (required for deploying bundles)
RUN mkdir -p /etc/ssl/certs && ln -sf /cacert.pem /etc/ssl/certs/ca-certificates.crt && ln -sf /cacert.pem /etc/ssl/ca-bundle.pem && mkdir -p /etc/pki/tls/certs && ln -sf /cacert.pem /etc/pki/tls/certs/ca-bundle.crt

# VS Code server checks call `getconf` (POSIX). Install libc-utils to provide it.
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add curl posix-libc-utils ripgrep bubblewrap socat docker docker-cli docker-compose bash gh jq \
        && ldconfig \
        && if ! command -v getconf >/dev/null 2>&1; then \
                    if [ -x /bin/busybox ]; then ln -sf /bin/busybox /usr/bin/getconf; fi; \
                fi

# Install Astro CLI
RUN curl -sSL install.astronomer.io | bash -s

# Install Starship prompt
RUN curl -fsSL https://starship.rs/install.sh | sh -s -- --yes

# Install mise for environment management
RUN curl -fsSL https://mise.jdx.dev/install.sh | MISE_VERSION=v2026.4.20 sh && \
    mv /root/.local/bin/mise /usr/local/bin/mise && \
    chmod +x /usr/local/bin/mise && \
    echo "✓ Mise installed"

# Copy setup scripts to fixed absolute paths
COPY .devcontainer/utils/setup-databricks-config.sh /tmp/setup-databricks-config.sh

# Install Databricks CLI via mise
ARG DATABRICKS_CLI_VERSION="0.236.0"
RUN mise install databricks-cli@${DATABRICKS_CLI_VERSION}

# Use Internal PyPI
COPY .devcontainer/utils/pip.conf /etc/pip.conf

# Configure Starship prompt
RUN mkdir -p /root/.config
COPY .devcontainer/utils/starship.toml /root/.config/starship.toml
COPY .devcontainer/utils/bashrc /root/.bashrc
RUN sed -i 's/\r$//' /root/.bashrc \
    && chmod 644 /root/.bashrc

# Create/configure a shared virtualenv inside the image
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    /usr/bin/python3 -m venv /opt/venv \
    && /opt/venv/bin/python -m pip install --upgrade pip setuptools wheel uv \
    && chown -R nonroot:nonroot /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Why: uv creates isolated Python build environments, so the SSL relaxation hook
# must be available on PYTHONPATH before dependency builds start.
COPY .devcontainer/sitecustomize.py /usr/local/share/sitecustomize.py
ENV PYTHONPATH="/usr/local/share"
RUN set -e; \
        for d in \
            /usr/lib/python3.13/site-packages \
            /usr/local/lib/python3.13/site-packages \
            /usr/local/lib/python3.13/dist-packages \
            /opt/venv/lib/python3.13/site-packages \
            ; do \
            [ -d "$d" ] || continue; \
            cp /usr/local/share/sitecustomize.py "$d/sitecustomize.py"; \
        done

# RUN groupadd -f docker && addgroup nonroot docker #here in case of change to nonroot user

# USER nonroot

# Install Java and Flyway (from official image)
RUN --mount=type=cache,target=/var/cache/apk,sharing=locked \
    apk add openjdk-17-jre && \
    JAVA_BIN=$(find /usr -name "java" -type f 2>/dev/null | head -1) && \
    ln -sf "$JAVA_BIN" /usr/local/bin/java
COPY --from=flyway /flyway /opt/flyway
RUN ln -sf /opt/flyway/flyway /usr/local/bin/flyway && \
    echo "Flyway installed"

# Install datacounsel CLI
COPY datacounsel /opt/datacounsel
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    cd /opt/datacounsel && uv sync --active --locked --no-dev --no-editable --quiet && \
    echo "datacounsel installed"

# VS Code Python experience helpers
COPY .devcontainer/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install -r requirements.txt

# Install devcontainer lifecycle scripts
COPY .devcontainer/start-dockerd.sh /usr/local/bin/start-dockerd.sh
COPY .devcontainer/ensure-dockerd.sh /usr/local/bin/ensure-dockerd.sh
COPY .devcontainer/post-start.sh /usr/local/bin/post-start.sh
COPY .devcontainer/check.sh /usr/local/bin/dpc-check
RUN chmod +x /usr/local/bin/start-dockerd.sh /usr/local/bin/ensure-dockerd.sh /usr/local/bin/post-start.sh /usr/local/bin/dpc-check