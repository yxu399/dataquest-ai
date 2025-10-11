"""
API Response Time Benchmarks
Tests the response times of all API endpoints
"""

import pytest
import os
import sys
import tempfile
import io
from datetime import datetime
from fastapi.testclient import TestClient

# Add backend root to Python path
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_root)

from app.core.database import SessionLocal, engine, Base
from app.models.database import Analysis


# Test fixtures
@pytest.fixture(scope="session")
def test_db():
    """Create test database tables"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Provide a database session for tests"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(test_db):
    """FastAPI test client"""
    from main import app

    return TestClient(app)


@pytest.fixture
def sample_csv_content():
    """Create sample CSV content"""
    csv_data = """id,name,category,value,quantity
1,Item 1,A,10.5,5
2,Item 2,B,20.3,10
3,Item 3,A,15.8,7
4,Item 4,C,30.2,12
5,Item 5,B,25.6,8"""
    return csv_data


@pytest.fixture
def sample_csv_file(sample_csv_content):
    """Create a temporary CSV file"""
    file = io.BytesIO(sample_csv_content.encode())
    file.name = "test_data.csv"
    return file


@pytest.fixture
def completed_analysis(db_session, sample_csv_content):
    """Create a completed analysis for testing"""
    # Save CSV to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(sample_csv_content)
        temp_path = f.name

    analysis = Analysis(
        filename="test_completed.csv",
        file_size=len(sample_csv_content),
        file_path=temp_path,
        status="completed",
        data_profile={
            "shape": [5, 5],
            "columns": ["id", "name", "category", "value", "quantity"],
            "dtypes": {
                "id": "int64",
                "name": "object",
                "category": "object",
                "value": "float64",
                "quantity": "int64",
            },
            "missing_data": {"id": 0, "name": 0, "category": 0, "value": 0, "quantity": 0},
            "numeric_columns": ["id", "value", "quantity"],
            "categorical_columns": ["name", "category"],
            "sample_data": [
                {
                    "id": 1,
                    "name": "Item 1",
                    "category": "A",
                    "value": 10.5,
                    "quantity": 5,
                }
            ],
        },
        analysis_results={
            "correlations": [
                {"column1": "id", "column2": "value", "correlation": 0.95}
            ],
            "summary": {"total_rows": 5, "total_columns": 5, "missing_percentage": 0.0},
        },
        insights=[
            "Strong correlation between id and value",
            "Dataset is complete with no missing values",
        ],
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    yield analysis

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)
    db_session.delete(analysis)
    db_session.commit()


# =============================================================================
# BASIC ENDPOINT RESPONSE TIME BENCHMARKS
# =============================================================================


class TestBasicEndpoints:
    """Benchmark basic API endpoints"""

    def test_root_endpoint_response_time(self, benchmark, client):
        """Benchmark: GET / response time"""

        def get_root():
            response = client.get("/")
            return response

        response = benchmark(get_root)
        assert response.status_code == 200
        assert "message" in response.json()

    def test_health_check_response_time(self, benchmark, client):
        """Benchmark: GET /health response time"""

        def health_check():
            response = client.get("/health")
            return response

        response = benchmark(health_check)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_api_test_endpoint_response_time(self, benchmark, client):
        """Benchmark: GET /api/v1/test response time"""

        def test_endpoint():
            response = client.get("/api/v1/test")
            return response

        response = benchmark(test_endpoint)
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_openapi_json_response_time(self, benchmark, client):
        """Benchmark: GET /openapi.json response time"""

        def get_openapi():
            response = client.get("/openapi.json")
            return response

        response = benchmark(get_openapi)
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data


# =============================================================================
# FILE UPLOAD ENDPOINT BENCHMARKS
# =============================================================================


class TestFileUploadEndpoints:
    """Benchmark file upload endpoints"""

    def test_file_upload_response_time(self, benchmark, client, sample_csv_content):
        """Benchmark: POST /api/v1/files/upload response time"""

        def upload_file():
            files = {"file": ("test.csv", sample_csv_content, "text/csv")}
            response = client.post("/api/v1/files/upload", files=files)

            # Clean up created analysis
            if response.status_code == 200:
                try:
                    file_id = response.json().get("file_id")
                    if file_id:
                        # Delete the analysis record
                        from app.core.database import SessionLocal

                        db = SessionLocal()
                        analysis = (
                            db.query(Analysis).filter(Analysis.id == file_id).first()
                        )
                        if (
                            analysis
                            and analysis.file_path
                            and os.path.exists(analysis.file_path)
                        ):
                            os.unlink(analysis.file_path)
                        if analysis:
                            db.delete(analysis)
                            db.commit()
                        db.close()
                except:
                    pass

            return response

        response = benchmark(upload_file)
        assert response.status_code == 200
        assert response.json()["success"] is True

    def test_list_analyses_response_time(self, benchmark, client, completed_analysis):
        """Benchmark: GET /api/v1/files/analyses response time"""

        def list_analyses():
            response = client.get("/api/v1/files/analyses")
            return response

        response = benchmark(list_analyses)
        assert response.status_code == 200
        assert "analyses" in response.json()

    def test_get_analysis_status_response_time(
        self, benchmark, client, completed_analysis
    ):
        """Benchmark: GET /api/v1/files/analysis/{id}/status response time"""
        analysis_id = completed_analysis.id

        def get_status():
            response = client.get(f"/api/v1/files/analysis/{analysis_id}/status")
            return response

        response = benchmark(get_status)
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_get_analysis_results_response_time(
        self, benchmark, client, completed_analysis
    ):
        """Benchmark: GET /api/v1/files/analysis/{id} response time"""
        analysis_id = completed_analysis.id

        def get_results():
            response = client.get(f"/api/v1/files/analysis/{analysis_id}")
            return response

        response = benchmark(get_results)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == analysis_id
        assert "data_profile" in data


# =============================================================================
# CHAT ENDPOINT BENCHMARKS
# =============================================================================


class TestChatEndpoints:
    """Benchmark chat endpoints"""

    def test_send_chat_message_response_time(
        self, benchmark, client, completed_analysis
    ):
        """Benchmark: POST /api/v1/chat/message response time"""
        analysis_id = completed_analysis.id

        def send_message():
            payload = {
                "analysis_id": analysis_id,
                "message": "Show me the key insights",
                "conversation_history": [],
            }
            response = client.post("/api/v1/chat/message", json=payload)
            return response

        response = benchmark(send_message)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"]["type"] == "assistant"

    def test_send_chat_message_with_history_response_time(
        self, benchmark, client, completed_analysis
    ):
        """Benchmark: POST /api/v1/chat/message with conversation history"""
        analysis_id = completed_analysis.id

        conversation_history = [
            {
                "id": "user-1",
                "type": "user",
                "content": "What insights do you have?",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "id": "assistant-1",
                "type": "assistant",
                "content": "I found some interesting patterns in your data.",
                "timestamp": datetime.now().isoformat(),
            },
        ]

        def send_message_with_history():
            payload = {
                "analysis_id": analysis_id,
                "message": "Tell me more about correlations",
                "conversation_history": conversation_history,
            }
            response = client.post("/api/v1/chat/message", json=payload)
            return response

        response = benchmark(send_message_with_history)
        assert response.status_code == 200

    def test_get_conversation_history_response_time(
        self, benchmark, client, completed_analysis
    ):
        """Benchmark: GET /api/v1/chat/conversation/{id} response time"""
        analysis_id = completed_analysis.id

        def get_conversation():
            response = client.get(f"/api/v1/chat/conversation/{analysis_id}")
            return response

        response = benchmark(get_conversation)
        assert response.status_code == 200
        assert "analysis_id" in response.json()


# =============================================================================
# ERROR HANDLING BENCHMARKS
# =============================================================================


class TestErrorHandlingResponseTimes:
    """Benchmark error response times"""

    def test_404_not_found_response_time(self, benchmark, client):
        """Benchmark: 404 error response time"""

        def get_nonexistent():
            response = client.get("/api/v1/files/analysis/999999/status")
            return response

        response = benchmark(get_nonexistent)
        assert response.status_code == 404

    def test_invalid_file_upload_response_time(self, benchmark, client):
        """Benchmark: Invalid file upload error response time"""

        def upload_invalid():
            files = {"file": ("test.txt", b"Not a CSV file", "text/plain")}
            response = client.post("/api/v1/files/upload", files=files)
            return response

        response = benchmark(upload_invalid)
        assert response.status_code == 400

    def test_chat_with_invalid_analysis_response_time(self, benchmark, client):
        """Benchmark: Chat with invalid analysis ID response time"""

        def send_invalid_message():
            payload = {
                "analysis_id": 999999,
                "message": "Hello",
                "conversation_history": [],
            }
            response = client.post("/api/v1/chat/message", json=payload)
            return response

        response = benchmark(send_invalid_message)
        assert response.status_code == 404


# =============================================================================
# PAGINATION BENCHMARKS
# =============================================================================


class TestPaginationResponseTimes:
    """Benchmark paginated endpoint response times"""

    def test_list_analyses_with_pagination_response_time(
        self, benchmark, client, db_session
    ):
        """Benchmark: GET /api/v1/files/analyses with pagination"""
        # Create multiple analyses for pagination test
        analyses = []
        for i in range(20):
            analysis = Analysis(
                filename=f"test_{i}.csv", file_size=1000 + i, status="completed"
            )
            db_session.add(analysis)
            analyses.append(analysis)
        db_session.commit()

        def list_with_pagination():
            response = client.get("/api/v1/files/analyses?skip=0&limit=10")
            return response

        response = benchmark(list_with_pagination)
        assert response.status_code == 200

        # Cleanup
        for analysis in analyses:
            db_session.delete(analysis)
        db_session.commit()


# =============================================================================
# CONCURRENT REQUEST BENCHMARKS
# =============================================================================


class TestConcurrentRequestTimes:
    """Benchmark concurrent request handling"""

    def test_multiple_status_checks_response_time(
        self, benchmark, client, completed_analysis
    ):
        """Benchmark: Multiple concurrent status check requests"""
        analysis_id = completed_analysis.id

        def multiple_status_checks():
            responses = []
            for _ in range(5):
                response = client.get(f"/api/v1/files/analysis/{analysis_id}/status")
                responses.append(response)
            return responses

        responses = benchmark(multiple_status_checks)
        assert all(r.status_code == 200 for r in responses)

    def test_multiple_chat_requests_response_time(
        self, benchmark, client, completed_analysis
    ):
        """Benchmark: Multiple concurrent chat message requests"""
        analysis_id = completed_analysis.id

        def multiple_chat_requests():
            responses = []
            messages = [
                "Show insights",
                "What are the correlations?",
                "Summarize the data",
            ]

            for msg in messages:
                payload = {
                    "analysis_id": analysis_id,
                    "message": msg,
                    "conversation_history": [],
                }
                response = client.post("/api/v1/chat/message", json=payload)
                responses.append(response)
            return responses

        responses = benchmark(multiple_chat_requests)
        assert all(r.status_code == 200 for r in responses)


# =============================================================================
# LARGE PAYLOAD BENCHMARKS
# =============================================================================


class TestLargePayloadResponseTimes:
    """Benchmark response times with larger payloads"""

    def test_large_csv_upload_response_time(self, benchmark, client):
        """Benchmark: Upload larger CSV file (1000 rows)"""
        # Generate larger CSV
        csv_lines = ["id,name,category,value,quantity"]
        for i in range(1, 1001):
            csv_lines.append(f"{i},Item {i},Category {i % 5},{i * 1.5},{i % 100}")
        large_csv = "\n".join(csv_lines)

        def upload_large_file():
            files = {"file": ("large_test.csv", large_csv, "text/csv")}
            response = client.post("/api/v1/files/upload", files=files)

            # Clean up
            if response.status_code == 200:
                try:
                    file_id = response.json().get("file_id")
                    if file_id:
                        from app.core.database import SessionLocal

                        db = SessionLocal()
                        analysis = (
                            db.query(Analysis).filter(Analysis.id == file_id).first()
                        )
                        if (
                            analysis
                            and analysis.file_path
                            and os.path.exists(analysis.file_path)
                        ):
                            os.unlink(analysis.file_path)
                        if analysis:
                            db.delete(analysis)
                            db.commit()
                        db.close()
                except:
                    pass

            return response

        response = benchmark(upload_large_file)
        assert response.status_code == 200

    def test_chat_with_long_history_response_time(
        self, benchmark, client, completed_analysis
    ):
        """Benchmark: Chat message with long conversation history"""
        analysis_id = completed_analysis.id

        # Generate long conversation history
        conversation_history = []
        for i in range(10):
            conversation_history.extend(
                [
                    {
                        "id": f"user-{i}",
                        "type": "user",
                        "content": f"Question {i}: Tell me about the data",
                        "timestamp": datetime.now().isoformat(),
                    },
                    {
                        "id": f"assistant-{i}",
                        "type": "assistant",
                        "content": f"Response {i}: Here's what I found in your data...",
                        "timestamp": datetime.now().isoformat(),
                    },
                ]
            )

        def send_with_long_history():
            payload = {
                "analysis_id": analysis_id,
                "message": "Final question about insights",
                "conversation_history": conversation_history,
            }
            response = client.post("/api/v1/chat/message", json=payload)
            return response

        response = benchmark(send_with_long_history)
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only", "--benchmark-sort=mean"])
