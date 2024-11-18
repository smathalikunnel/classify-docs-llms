# Use the official Python image from the Docker Hub
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies for pdf2image, including poppler-utils
RUN apt-get update && apt-get install -y poppler-utils

# Copy requirements.txt first to leverage Docker cache for dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Set environment variables to run Flask
ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production

# Expose the port that the Flask app runs on
EXPOSE 5001

# Run the Flask application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5001", "src.app:app"]
