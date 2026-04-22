# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables for Flask
ENV FLASK_APP=src.app:create_app()
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=True

# Expose port 8080 (Cloud Run's default port)
EXPOSE 8080

# Run waitress as the production WSGI server
CMD ["waitress-serve", "--port=8080", "--call", "src.app:create_app"]
