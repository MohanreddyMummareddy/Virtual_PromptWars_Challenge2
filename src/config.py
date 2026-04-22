import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
    GOOGLE_CLOUD_LOCATION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
    TESTING = False

class TestConfig(Config):
    """Testing configuration."""
    TESTING = True
    GOOGLE_CLOUD_PROJECT = 'test-project'
