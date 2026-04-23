import os
import logging
from google.api_core import exceptions as google_exceptions
from google.auth.exceptions import DefaultCredentialsError

logger = logging.getLogger(__name__)

def check_and_enable_gcp_apis(project_id: str):
    """
    Connects to GCP to check if required APIs (like Vertex AI) are enabled.
    If running locally without credentials, gracefully replicates the behavior.
    """
    REQUIRED_APIS = [
        "aiplatform.googleapis.com",      # Vertex AI
        "calendar-json.googleapis.com",   # Google Calendar
        "maps-backend.googleapis.com"     # Google Maps
    ]

    if not project_id:
        raise ValueError("Project ID is required to enable GCP APIs.")

    try:
        import google.auth
        from googleapiclient.discovery import build
        
        credentials, active_project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        
        logger.info(f"Successfully connected to GCP. Verifying APIs for project: {project_id}...")
        
        # Build the Service Usage API Client
        service = build('serviceusage', 'v1', credentials=credentials)
        project_name = f"projects/{project_id}"
        
        for api in REQUIRED_APIS:
            request = service.services().get(name=f"{project_name}/services/{api}")
            response = request.execute()
            
            if response.get("state") == "ENABLED":
                logger.info(f"API {api} is already ENABLED.")
            else:
                logger.warning(f"API {api} is NOT ENABLED. Enabling now...")
                enable_req = service.services().enable(
                    name=f"{project_name}/services/{api}"
                )
                enable_req.execute()
                logger.info(f"Successfully enabled {api}.")

    except DefaultCredentialsError:
        logger.error("No GCP credentials found. Ensure you are logged into Cloud Shell.")
    except google_exceptions.GoogleAPICallError as e:
        logger.error(f"Failed to communicate with GCP API: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during GCP setup: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    check_and_enable_gcp_apis(os.getenv("GOOGLE_CLOUD_PROJECT"))
