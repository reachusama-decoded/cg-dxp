FROM python:3.11-slim AS base
WORKDIR /app
FROM base AS test
COPY app/ ./
RUN python test_summary.py
CMD ["python", "test_summary.py"]
FROM base AS runtime
RUN useradd --uid 10001 --create-home learner
COPY --from=test --chown=10001:10001 /app/summarize.py /app/holdings.csv ./
USER 10001
CMD ["python", "summarize.py"]
