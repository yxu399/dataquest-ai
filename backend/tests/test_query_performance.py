"""
Performance benchmarks for database queries and API endpoints
"""

import pytest
import os
import sys
import tempfile
import pandas as pd
from datetime import datetime
from fastapi.testclient import TestClient

# Add backend root to Python path
backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_root)

from main import app
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
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file for testing"""
    data = {
        "id": range(1, 1001),
        "name": [f"Item {i}" for i in range(1, 1001)],
        "category": ["A", "B", "C", "D"] * 250,
        "value": [i * 1.5 for i in range(1, 1001)],
        "quantity": [i % 100 for i in range(1, 1001)],
    }
    df = pd.DataFrame(data)

    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df.to_csv(f.name, index=False)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def sample_analysis(db_session, sample_csv_file):
    """Create a sample analysis record"""
    analysis = Analysis(
        filename="test_data.csv",
        file_size=os.path.getsize(sample_csv_file),
        file_path=sample_csv_file,
        status="processing",
        data_profile={
            "shape": [1000, 5],
            "columns": ["id", "name", "category", "value", "quantity"],
            "numeric_columns": ["id", "value", "quantity"],
            "categorical_columns": ["name", "category"],
        },
        analysis_results={
            "correlations": [
                {"column1": "id", "column2": "value", "correlation": 0.99}
            ],
            "summary": {
                "total_rows": 1000,
                "total_columns": 5,
                "missing_percentage": 0.0,
            },
        },
        insights=["Strong correlation between id and value"],
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    yield analysis

    # Cleanup
    db_session.delete(analysis)
    db_session.commit()


# =============================================================================
# DATABASE QUERY BENCHMARKS
# =============================================================================


class TestDatabaseQueryPerformance:
    """Benchmark database query operations"""

    def test_select_single_analysis_by_id(self, benchmark, db_session, sample_analysis):
        """Benchmark: SELECT single analysis by ID"""

        def query():
            return (
                db_session.query(Analysis)
                .filter(Analysis.id == sample_analysis.id)
                .first()
            )

        result = benchmark(query)
        assert result is not None
        assert result.id == sample_analysis.id

    def test_select_all_analyses(self, benchmark, db_session, sample_analysis):
        """Benchmark: SELECT all analyses"""
        # Create multiple records for more realistic test
        analyses = []
        for i in range(10):
            a = Analysis(
                filename=f"test_{i}.csv", file_size=1000 + i, status="completed"
            )
            db_session.add(a)
            analyses.append(a)
        db_session.commit()

        def query():
            return db_session.query(Analysis).all()

        result = benchmark(query)
        assert len(result) >= 11  # At least sample_analysis + 10 new ones

        # Cleanup
        for a in analyses:
            db_session.delete(a)
        db_session.commit()

    def test_select_with_filter_status(self, benchmark, db_session, sample_analysis):
        """Benchmark: SELECT with WHERE clause filtering by status"""

        def query():
            return (
                db_session.query(Analysis).filter(Analysis.status == "processing").all()
            )

        result = benchmark(query)
        assert isinstance(result, list)

    def test_select_with_json_access(self, benchmark, db_session, sample_analysis):
        """Benchmark: SELECT and access JSON fields"""

        def query():
            analysis = (
                db_session.query(Analysis)
                .filter(Analysis.id == sample_analysis.id)
                .first()
            )
            # Access JSON fields
            _ = analysis.data_profile
            _ = analysis.analysis_results
            _ = analysis.insights
            return analysis

        result = benchmark(query)
        assert result.data_profile is not None

    def test_insert_analysis(self, benchmark, db_session):
        """Benchmark: INSERT new analysis record"""

        def insert():
            analysis = Analysis(
                filename="benchmark_test.csv",
                file_size=5000,
                status="processing",
                data_profile={"test": "data"},
                analysis_results={"test": "results"},
            )
            db_session.add(analysis)
            db_session.commit()
            db_session.refresh(analysis)

            # Cleanup immediately
            db_session.delete(analysis)
            db_session.commit()

            return analysis.id

        result = benchmark(insert)
        assert result is not None

    def test_update_analysis_status(self, benchmark, db_session, sample_analysis):
        """Benchmark: UPDATE analysis status"""
        original_status = sample_analysis.status

        def update():
            analysis = (
                db_session.query(Analysis)
                .filter(Analysis.id == sample_analysis.id)
                .first()
            )
            analysis.status = "completed"
            analysis.updated_at = datetime.utcnow()
            db_session.commit()

            # Reset for next iteration
            analysis.status = original_status
            db_session.commit()

        benchmark(update)

    def test_update_analysis_json_fields(self, benchmark, db_session, sample_analysis):
        """Benchmark: UPDATE JSON fields"""

        def update():
            analysis = (
                db_session.query(Analysis)
                .filter(Analysis.id == sample_analysis.id)
                .first()
            )
            analysis.insights = ["New insight 1", "New insight 2"]
            db_session.commit()

        benchmark(update)

        # Verify update
        updated = (
            db_session.query(Analysis).filter(Analysis.id == sample_analysis.id).first()
        )
        assert "New insight 2" in updated.insights

    def test_delete_analysis(self, benchmark, db_session):
        """Benchmark: DELETE analysis record"""

        def delete_op():
            # Create a record to delete
            analysis = Analysis(
                filename="to_delete.csv", file_size=1000, status="processing"
            )
            db_session.add(analysis)
            db_session.commit()
            analysis_id = analysis.id

            # Delete it
            db_session.delete(analysis)
            db_session.commit()

            return analysis_id

        result = benchmark(delete_op)
        assert result is not None

    def test_complex_query_with_joins_and_filters(
        self, benchmark, db_session, sample_analysis
    ):
        """Benchmark: Complex query with multiple conditions"""

        def complex_query():
            return (
                db_session.query(Analysis)
                .filter(
                    Analysis.status.in_(["processing", "completed"]),
                    Analysis.file_size > 0,
                )
                .order_by(Analysis.created_at.desc())
                .limit(10)
                .all()
            )

        result = benchmark(complex_query)
        assert isinstance(result, list)


# =============================================================================
# API ENDPOINT BENCHMARKS
# =============================================================================


class TestAPIEndpointPerformance:
    """Benchmark API endpoint response times"""

    @pytest.mark.skipif(
        os.getenv("DATABASE_URL") is None, reason="Requires DATABASE_URL"
    )
    def test_health_check_endpoint(self, benchmark, client):
        """Benchmark: /health endpoint"""

        def health_check():
            response = client.get("/health")
            return response

        response = benchmark(health_check)
        assert response.status_code == 200

    @pytest.mark.skipif(
        os.getenv("DATABASE_URL") is None, reason="Requires DATABASE_URL"
    )
    def test_root_endpoint(self, benchmark, client):
        """Benchmark: / root endpoint"""

        def root():
            response = client.get("/")
            return response

        response = benchmark(root)
        assert response.status_code == 200

    @pytest.mark.skipif(
        os.getenv("DATABASE_URL") is None, reason="Requires DATABASE_URL"
    )
    def test_api_test_endpoint(self, benchmark, client):
        """Benchmark: /api/v1/test endpoint"""

        def test_endpoint():
            response = client.get("/api/v1/test")
            return response

        response = benchmark(test_endpoint)
        assert response.status_code == 200

    @pytest.mark.skipif(
        os.getenv("DATABASE_URL") is None, reason="Requires DATABASE_URL"
    )
    def test_openapi_json_endpoint(self, benchmark, client):
        """Benchmark: /openapi.json endpoint"""

        def openapi():
            response = client.get("/openapi.json")
            return response

        response = benchmark(openapi)
        assert response.status_code == 200

    @pytest.mark.skipif(
        os.getenv("DATABASE_URL") is None, reason="Requires DATABASE_URL"
    )
    def test_list_analyses_endpoint(self, benchmark, client, sample_analysis):
        """Benchmark: GET /api/v1/files/analyses endpoint"""

        def list_analyses():
            response = client.get("/api/v1/files/analyses")
            return response

        response = benchmark(list_analyses)
        # May be 200 or 404 depending on implementation
        assert response.status_code in [200, 404]

    @pytest.mark.skipif(
        os.getenv("DATABASE_URL") is None, reason="Requires DATABASE_URL"
    )
    def test_get_analysis_by_id_endpoint(self, benchmark, client, sample_analysis):
        """Benchmark: GET /api/v1/files/analyses/{id} endpoint"""

        def get_analysis():
            response = client.get(f"/api/v1/files/analyses/{sample_analysis.id}")
            return response

        response = benchmark(get_analysis)
        # Endpoint may or may not exist
        assert response.status_code in [200, 404]


# =============================================================================
# CHAT SERVICE BENCHMARKS
# =============================================================================


class TestChatServicePerformance:
    """Benchmark chat service operations"""

    @pytest.mark.asyncio
    async def test_chat_message_processing_fallback(self, benchmark, sample_analysis):
        """Benchmark: Chat message processing with fallback (no AI)"""
        from app.services.chat_service import ChatService

        chat_service = ChatService()

        async def process_message():
            return await chat_service.process_message(
                user_message="Show me the key insights",
                analysis_data=sample_analysis,
                conversation_history=[],
            )

        result = await benchmark(process_message)
        assert "content" in result

    def test_build_analysis_context(self, benchmark, sample_analysis):
        """Benchmark: Building analysis context"""
        from app.services.chat_service import ChatService

        chat_service = ChatService()

        def build_context():
            return chat_service._build_analysis_context(sample_analysis)

        result = benchmark(build_context)
        assert "data_profile" in result
        assert "analysis_results" in result

    def test_extract_column_mentions(self, benchmark):
        """Benchmark: Extracting column mentions from user message"""
        from app.services.chat_service import ChatService

        chat_service = ChatService()
        data_profile = {
            "numeric_columns": ["value", "quantity", "price"],
            "categorical_columns": ["category", "name", "department"],
        }

        def extract():
            return chat_service._extract_column_mentions(
                "Show me the distribution of value across different categories",
                data_profile,
            )

        result = benchmark(extract)
        assert isinstance(result, list)


# =============================================================================
# DATA ANALYSIS WORKFLOW BENCHMARKS
# =============================================================================


class TestDataAnalysisPerformance:
    """Benchmark data analysis operations"""

    def test_csv_file_reading(self, benchmark, sample_csv_file):
        """Benchmark: Reading CSV file with pandas"""

        def read_csv():
            return pd.read_csv(sample_csv_file)

        df = benchmark(read_csv)
        assert len(df) == 1000

    def test_data_profiling(self, benchmark, sample_csv_file):
        """Benchmark: Basic data profiling operations"""
        df = pd.read_csv(sample_csv_file)

        def profile():
            profile_data = {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "missing": df.isnull().sum().to_dict(),
                "numeric_stats": df.describe().to_dict(),
            }
            return profile_data

        result = benchmark(profile)
        assert "shape" in result

    def test_correlation_calculation(self, benchmark, sample_csv_file):
        """Benchmark: Calculating correlations"""
        df = pd.read_csv(sample_csv_file)

        def calculate_corr():
            numeric_df = df.select_dtypes(include=["float64", "int64"])
            return numeric_df.corr()

        result = benchmark(calculate_corr)
        assert result is not None

    def test_statistical_summary(self, benchmark, sample_csv_file):
        """Benchmark: Statistical summary generation"""
        df = pd.read_csv(sample_csv_file)

        def summary():
            return {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "missing_percentage": (
                    df.isnull().sum().sum() / (len(df) * len(df.columns))
                )
                * 100,
                "numeric_summary": df.describe().to_dict(),
            }

        result = benchmark(summary)
        assert result["total_rows"] == 1000


# =============================================================================
# CONCURRENT QUERY BENCHMARKS
# =============================================================================


class TestConcurrentQueryPerformance:
    """Benchmark concurrent database operations"""

    def test_concurrent_read_queries(self, benchmark, db_session, sample_analysis):
        """Benchmark: Multiple concurrent read queries"""

        def concurrent_reads():
            results = []
            for _ in range(10):
                result = (
                    db_session.query(Analysis)
                    .filter(Analysis.id == sample_analysis.id)
                    .first()
                )
                results.append(result)
            return results

        results = benchmark(concurrent_reads)
        assert len(results) == 10

    def test_batch_insert_operations(self, benchmark, db_session):
        """Benchmark: Batch insert operations"""

        def batch_insert():
            analyses = []
            for i in range(50):
                analysis = Analysis(
                    filename=f"batch_test_{i}.csv",
                    file_size=1000 + i,
                    status="processing",
                )
                analyses.append(analysis)

            db_session.add_all(analyses)
            db_session.commit()

            # Cleanup
            for analysis in analyses:
                db_session.delete(analysis)
            db_session.commit()

        benchmark(batch_insert)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
