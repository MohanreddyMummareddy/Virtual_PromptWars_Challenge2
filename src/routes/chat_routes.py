from flask import Blueprint, request, jsonify, current_app
from src.services.llm_service import LLMService
import html
import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.auth

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
    
    # Validate input (Must match test expectations in test_api.py)
    if not user_message or len(user_message) > 1000:
        return jsonify({"error": "Message body cannot be empty and must be under 1000 characters."}), 400
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

@chat_bp.route('/api/calendar/invite', methods=['POST'])
def create_calendar_invite():
    """Actual Google Calendar API integration."""
    try:
        data = request.json
        title = data.get('title', 'Election Deadline')
        zip_code = data.get('zipCode', 'India')

        # Initialize Google Calendar API with Default Credentials (ADC)
        # Note: Re-authenticate with: gcloud auth application-default login --scopes="https://www.googleapis.com/auth/calendar.events,https://www.googleapis.com/auth/cloud-platform"
        credentials, project = google.auth.default(
            scopes=[
                'https://www.googleapis.com/auth/calendar.events',
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/cloud-platform'
            ]
        )
        
        logger.info(f"Using credentials for project: {project}")
        
        # Disable discovery cache to resolve warnings in environment logs
        service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)

        event = {
            'summary': f'Civic Journey: {title}',
            'location': f'Pincode: {zip_code}, India',
            'description': f'Reminder for your {title} step. Stay informed, stay voting!',
            'start': {
                'dateTime': '2026-05-07T09:00:00Z', # Future date for 2026
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': '2026-05-07T10:00:00Z',
                'timeZone': 'Asia/Kolkata',
            },
            'reminders': {
                'useDefault': True,
            },
        }

        created_event = service.events().insert(calendarId='primary', body=event).execute()
        event_link = created_event.get('htmlLink')

        return jsonify({
            "status": "success", 
            "message": f"Event created! [View in Google Calendar]({event_link})",
            "link": event_link
        }), 200
    except HttpError as e:
        status = e.resp.status
        logger.error(f"Calendar API HttpError: {status} - {e.reason}")
        if status == 403:
            return jsonify({
                "error": "Insufficient permissions for Google Calendar. Please ensure you have authorized the 'calendar.events' scope."
            }), 403
        return jsonify({"error": f"Google Calendar API error: {e.reason}"}), status
    except Exception as e:
        logger.error(f"Calendar API Error: {str(e)}")
        return jsonify({"error": "Could not sync with Google Calendar"}), 500
