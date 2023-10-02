# Use a slim Python base image
FROM python:3.8-slim

# Install curl
RUN apt-get update && apt-get install -y curl

# Set the working directory inside the container
WORKDIR /app

# Copy the directory structure into the container's working directory
COPY . .

# Copy env
COPY .env .env

# Install dependencies
RUN pip install -r requirements.txt

# Set the environment variable for Flask
ENV FLASK_APP=leanix_description/ld.py

# Expose the port on which Flask will run (default is 5000)
EXPOSE 5000

# Start the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]
