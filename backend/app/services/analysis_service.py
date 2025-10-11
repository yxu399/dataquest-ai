from datetime import datetime

from app.models.database import Analysis
from app.core.database import SessionLocal
from app.agents.simple_workflow import run_data_analysis


class AnalysisService:
    """Service for running data analysis workflows"""

    @staticmethod
    def run_analysis(analysis_id: int) -> dict:
        """Run complete analysis workflow for given analysis ID"""

        db = SessionLocal()
        try:
            # Get analysis record
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                return {"success": False, "error": "Analysis not found"}

            if not analysis.file_path:
                return {"success": False, "error": "No file path found"}

            # Run the simple data analysis workflow
            result = run_data_analysis(analysis.file_path, analysis.filename)

            # Update database with results
            if result.get("error"):
                analysis.status = "failed"
                analysis.error_message = result["error"]
            else:
                analysis.status = "completed"
                analysis.data_profile = result.get("data_profile")
                analysis.analysis_results = result.get("statistical_analysis")
                analysis.insights = result.get("insights")
                analysis.completed_at = datetime.utcnow()

            analysis.updated_at = datetime.utcnow()
            db.commit()

            return {
                "success": True,
                "analysis_id": analysis_id,
                "status": analysis.status,
                "results": {
                    "data_profile": result.get("data_profile"),
                    "statistical_analysis": result.get("statistical_analysis"),
                    "insights": result.get("insights"),
                    "error": result.get("error"),
                },
            }

        except Exception as e:
            # Update analysis as failed
            analysis.status = "failed"
            analysis.error_message = f"Analysis service error: {str(e)}"
            analysis.updated_at = datetime.utcnow()
            db.commit()

            return {"success": False, "error": str(e), "analysis_id": analysis_id}
        finally:
            db.close()


# Create service instance
analysis_service = AnalysisService()
