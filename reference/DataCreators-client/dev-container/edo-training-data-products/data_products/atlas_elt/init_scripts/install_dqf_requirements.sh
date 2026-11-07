#!/bin/sh
VOLUME_BASE="/Volumes/${DEFAULT_CATALOG}/${DEFAULT_SCHEMA}/dqf_libs"
CGREPO_PYPI="https://cgrepo.capgroup.com/repository/cgpypi/simple"

# Verify the Unity Catalog volume exists before proceeding
if [ ! -d "/Volumes/${DEFAULT_CATALOG}/${DEFAULT_SCHEMA}/dqf_libs" ]; then
    echo "ERROR: Volume ${DEFAULT_CATALOG}.${DEFAULT_SCHEMA}.dqf_libs does not exist."
    echo "ERROR: Please create it first, e.g.:"
    echo "  CREATE VOLUME ${DEFAULT_CATALOG}.${DEFAULT_SCHEMA}.dqf_libs;"
    exit 1
fi

# Ensure deequ jar is available on the volume
DEEQU_JAR="deequ-2.0.16-spark-3.5.jar"
DEEQU_URL="https://cgrepo.capgroup.com/repository/maven-central/com/amazon/deequ/deequ/2.0.16-spark-3.5/${DEEQU_JAR}"

if [ ! -f "${VOLUME_BASE}/${DEEQU_JAR}" ]; then
    echo "INFO: Deequ jar not found, downloading from cgrepo..."
    mkdir -p "${VOLUME_BASE}"
    curl -fSL -o "${VOLUME_BASE}/${DEEQU_JAR}" "${DEEQU_URL}"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to download deequ jar from cgrepo"
        exit 1
    fi
    echo "INFO: Deequ jar downloaded successfully"
else
    echo "INFO: Deequ jar already exists at ${VOLUME_BASE}/${DEEQU_JAR}"
fi

# Resolve dqf_requirements.txt with fallback for bundle sync paths
DQF_REQ="$PROJECT_HOME/dqf_requirements.txt"
if [ ! -f "$DQF_REQ" ]; then
    DQF_REQ="$PROJECT_HOME/data_products/atlas_elt/dqf_requirements.txt"
fi
if [ ! -f "$DQF_REQ" ]; then
    echo "ERROR: dqf_requirements.txt not found. Checked:"
    echo "  - $PROJECT_HOME/dqf_requirements.txt"
    echo "  - $PROJECT_HOME/data_products/atlas_elt/dqf_requirements.txt"
    exit 1
fi

# Ensure wheel files are available on the volume
WHEEL_DEST="${VOLUME_BASE}/wheelhouse"
MISSING_WHEELS=false

# Derive package names from requirements file (e.g. "caspian-core-libs==0.1.0" -> "caspian_core_libs")
while IFS= read -r line; do
    pkg=$(echo "${line}" | sed 's/[=<>!].*//' | tr '-' '_')
    [ -z "${pkg}" ] && continue
    if [ -z "$(ls ${WHEEL_DEST}/${pkg}-*.whl 2>/dev/null)" ]; then
        echo "INFO: Wheel for ${pkg} not found at ${WHEEL_DEST}"
        MISSING_WHEELS=true
    fi
done < "$DQF_REQ"

if [ "${MISSING_WHEELS}" = true ]; then
    echo "INFO: Downloading wheel files from cgrepo..."
    mkdir -p "${WHEEL_DEST}"
    pip download --no-deps -d "${WHEEL_DEST}" -r "$DQF_REQ" --extra-index-url "${CGREPO_PYPI}"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to download wheel files from cgrepo"
        exit 1
    fi
    echo "INFO: Wheel files downloaded successfully"
else
    echo "INFO: All wheel files already exist at ${WHEEL_DEST}"
fi

# Install from volume wheels, allowing transitive deps from cgrepo
pip install --find-links "${WHEEL_DEST}" --extra-index-url "${CGREPO_PYPI}" -r "$DQF_REQ"
PIP_INSTALLATION_STATUS=$?
echo "pip install status: ${PIP_INSTALLATION_STATUS}"
if [ "${PIP_INSTALLATION_STATUS}" -ne "0" ]; then
    echo "ERROR: DQF requirements installation FAILED"
    exit 1
else
    echo "INFO: DQF requirements installation SUCCESS"
fi
