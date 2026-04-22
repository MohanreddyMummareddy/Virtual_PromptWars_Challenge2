import pytest
from unittest.mock import patch, MagicMock
from src.services.llm_service import LLMService

class TestLLMService:

    def test_mock_response_when_test_project_used(self):
        # Action (using test-project)
        service = LLMService(project_id="test-project", location="us-central1")
        
        # Assert
        resp = service.get_chat_response("How do I register?", "Stop 1: Registration")
        assert "mock response" in resp.lower()
        assert service.model is None
