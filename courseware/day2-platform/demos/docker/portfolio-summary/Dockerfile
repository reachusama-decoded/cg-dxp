# Start from a small official Python base image (Python 3.11 on slim Debian).
FROM python:3.11-slim

# Everything below runs relative to /app inside the image.
WORKDIR /app

# Copy the app (summarize.py + holdings.csv) into the working directory.
COPY app/ ./

# Run the summary script when the container starts.
CMD ["python", "summarize.py"]