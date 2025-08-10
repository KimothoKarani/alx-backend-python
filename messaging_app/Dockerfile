# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install any dependencies specified in requirements.txt
# Copy requirements.txt first to leverage Docker's layer caching.
# If requirements.txt doesn't change, this layer won't be rebuilt.
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project code into the container
# The '.' indicates the current directory (messaging_app) on the host
# and '/app' is the WORKDIR inside the container.
COPY . /app/

# Expose the port your Django app runs on
# Django's default development server port is 8000
EXPOSE 8000

# Define the command to run your Django application
# This command starts the Django development server, listening on all available network interfaces
# (0.0.0.0) and on port 8000.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]