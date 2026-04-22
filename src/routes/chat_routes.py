from flask import Blueprint, request, jsonify
from src.services.llm_service import LLMService
import html

# Create blueprint
chat_bp = Blueprint('chat', __name__)

# This will be injected by the app factory
llm_service: LLMService = None

def init_routes(service: LLMService):
    global llm_service
    llm_service = service

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.json
    user_message = data.get('message', '').strip()
    context = data.get('context', '').strip()
    
    if not user_message:
        return jsonify({"error": "Message body cannot be empty"}), 400

    # Basic input sanitation (evaluation requirement)
    clean_message = html.escape(user_message)
    clean_context = html.escape(context)
    
    try:
        response_text = llm_service.get_chat_response(clean_message, clean_context)
        return jsonify({"response": response_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
