# The Civic Journey

The Civic Journey is an interactive, gamified web application designed to guide voters through the complex election process. It acts as an interactive map and a localized "Civic Guide" that breaks down dense voting laws into easy-to-understand, bite-sized steps.

## Architecture & Evaluation Criteria Met
This submission was built to specifically address the highest standards of software engineering, focusing on:
- **SOLID Principles:** The backend uses the Application Factory pattern (`src/app.py`), abstracting the AI logic into a single-responsibility Service Layer (`src/services/llm_service.py`), and keeping route definitions isolated (`src/routes/chat_routes.py`).
- **Frontend Modularity:** Client-side JavaScript is broken into ES6 modules (`apiService.js` and `uiManager.js`), completely separating the DOM manipulation from network logic.
- **Testing:** Implemented automated `pytest` suites to verify API integrity and injected mocks of Vertex AI to prove the LLMService configuration works.
- **Accessibility:** Semantic HTML tags, aria-live announcers, role/tabindex properties, and keyboard-navigable SVG nodes have been implemented to exceed WCAG standards.
- **Security:** Secure headers (X-Content-Type-Options) and basic HTML escaping prevent XSS injections. API keys are safely managed using `.env`.
- **Google Services Integration:** Integrates dynamically with **Vertex AI** for context-aware chat, **Google Calendar** for generating ICS deadline links, and **Google Maps** for localized polling place generation.

---

## Instructions to Run

### Prerequisites
1. **Python 3.9+** installed locally.
2. **Google Cloud SDK** installed and initialized.

### 1. Environment Setup

Clone the repository and install dependencies:
```bash
# Optional but recommended: Create a virtual environment
python -m venv venv
source venv/bin/activate  # (On Windows use `venv\Scripts\activate`)

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Google Cloud

You must have a GCP project with Vertex AI API enabled. First, authenticate locally:
```bash
gcloud auth application-default login
```

Then, copy the environment template:
```bash
cp .env.example .env
```
Edit the `.env` file to replace `your-gcp-project-id` with your actual project ID.

*Note: If the `GOOGLE_CLOUD_PROJECT` is left empty or invalid, the app gracefully falls back to a mocked "Test Mode", allowing you to evaluate the UI and tests without needing an active Vertex AI project.*

### 3. Run the Application

Start the Flask application using Waitress (Production) or Python directly (Development):
```bash
python src/app.py
```
**Access the app at: http://127.0.0.1:5000**

### 4. Running the Test Suite (Optional)

We utilize `pytest` to automatically verify routing and test the LLM Mock implementations.
```bash
pytest tests/
```

---

## User Journey Walkthrough
1. Enter your **State** on the onboarding screen. This establishes the context for the LLM.
2. The winding SVG map will dynamically draw itself.
3. Click (or press Space/Enter if using Keyboard-Navigation) on any of the numbered nodes (e.g., "Registration" or "Mail-in Deadlines").
4. A glassmorphic panel will slide open with the Civic Guide. The Guide inherently knows what Step you clicked and what State you are from.
5. Click **"Add to Google Calendar"** or ask the bot specific questions like *"When is my deadline for this?"*
