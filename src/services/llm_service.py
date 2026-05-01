import os
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are the 'Indian Election Tour Guide', an expert on the Election Commission of India (ECI) procedures. "
    "The user is navigating a subway-style journey map for the Indian General Elections. "
    "Your goal is to guide them through Voter Registration (Form 6), Electoral Roll searching, KYC of candidates, and EVM/VVPAT procedures. "
    "Keep your answers friendly, extremely concise (1-2 short paragraphs max), and actionable. "
    "Use Indian terminology: Pincode instead of Zip code, EPIC card instead of Voter ID, and Polling Booth instead of Polling Place."
)

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
            if not self.project_id or self.project_id == "test-project":
                logger.warning("Using Mock LLM Mode. Vertex AI will not be called.")
                self.model = None
                return

            import vertexai
            from vertexai.generative_models import GenerativeModel, GenerationConfig, HarmCategory, HarmBlockThreshold
            vertexai.init(project=self.project_id, location=self.location)
            
            # Production-Grade Configuration
            self.generation_config = GenerationConfig(
                temperature=0.2,
                top_p=0.8,
                top_k=40,
                max_output_tokens=512,
            )
            
            self.safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }

            self.model = GenerativeModel("gemini-1.5-flash")
            logger.info(f"Initialized Vertex AI for project: {self.project_id}")
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise RuntimeError(f"Failed to initialize Vertex AI: {e}")

    @lru_cache(maxsize=100)
    def get_chat_response(self, user_message: str, user_context: str) -> str:
        """Fetch chat response from the Model."""
        # Fallback for Testing/Mocking
        if not self.model:
            return f"[MOCK RESPONSE] To register for the Indian Elections, use Form 6 on the Voter Service Portal. Context: {user_context}"
            
        full_prompt = f"System Context: {SYSTEM_PROMPT}\nUser App Context: {user_context}\n\nUser: {user_message}\nCivic Guide:"

        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            return response.text
        except Exception as e:
            logger.error(f"API Call Failed: {e}")
            raise e
