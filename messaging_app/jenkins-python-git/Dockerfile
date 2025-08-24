FROM python:3.12-slim

# Install git (no recommends keeps the image smaller)
RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/*