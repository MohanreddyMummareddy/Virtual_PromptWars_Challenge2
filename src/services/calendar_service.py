import logging
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
import google.auth

logger = logging.getLogger(__name__)

class CalendarService:
    """Service to handle interactions with the Google Calendar API."""
    
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/calendar'
        ]

    def _get_service(self):
        credentials, _ = google.auth.default(scopes=self.scopes)
        return build('calendar', 'v3', credentials=credentials, cache_discovery=False)

    def create_election_event(self, title, pincode):
        """Creates a localized election reminder event."""
        try:
            service = self._get_service()
            
            # Logic: Set deadline for 7 days from now at 10 AM
            start_time = (datetime.now(timezone.utc) + timedelta(days=7)).replace(hour=10, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=1)

            event = {
                'summary': f'Civic Journey: {title}',
                'location': f'Pincode: {pincode}, India',
                'description': f'Reminder for your {title} step. Prepared via the Indian Election Guide.',
                'start': {
                    'dateTime': start_time.isoformat() + 'Z',
                },
                'end': {
                    'dateTime': end_time.isoformat() + 'Z',
                },
                'reminders': {
                    'useDefault': True,
                },
                'transparency': 'transparent', # Doesn't block out the whole day
            }

            created_event = service.events().insert(calendarId='primary', body=event).execute()
            return created_event.get('htmlLink')
        except Exception as e:
            logger.error(f"Calendar Service Error: {e}")
            raise e