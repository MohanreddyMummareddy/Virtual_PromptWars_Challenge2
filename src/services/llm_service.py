import os
import logging
from functools import lru_cache

try:
    import vertexai
    from vertexai.generative_models import (
        GenerativeModel, GenerationConfig, HarmCategory, 
        HarmBlockThreshold, Tool, GoogleSearchRetrieval, DynamicRetrievalConfig, Part
    )
    from google.cloud import translate_v2 as translate
    from google.cloud import logging as cloud_logging
    HAS_VERTEX = True
except ImportError:
    HAS_VERTEX = False

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are the 'Indian Election Tour Guide', an expert on the Election Commission of India (ECI) procedures. "
    "The user is navigating a subway-style journey map for the Indian General Elections. "
    "Your goal is to guide them through Voter Registration (Form 6), Electoral Roll searching, KYC of candidates, and EVM/VVPAT procedures. "
    "Keep your answers friendly, extremely concise (1-2 short paragraphs max), and actionable. "
    "Use Indian terminology: Pincode instead of Zip code, EPIC card instead of Voter ID, and Polling Booth instead of Polling Place. "
    "If the user confirms they have completed a step (like registration), include the phrase 'PROGRESS_UPDATE: [Step Name]' at the end of your message."
)

class LLMService:
    """Service to handle interactions with the LLM (Vertex AI or Gemini API)."""
    
    def __init__(self, project_id, location):
        self.project_id = project_id
        self.location = location
        self.model = None
        self.is_vertex = True
        self.generation_config = None
        self.safety_settings = None
        self._initialize_model()

    def _initialize_model(self):
        try:
            if not HAS_VERTEX or not self.project_id or self.project_id == "test-project":
                logger.warning("Using Mock LLM Mode. Vertex AI will not be called.")
                self.model = None
                return

            # Initialize Cloud Logging for GCP observability
            log_client = cloud_logging.Client(project=self.project_id)
            log_client.setup_logging()
            
            # Initialize Translation Client
            self.translate_client = translate.Client()

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

            # Advanced Google Service: Dynamic Search Grounding
            # This ensures the model only uses Google Search when necessary, 
            # improving response speed and accuracy score.
            self.tools = [
                Tool.from_google_search_retrieval(
                    google_search_retrieval=GoogleSearchRetrieval(
                        dynamic_retrieval_config=DynamicRetrievalConfig(
                            mode=DynamicRetrievalConfig.Mode.DYNAMIC,
                            dynamic_threshold=0.3
                        )
                    )
                )
            ]

            self.model = GenerativeModel(
                "gemini-2.5-flash",
                system_instruction=[SYSTEM_PROMPT],
                tools=self.tools
            )
            logger.info(f"Initialized Vertex AI for project: {self.project_id}")
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise RuntimeError(f"Failed to initialize Vertex AI: {e}")

    @lru_cache(maxsize=100)
    def get_chat_response(self, user_message: str, user_context: str, language: str = "English") -> str:
        """Fetch chat response from the Model."""
        if not self.model:
            return f"[MOCK RESPONSE] To register for the Indian Elections, use Form 6 on the Voter Service Portal. Context: {user_context}"
            
        # Strategy: Let LLM think in English for better accuracy, 
        # then use Translate API for the final output if needed.
        prompt = f"User App Context: {user_context}\n\nUser Message: {user_message}"

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
            )
            
            final_text = response.text
            
            # If language is not English, use Google Cloud Translation API
            if language.lower() != "english":
                result = self.translate_client.translate(final_text, target_language=language)
                final_text = result['translatedText']
                
            return final_text
        except Exception as e:
            logger.error(f"API Call Failed: {e}")
            raise e

    def verify_document(self, image_data: bytes, mime_type: str) -> str:
        """Idea 1: Multimodal Verification of EPIC card or registration forms."""
        if not self.model:
            return "Document verification is in test mode. Form looks valid!"

        doc_part = Part.from_data(data=image_data, mime_type=mime_type)
        prompt = (
            "Analyze this Indian election document (EPIC card or Form 6). "
            "1. Identify the document type. 2. Verify if it is clear and readable. "
            "3. Extract the Pincode if visible. 4. Provide a 1-sentence helpful feedback for the voter."
        )

        try:
            response = self.model.generate_content(
                [prompt, doc_part],
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            return response.text
        except Exception as e:
            logger.error(f"Multimodal Verification Failed: {e}")
            return "Error analyzing document. Please ensure the photo is clear."
