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
        try:
            if not self.project_id:
                logger.error("No Google Cloud Project ID provided for Vertex AI.")
                return

            import vertexai
            from vertexai.generative_models import GenerativeModel
            vertexai.init(project=self.project_id, location=self.location)
            self.model = GenerativeModel("gemini-2.5-flash")
            logger.info(f"Initialized Vertex AI for project: {self.project_id}")
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise RuntimeError(f"Failed to initialize Vertex AI: {e}")

    def get_chat_response(self, user_message: str, user_context: str) -> str:
        """Fetch chat response from the Model."""
        if not self.model:
            raise ValueError("LLM Model is not initialized.")
            
        system_prompt = (
            "You are the 'Indian Election Tour Guide', an expert on the Election Commission of India (ECI) procedures. "
            "The user is navigating a subway-style journey map for the Indian General Elections. "
            "Your goal is to guide them through Voter Registration (Form 6), Electoral Roll searching, KYC of candidates, and EVM/VVPAT procedures. "
            "Keep your answers friendly, extremely concise (1-2 short paragraphs max), and actionable. "
            "Use Indian terminology: Pincode instead of Zip code, EPIC card instead of Voter ID, and Polling Booth instead of Polling Place."
        )
        
        full_prompt = f"System Context: {system_prompt}\nUser App Context: {user_context}\n\nUser: {user_message}\nCivic Guide:"

        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"API Call Failed: {e}")
            raise e
