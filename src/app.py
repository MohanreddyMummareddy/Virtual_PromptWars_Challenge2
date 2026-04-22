from flask import Flask, render_template
import logging
import mimetypes
from src.config import Config
from src.services.llm_service import LLMService
from src.gcp_setup import check_and_enable_gcp_apis

# Fix for Windows registry sometimes assigning text/plain to .js files
mimetypes.add_type('application/javascript', '.js')

# Configure logging
logging.basicConfig(level=logging.INFO)

def create_app(config_class=Config):
    """Application Factory Pattern."""
    
    app = Flask(__name__, 
                static_folder='../static', 
                template_folder='../templates')
    
    app.config.from_object(config_class)

    # 1. Connect and Verify Google Services APIs (Local replication fallback included)
    check_and_enable_gcp_apis(app.config['GOOGLE_CLOUD_PROJECT'])

    # 2. Initialize Core LLM Service
    llm_service = LLMService(
        project_id=app.config['GOOGLE_CLOUD_PROJECT'],
        location=app.config['GOOGLE_CLOUD_LOCATION']
    )

    # Import and register Blueprints
    from src.routes.chat_routes import chat_bp, init_routes
    init_routes(llm_service)
    
    app.register_blueprint(chat_bp)

    @app.route('/')
    def index():
        # Secure headers (Security evaluation criteria)
        resp = app.make_response(render_template('index.html'))
        resp.headers['X-Content-Type-Options'] = 'nosniff'
        resp.headers['X-Frame-Options'] = 'DENY'
        return resp

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
