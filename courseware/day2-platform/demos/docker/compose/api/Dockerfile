# The API's image: the four-instruction shape of Challenge 7, plus a RUN to install the one dependency and a USER
# so the process does not run as root. Comments sit on their own lines: Docker reads `#` only at the start of a line.

# The base layer: the same image as portfolio-summary, so it is already on this laptop.
FROM python:3.11-slim

# Every instruction below runs here.
WORKDIR /app

# The dependency list first, on its own layer: editing app.py later does not reinstall it.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# The application last: the layer that changes most often goes nearest the bottom.
COPY app.py ./

# A non-root user, and run as it: a compromised process gets a user's rights, not root's.
RUN useradd --create-home api
USER api

# Documentation only: the port the app listens on. The `ports:` line in docker-compose.yml does the publishing.
EXPOSE 8000

# What runs when the container starts.
CMD ["python", "app.py"]
