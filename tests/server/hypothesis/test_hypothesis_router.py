"""Test hypothesis router."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock

from private_gpt.server.hypothesis.hypothesis_router import hypothesis_router, GenerateBody, UpdateStatusBody


@pytest.fixture
def mock_hypothesis_component():
    """Mock hypothesis component."""
    mock = Mock()
    mock.generate.return_value = Mock(id="test_id", status="pending")
    mock.list.return_value = [Mock(id="test_id", status="pending")]
    mock.update_status.return_value = Mock(id="test_id", status="done")
    mock.clear.return_value = None
    return mock


@pytest.fixture
def test_client(mock_hypothesis_component):
    """Test client with mocked dependencies."""
    from fastapi import FastAPI
    from private_gpt.server.utils.auth import authenticated
    
    app = FastAPI()
    
    # Mock the authenticated dependency
    def mock_authenticated():
        return True
    
    app.dependency_overrides[authenticated] = mock_authenticated
    
    # Mock the injector
    def mock_injector():
        return MagicMock(get=lambda x: mock_hypothesis_component)
    
    app.dependency_overrides[authenticated] = mock_injector
    
    app.include_router(hypothesis_router)
    
    with TestClient(app) as client:
        yield client


def test_generate_hypothesis(test_client, mock_hypothesis_component):
    """Test hypothesis generation endpoint."""
    body = GenerateBody(
        last_user_message="Test message",
        assistant_response="Test response",
        top_memory_limit=5,
        tags=["test"]
    )
    
    response = test_client.post("/v1/hypothesis/generate", json=body.dict())
    assert response.status_code == 200
    mock_hypothesis_component.generate.assert_called_once()


def test_list_hypotheses(test_client, mock_hypothesis_component):
    """Test hypothesis listing endpoint."""
    response = test_client.get("/v1/hypothesis/list?limit=10")
    assert response.status_code == 200
    mock_hypothesis_component.list.assert_called_once_with(limit=10)


def test_update_status(test_client, mock_hypothesis_component):
    """Test hypothesis status update endpoint."""
    body = UpdateStatusBody(id="test_id", status="done")
    
    response = test_client.post("/v1/hypothesis/update_status", json=body.dict())
    assert response.status_code == 200
    mock_hypothesis_component.update_status.assert_called_once_with(hyp_id="test_id", status="done")


def test_clear_hypotheses(test_client, mock_hypothesis_component):
    """Test hypothesis clearing endpoint."""
    response = test_client.post("/v1/hypothesis/clear")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_hypothesis_component.clear.assert_called_once()
