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
    if not project_id or project_id == 'test-project':
        logger.info("[Local Replication] Skipping GCP API checks. Running in test mode.")
        return

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
        
        # Check if Vertex AI is enabled
        request = service.services().get(name=f"{project_name}/services/aiplatform.googleapis.com")
        response = request.execute()
        
        if response.get("state") == "ENABLED":
            logger.info("Vertex AI API (aiplatform.googleapis.com) is already ENABLED.")
        else:
            logger.warning("Vertex AI API is NOT ENABLED. Enabling now...")
            enable_req = service.services().enable(
                name=f"{project_name}/services/aiplatform.googleapis.com"
            )
            enable_req.execute()
            logger.info("Successfully enabled Vertex AI API.")

    except DefaultCredentialsError:
        logger.warning(
            "[Local Replication] No GCP credentials found locally. "
            "Simulating that Vertex AI APIs are verified so development can continue."
        )
    except google_exceptions.GoogleAPICallError as e:
        logger.error(f"Failed to communicate with GCP API: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during GCP setup: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    check_and_enable_gcp_apis(os.getenv("GOOGLE_CLOUD_PROJECT"))
