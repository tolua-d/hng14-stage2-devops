"""
Unit tests for api/main.py.

Redis is fully mocked via conftest.py (sys.modules stub), so no running
Redis instance is required.  All tests use FastAPI's TestClient.
"""
import sys
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Grab the mock instance that conftest.py installed
_redis_mock: MagicMock = sys.modules["redis"].Redis.return_value

# Import app AFTER the stub is in place
from .main import app  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_redis_mock():
    """Reset call history before every test so tests are independent."""
    _redis_mock.reset_mock()


# Test 1: Test Health Endpoint
def test_health_returns_ok():
    """GET /health must return 200 and {"status": "ok"} when Redis is up."""
    _redis_mock.ping.return_value = True

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_fails_when_redis_unavailable():
    """GET /health must return 503 when Redis is unreachable."""
    _redis_mock.ping.side_effect = Exception("Redis unreachable")

    response = client.get("/health")

    assert response.status_code == 503
    # Reset so later tests are not affected
    _redis_mock.ping.side_effect = None


# Test 2: Job creation
def test_create_job_returns_job_id():
    """POST /jobs must return a dict containing a non-empty job_id string."""
    response = client.post("/jobs")

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert isinstance(data["job_id"], str)
    assert len(data["job_id"]) > 0


def test_create_job_writes_to_redis():
    """POST /jobs must push the job onto the queue and set its initial status."""
    response = client.post("/jobs")
    job_id = response.json()["job_id"]

    # Verify the job was enqueued
    _redis_mock.lpush.assert_called_once_with("job", job_id)
    # Verify the initial status was recorded
    _redis_mock.hset.assert_called_once_with(f"job:{job_id}", "status", "queued")


# Test 3: Job status retrieval
def test_get_job_returns_status_when_found():
    """GET /jobs/{id} must return the job_id and its current status."""
    _redis_mock.hget.return_value = b"queued"

    response = client.get("/jobs/test-job-123")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "test-job-123"
    assert data["status"] == "queued"


def test_get_job_returns_404_when_not_found():
    """GET /jobs/{id} must return 404, not 200, when the job does not exist.

    BUG that was fixed: the original code returned 200 {"error": "not found"},
    making it impossible for callers to distinguish missing jobs by status code.
    """
    _redis_mock.hget.return_value = None

    response = client.get("/jobs/nonexistent-id")

    assert response.status_code == 404


def test_get_job_returns_completed_status():
    """GET /jobs/{id} correctly surfaces a completed status."""
    _redis_mock.hget.return_value = b"completed"

    response = client.get("/jobs/done-job-456")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
