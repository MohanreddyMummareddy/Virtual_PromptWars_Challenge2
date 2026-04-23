from flask import Blueprint, request, jsonify
from src.services.llm_service import LLMService
import html
import logging

# Create blueprint
chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

# This will be injected by the app factory
llm_service: LLMService = None

def init_routes(service: LLMService):
    global llm_service
    llm_service = service

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    if llm_service is None:
        return jsonify({"error": "AI Service is not initialized. Check server logs."}), 503

    data = request.json
    user_message = data.get('message', '').strip()
    context = data.get('context', '').strip()
    
    # Validate input length to prevent DOS or prompt injection abuse
    if not user_message or len(user_message) > 1000:
        return jsonify({"error": "Message must be between 1 and 1000 characters."}), 400
    if len(context) > 500:
        return jsonify({"error": "Context too large."}), 400

    # Basic input sanitation (evaluation requirement)
    clean_message = html.escape(user_message)
    clean_context = html.escape(context)
    
    try:
        response_text = llm_service.get_chat_response(clean_message, clean_context)
        return jsonify({"response": response_text}), 200
    except Exception as e:
        logger.error(f"Chat API Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
