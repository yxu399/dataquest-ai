"""Simplified analysis workflow without complex LangGraph dependencies"""
import pandas as pd
from typing import Dict, Any, Optional

def run_data_analysis(file_path: str, filename: str) -> Dict[str, Any]:
    """Run complete data analysis workflow"""
    
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # 1. Data Profiling
        data_profile = {
            "shape": list(df.shape),
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_data": {col: int(count) for col, count in df.isnull().sum().items()},
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
            "sample_data": df.head(3).to_dict('records'),
            "full_data": df.to_dict('records')
        }
        
        # Add numeric statistics
        if data_profile["numeric_columns"]:
            numeric_stats = {}
            for col in data_profile["numeric_columns"]:
                numeric_stats[col] = {
                    "mean": float(df[col].mean()),
                    "median": float(df[col].median()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max())
                }
            data_profile["numeric_statistics"] = numeric_stats
        
        # 2. Statistical Analysis
        statistical_analysis = {
            "summary": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "missing_percentage": round((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100, 2)
            }
        }
        
        # Correlation analysis
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 1:
            correlation_matrix = df[numeric_cols].corr()
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
            statistical_analysis["correlations"] = high_corr
        
        # Categorical distribution analysis
        categorical_analysis = {}
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() <= 20:  # Only for reasonable number of unique values
                categorical_analysis[col] = df[col].value_counts().head(5).to_dict()
        
        if categorical_analysis:
            statistical_analysis["categorical_distribution"] = categorical_analysis
        
        # 3. Generate Insights
        insights = []
        rows, cols = data_profile["shape"]
        insights.append(f"Dataset contains {rows:,} rows and {cols} columns")
        
        missing_pct = statistical_analysis["summary"]["missing_percentage"]
        if missing_pct > 10:
            insights.append(f"⚠️ High missing data: {missing_pct}% of values are missing")
        elif missing_pct > 0:
            insights.append(f"✓ Low missing data: {missing_pct}% of values are missing")
        else:
            insights.append("✓ Complete dataset: No missing values detected")
        
        # Correlation insights
        correlations = statistical_analysis.get("correlations", [])
        if correlations:
            for corr in correlations[:3]:  # Top 3 correlations
                direction = "positively" if corr["correlation"] > 0 else "negatively"
                insights.append(f"📊 {corr['column1']} and {corr['column2']} are strongly {direction} correlated ({corr['correlation']})")
        
        # Data type insights
        numeric_cols = len(data_profile["numeric_columns"])
        categorical_cols = len(data_profile["categorical_columns"])
        
        if numeric_cols > categorical_cols:
            insights.append(f"📈 Numeric-heavy dataset: {numeric_cols} numeric vs {categorical_cols} categorical columns")
        elif categorical_cols > numeric_cols:
            insights.append(f"📋 Category-heavy dataset: {categorical_cols} categorical vs {numeric_cols} numeric columns")
        else:
            insights.append(f"⚖️ Balanced dataset: {numeric_cols} numeric and {categorical_cols} categorical columns")
        
        return {
            "success": True,
            "data_profile": data_profile,
            "statistical_analysis": statistical_analysis,
            "insights": insights,
            "status": "completed",
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "data_profile": None,
            "statistical_analysis": None,
            "insights": None,
            "status": "failed",
            "error": str(e)
        }