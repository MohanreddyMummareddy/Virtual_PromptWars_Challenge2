import os
import logging

logger = logging.getLogger(__name__)

class LLMService:
    """Service to handle interactions with the LLM (Vertex AI or Gemini API)."""
    
    def __init__(self, project_id, location):
        self.project_id = project_id
        self.location = location
        self.model = None
        self.is_vertex = True
        self._initialize_model()

    def _initialize_model(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if api_key:
            # Bypass Vertex AI and use standard simple API key (for local without gcloud CLI)
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.is_vertex = False
            logger.info("Initialized Gemini with Developer API Key.")
            return

        try:
            if self.project_id and self.project_id != 'test-project':
                import vertexai
                from vertexai.generative_models import GenerativeModel
                vertexai.init(project=self.project_id, location=self.location)
                self.model = GenerativeModel("gemini-1.5-flash")
                logger.info(f"Initialized Vertex AI for project: {self.project_id}")
            else:
                logger.warning("No valid GOOGLE_CLOUD_PROJECT found. Model running in mock mode.")
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            self.model = None

    def get_chat_response(self, user_message: str, user_context: str) -> str:
        """Fetch chat response from the Model."""
        if not self.model:
            return "This is a mock response because the LLMService is running without valid Google Cloud credentials or testing mode."
            
        system_prompt = (
            "You are the 'Civic Guide', an interactive assistant for the election process. "
            "Keep your answers friendly, extremely concise (1-2 short paragraphs max), and actionable. "
            "Help the user understand the specific step they are on in the voting journey."
        )
        
        full_prompt = f"System Context: {system_prompt}\nUser App Context: {user_context}\n\nUser: {user_message}\nCivic Guide:"

        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.warning(f"Failed to reach Google Services (likely missing credentials). Replicating locally: {e}")
            # Mocked local replication to unblock development
            return f"**[Local Mock Mode]** I see you are asking about the {user_context}. Here is a simulated response designed to keep your development flowing without hitting the actual Google APIs!"
