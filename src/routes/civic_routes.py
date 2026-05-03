from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)
civic_bp = Blueprint('civic', __name__)

@civic_bp.route('/api/calendar/invite', methods=['POST'])
def create_calendar_event():
    """Endpoint to trigger Google Calendar API event creation."""
    data = request.json
    title = data.get('title')
    pincode = data.get('pincode')
    
    try:
        link = current_app.calendar_service.create_election_event(title, pincode)
        return jsonify({"link": link}), 200
    except Exception as e:
        logger.error(f"Route error creating calendar event: {e}")
        return jsonify({"error": str(e)}), 500

@civic_bp.route('/api/verify-document', methods=['POST'])
def verify_document():
    """Endpoint for Multimodal document analysis via Gemini."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    image_data = file.read()
    mime_type = file.content_type
    
    try:
        analysis = current_app.llm_service.verify_document(image_data, mime_type)
        return jsonify({"analysis": analysis}), 200
    except Exception as e:
        logger.error(f"Route error verifying document: {e}")
        return jsonify({"error": "Verification failed"}), 500

@civic_bp.route('/api/wallet/generate', methods=['POST'])
def generate_wallet_pass():
    """Endpoint to generate a Google Wallet Civic Pass."""
    data = request.json
    pincode = data.get('pincode')
    user_id = "USER_123" # In a real app, this would come from session
    
    try:
        url = current_app.wallet_service.create_civic_pass(user_id, pincode)
        if url:
            return jsonify({"url": url}), 200
        return jsonify({"error": "Failed to generate pass"}), 500
    except Exception as e:
        logger.error(f"Route error generating wallet pass: {e}")
        return jsonify({"error": str(e)}), 500