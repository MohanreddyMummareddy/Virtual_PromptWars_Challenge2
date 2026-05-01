FROM python:3.11-slim

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
# Note: Ensure gunicorn is added to your requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup.
# We use gunicorn as the production-grade WSGI server.
# Timeout is set to 0 to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 "src.app:create_app()"