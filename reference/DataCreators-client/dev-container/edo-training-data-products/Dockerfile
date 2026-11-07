#syntax=cgregistry.capgroup.com/fix-container-certs:1.9
## Astronomer Runtime base image (Airflow 3).
FROM cgprdregistry-aws.capgroup.com/astronomer/astro-runtime:3.1-17-base AS stage1

LABEL maintainer="Caspian Platform <caspian_platform_pod@capgroup.com>"
ARG BUILD_NUMBER=-1
LABEL io.astronomer.docker=true
LABEL io.astronomer.docker.build.number=$BUILD_NUMBER
LABEL io.astronomer.docker.airflow.onbuild=false
# Install Python and OS-Level Packages

USER root

# https://www.astronomer.io/docs/astro/cli/customize-dockerfile/#add-a-ca-certificate-to-an-astro-runtime-image
# Add internal CA certificate
ADD https://cgrepo-aws.capgroup.com/repository/cgfiles/network/cg-decrypt-cert/cacert-2021-07-23.pem /usr/local/share/ca-certificates/cacert-2021-07-23.pem
RUN update-ca-certificates && chmod +rx /usr/local/share/ca-certificates/cacert-2021-07-23.pem && \
    echo 'deb [trusted=yes] https://cgrepo-aws.capgroup.com/repository/apt-proxy-12/ bookworm main contrib non-free non-free-firmware' > /etc/apt/sources.list && \
    echo 'deb-src [trusted=yes] https://cgrepo-aws.capgroup.com/repository/apt-proxy-12/ bookworm main contrib non-free non-free-firmware' >> /etc/apt/sources.list && \
    echo 'deb [trusted=yes] https://cgrepo-aws.capgroup.com/repository/apt-proxy-12/ bookworm-updates main contrib non-free non-free-firmware' >> /etc/apt/sources.list && \
    echo 'deb-src [trusted=yes] https://cgrepo-aws.capgroup.com/repository/apt-proxy-12/ bookworm-updates main contrib non-free non-free-firmware' >> /etc/apt/sources.list && \
    echo 'deb [trusted=yes] https://cgrepo-aws.capgroup.com/repository/apt-proxy-12/ bookworm-proposed-updates main contrib non-free non-free-firmware' >> /etc/apt/sources.list && \
    echo 'deb-src [trusted=yes] https://cgrepo-aws.capgroup.com/repository/apt-proxy-12/ bookworm-proposed-updates main contrib non-free non-free-firmware' >> /etc/apt/sources.list

# Create symlink for Kafka/librdkafka to find CA certificates (expects Red Hat path)
RUN mkdir -p /etc/pki/tls/certs && \
    ln -sf /etc/ssl/certs/ca-certificates.crt /etc/pki/tls/certs/ca-bundle.crt

# Install OS Packages
COPY os-packages.txt .
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get update \
    && xargs -r apt-get install -y < os-packages.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

FROM stage1 AS stage2
# Install Python Packages
ENV PIP_INDEX_URL=https://cgrepo-aws.capgroup.com/repository/cgpypi/simple

# Why: PIP_NO_CACHE_DIR=true is set in the Astronomer Runtime base image (via ENV and /etc/pip.conf),
# which makes the cache mount a no-op. Clear it here so the mount is actually used.
# env -u in the RUN command guarantees the var is unset even if inherited from a parent layer.
ENV PIP_NO_CACHE_DIR=""

COPY requirements-pypi.txt ./requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip,id=airflow-pip312-${TARGETARCH},sharing=locked \
    env -u PIP_NO_CACHE_DIR pip install -r requirements.txt --extra-index-url https://cgrepo.capgroup.com/repository/cgpypi/simple

FROM stage1 AS stage3
# Copy requirements directory
COPY --from=stage2 /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=stage2 /usr/local/bin /home/astro/.local/bin

ENV PATH="/home/astro/.local/bin:$PATH"

# COPY --link . .
USER astro

# create a venv for dbt-cosmos, which requires conflicting dbt dependencies
ENV PIP_INDEX_URL=https://cgrepo-aws.capgroup.com/repository/cgpypi/simple

COPY requirements-venv-cosmos.txt .

RUN --mount=type=cache,target=/home/astro/.cache/pip,sharing=locked \
    mkdir -p /home/astro/.venv && \
    python3 -m venv /home/astro/.venv/cosmos && \
    /home/astro/.venv/cosmos/bin/python -m pip install --upgrade pip && \
    /home/astro/.venv/cosmos/bin/python -m pip install -q -r requirements-venv-cosmos.txt

# =============================================================================
# Airflow Environment Variables
# https://www.astronomer.io/docs/astro/environment-variables#environment-variable-priority
#
# Static defaults are set here (in the image) so the Terraform astro_deployment
# resource does not need the AWS provider to render them. Deployment-specific
# values (bucket paths, role ARNs, region, kafka bootstrap, tags, deployment
# name) are still set by Terraform via `environment_variables` and will
# override anything set here at runtime.
# =============================================================================

# --- Airflow 3.x backends (moved from TF; the v2-only local guards these) ---
ENV AIRFLOW__CORE__XCOM_BACKEND=airflow.providers.common.io.xcom.backend.XComObjectStorageBackend
ENV AIRFLOW__SECRETS__BACKEND=airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend

# --- Core / scheduler defaults ---
ENV DAG_IGNORE_FILE_SYNTAX=glob
# Astronomer sets a 24h grace period for code deploys; default task timeout is 1h.
ENV AIRFLOW__CORE__DEFAULT_TASK_EXECUTION_TIMEOUT=3600
# Prefer deferrable operators by default.
ENV AIRFLOW__OPERATORS__DEFAULT_DEFERRABLE=true

# --- XCom object storage (path/bucket set by TF) ---
ENV AIRFLOW__COMMON_IO__XCOM_OBJECTSTORAGE_COMPRESSION=zip
ENV AIRFLOW__COMMON_IO__XCOM_OBJECTSTORAGE_THRESHOLD=0

# --- Remote logging to S3 (bucket path set by TF) ---
ENV AIRFLOW__LOGGING__REMOTE_LOGGING=True
ENV AIRFLOW__LOGGING__REMOTE_LOG_CONN_ID=aws_s3_logs
ENV AIRFLOW__LOGGING__ENCRYPT_S3_LOGS=True
ENV AIRFLOW__ASTRO_SECONDARY_LOGS__S3_BUCKET_ENABLED=True

# --- Datadog (API key, tags, and site-specific overrides come from TF/cluster) ---
ENV DATADOG_SITE=datadoghq.com
ENV ASTRO_DATADOG_TASK_LOGS_ENABLED=true
ENV AIRFLOW__METRICS__STATSD_DATADOG_ENABLED=true

# --- Kafka static topology (bootstrap, oauth, sr set by TF from remote state) ---
ENV ASTRO__KAFKA__CA_CERT_LOCATION=/etc/ssl/certs/ca-certificates.crt
ENV ASTRO__KAFKA__EVENT_TOPIC=aa00002933.airflow-data.events
ENV ASTRO__KAFKA__DLQ_TOPIC=aa00002933.failed-data.events
