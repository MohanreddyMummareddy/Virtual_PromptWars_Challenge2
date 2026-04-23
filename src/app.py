from flask import Flask, render_template, send_file, jsonify
import os
import logging
import mimetypes
from src.config import Config
from src.services.llm_service import LLMService
from src.gcp_setup import check_and_enable_gcp_apis

# Fix for browser mime-type issues
mimetypes.add_type('application/javascript', '.js')

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()]
)

def create_app(config_class=Config):
    """Application Factory Pattern."""
    # Dynamically resolve paths relative to this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, '..', 'static')
    template_dir = os.path.join(base_dir, '..', 'templates')
    
    app = Flask(__name__,
                static_folder=static_dir,
                template_folder=template_dir)
    
    app.config.from_object(config_class)

    # Ensure critical GCP configs are pulled from environment if not in Config object
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT') or app.config.get('GOOGLE_CLOUD_PROJECT')
    location = app.config.get('GOOGLE_CLOUD_LOCATION') or os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

    if not project_id:
        raise RuntimeError("GOOGLE_CLOUD_PROJECT not detected. Active Cloud Shell session required.")

    # 1. Connect and Verify Google Services APIs
    check_and_enable_gcp_apis(project_id)

    # 2. Initialize Core LLM Service
    llm_service = LLMService(
        project_id=project_id,
        location=location
    )

    # Import and register Blueprints
    from src.routes.chat_routes import chat_bp, init_routes
    init_routes(llm_service)
    
    app.register_blueprint(chat_bp)

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        app.logger.debug("Security headers applied to response")
        return response

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/system/health')
    def health_check():
        """Endpoint to verify the server is reachable."""
        return jsonify({"status": "healthy", "message": "Civic Journey Backend is live"}), 200

    @app.route('/api/system/logs')
    def get_server_logs():
        """Endpoint to download the server-side log file."""
        try:
            if not os.path.exists(log_file):
                return "Log file not yet created.", 404
            return send_file(log_file, as_attachment=True, download_name='server_logs.log')
        except Exception as e:
            logging.error(f"Failed to serve logs: {e}")
            return f"Error retrieving logs: {str(e)}", 500

    return app

if __name__ == '__main__':
    app = create_app()
    # Default to 8080 for seamless Cloud Shell Web Preview
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
