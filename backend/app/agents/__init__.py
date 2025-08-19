import pandas as pd
import json
from typing_extensions import TypedDict
from typing import Optional

class DataAnalysisState(TypedDict):
    """State for data analysis workflow"""
    file_path: str
    filename: str
    data_profile: Optional[dict]
    statistical_analysis: Optional[dict]
    insights: Optional[list]
    error: Optional[str]
    status: str

def data_profiler_agent(state: DataAnalysisState) -> DataAnalysisState:
    """Analyze dataset characteristics and structure"""
    try:
        # Load CSV file
        df = pd.read_csv(state["file_path"])

        # ADD THIS DEBUG LINE
        print(f"🔍 DEBUG: Processing {len(df)} rows for full_data")
        
        # Basic data profiling
        profile = {
            "shape": list(df.shape),  # [rows, columns]
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_data": {col: int(count) for col, count in df.isnull().sum().items()},
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
            
            # Keep sample for quick preview
            "sample_data": df.head(3).to_dict('records'),
            
            # ADD THIS: Full dataset for charts (limit to reasonable size)
            "full_data": df.head(1000).to_dict('records') if len(df) <= 1000 else df.sample(1000).to_dict('records')
        }

        # ADD THIS DEBUG LINE TOO
        print(f"🔍 DEBUG: Created full_data with {len(profile['full_data'])} rows")
        
        # Add summary statistics for numeric columns
        if profile["numeric_columns"]:
            numeric_stats = {}
            for col in profile["numeric_columns"]:
                numeric_stats[col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }
            profile["numeric_statistics"] = numeric_stats
        
        return {
            **state,
            "data_profile": profile,
            "status": "profiled",
            "error": None
        }
        
    except Exception as e:
        return {
            **state,
            "data_profile": None,
            "status": "error",
            "error": f"Data profiling failed: {str(e)}"
        }

def statistical_analyst_agent(state: DataAnalysisState) -> DataAnalysisState:
    """Perform statistical analysis on the dataset"""
    try:
        if state.get("error"):
            return state
            
        df = pd.read_csv(state["file_path"])
        
        analysis = {
            "summary": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "missing_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            }
        }
        
        # Correlation analysis for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 1:
            correlation_matrix = df[numeric_cols].corr()
            # Find high correlations (> 0.7)
            high_corr = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_val = correlation_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        high_corr.append({
                            "column1": correlation_matrix.columns[i],
                            "column2": correlation_matrix.columns[j],
                            "correlation": round(float(corr_val), 3)
                        })
            analysis["correlations"] = high_corr
        
        # Value counts for categorical columns
        categorical_analysis = {}
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() <= 20:  # Only for columns with reasonable number of unique values
                categorical_analysis[col] = df[col].value_counts().head(5).to_dict()
        
        if categorical_analysis:
            analysis["categorical_distribution"] = categorical_analysis
        
        return {
            **state,
            "statistical_analysis": analysis,
            "status": "analyzed",
            "error": None
        }
        
    except Exception as e:
        return {
            **state,
            "statistical_analysis": None,
            "status": "error", 
            "error": f"Statistical analysis failed: {str(e)}"
        }

def insights_generator_agent(state: DataAnalysisState) -> DataAnalysisState:
    """Generate business insights from the analysis"""
    try:
        if state.get("error"):
            return state
            
        insights = []
        profile = state.get("data_profile", {})
        stats = state.get("statistical_analysis", {})
        
        # Dataset overview insights
        if profile:
            rows, cols = profile.get("shape", [0, 0])
            insights.append(f"Dataset contains {rows:,} rows and {cols} columns")
            
            missing_pct = stats.get("summary", {}).get("missing_percentage", 0)
            if missing_pct > 10:
                insights.append(f"⚠️ High missing data: {missing_pct:.1f}% of values are missing")
            elif missing_pct > 0:
                insights.append(f"✓ Low missing data: {missing_pct:.1f}% of values are missing")
            else:
                insights.append("✓ Complete dataset: No missing values detected")
        
        # Correlation insights
        correlations = stats.get("correlations", [])
        if correlations:
            for corr in correlations[:3]:  # Top 3 correlations
                direction = "positively" if corr["correlation"] > 0 else "negatively"
                insights.append(f"📊 {corr['column1']} and {corr['column2']} are strongly {direction} correlated ({corr['correlation']})")
        
        # Data type insights
        if profile:
            numeric_cols = len(profile.get("numeric_columns", []))
            categorical_cols = len(profile.get("categorical_columns", []))
            
            if numeric_cols > categorical_cols:
                insights.append(f"📈 Numeric-heavy dataset: {numeric_cols} numeric vs {categorical_cols} categorical columns")
            elif categorical_cols > numeric_cols:
                insights.append(f"📋 Category-heavy dataset: {categorical_cols} categorical vs {numeric_cols} numeric columns")
            else:
                insights.append(f"⚖️ Balanced dataset: {numeric_cols} numeric and {categorical_cols} categorical columns")
        
        return {
            **state,
            "insights": insights,
            "status": "completed",
            "error": None
        }
        
    except Exception as e:
        return {
            **state,
            "insights": None,
            "status": "error",
            "error": f"Insights generation failed: {str(e)}"
        }