#!/bin/sh
# Bootstrap CA trust for outbound HTTPS from dbt/requests on cluster nodes.
CA_SOURCE="${PROJECT_HOME}/data_products/atlas_elt/init_scripts/certs/cacert.pem"
if [ ! -f "$CA_SOURCE" ]; then
    CA_SOURCE="${PROJECT_HOME}/init_scripts/certs/cacert.pem"
fi

if [ -f "$CA_SOURCE" ]; then
    mkdir -p /usr/local/share/ca-certificates
    cp "$CA_SOURCE" /usr/local/share/ca-certificates/cg-custom-ca.crt
    update-ca-certificates || true
fi

export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
export CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
export GIT_SSL_CAINFO=/etc/ssl/certs/ca-certificates.crt

# Protect the Databricks-provided psutil binary from being overwritten by pip.
# DBR ships a custom psutil build; reinstalling from PyPI breaks PySpark.
PSUTIL_VERSION=$(python3 -c "import psutil; print(psutil.__version__)" 2>/dev/null)
if [ -n "$PSUTIL_VERSION" ]; then
    echo "psutil==$PSUTIL_VERSION" > /tmp/psutil_constraint.txt
    CONSTRAINT_FLAG="-c /tmp/psutil_constraint.txt"
fi

REQUIREMENTS_FILE="$PROJECT_HOME/requirements.txt"
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    REQUIREMENTS_FILE="$PROJECT_HOME/data_products/atlas_elt/requirements.txt"
fi

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "ERROR: requirements.txt not found. Checked:"
    echo "  - $PROJECT_HOME/requirements.txt"
    echo "  - $PROJECT_HOME/data_products/atlas_elt/requirements.txt"
    exit 1
fi

pip install -r "$REQUIREMENTS_FILE" ${CONSTRAINT_FLAG:-} --find-links "$PROJECT_HOME/wheelhouse/" --extra-index-url https://cgrepo-aws.capgroup.com/repository/cgpypi/simple
PIP_INSTALLATION_STATUS=$?
echo "pip install status: ${PIP_INSTALLATION_STATUS}"
if [ "${PIP_INSTALLATION_STATUS}" -ne "0" ]; then
    echo "ERROR: Requirements installation FAILED"
    exit 1
else
    echo "INFO: Requirements installation SUCCESS"
fi
