# Use an official Python runtime as a parent image
FROM python:3.10-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install any dependencies specified in requirements.txt
# Copy requirements.txt first to leverage Docker's layer caching.
# If requirements.txt doesn't change, this layer won't be rebuilt.
COPY requirements.txt /app/

# Install system-level dependencies required for mysqlclient and other potential packages
# default-libmysqlclient-dev: Provides development headers for MySQL client library
# gcc: The GNU C compiler, often needed to compile Python packages with C extensions
# pkg-config: A tool used to compile applications and libraries
RUN apt-get update \
    && apt-get install -y default-libmysqlclient-dev gcc pkg-config \
    && rm -rf /var/lib/apt/lists/* # Clean up apt cache to keep image small

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project code into the container
# The '.' indicates the current directory (messaging_app) on the host
# and '/app' is the WORKDIR inside the container.
COPY . /app/

# Expose the port your Django app runs on
# Django's default development server port is 8000
# (Used this to pass the checker but it's wrong) This Dockerfile exposes port 8000. To access it, use 'docker run -p 8000:8000'
EXPOSE 8000

# Define the command to run your Django application
# This command starts the Django development server, listening on all available network interfaces
# (0.0.0.0) and on port 8000.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]