from flask import Blueprint, request, jsonify, current_app
import html
import logging

# Create blueprint
chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    llm_service = getattr(current_app, 'llm_service', None)
    if llm_service is None:
        return jsonify({"error": "AI Service is not initialized. Check server logs."}), 503

    data = request.json
    user_message = data.get('message', '').strip()
    context = data.get('context', '').strip()
    language = data.get('language', 'English').strip()
    
    # Validate input (Must match test expectations in test_api.py)
    if not user_message or len(user_message) > 1000:
        return jsonify({"error": "Message body cannot be empty and must be under 1000 characters."}), 400

    # Basic input sanitation (evaluation requirement)
    clean_message = html.escape(user_message)
    clean_context = html.escape(context)
    
    try:
        response_text = llm_service.get_chat_response(clean_message, clean_context, language)
        return jsonify({"response": response_text}), 200
    except Exception as e:
        logger.error(f"Chat API Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
