# Same image family as the learners' container (astro-runtime 3.1-17-base = Airflow 3.1.8,
# Python 3.12), same split: Airflow providers in the base environment, dbt in its own venv
# at /home/astro/.venv/cosmos so Cosmos finds it at the same path.
FROM quay.io/astronomer/astro-runtime:3.1-17-base

USER root
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

USER astro
COPY requirements-venv-cosmos.txt /tmp/requirements-venv-cosmos.txt
RUN python3 -m venv /home/astro/.venv/cosmos \
    && /home/astro/.venv/cosmos/bin/python -m pip install --no-cache-dir --upgrade pip \
    && /home/astro/.venv/cosmos/bin/python -m pip install --no-cache-dir -r /tmp/requirements-venv-cosmos.txt
