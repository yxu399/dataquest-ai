import React from 'react';

interface StatisticalSummaryProps {
  analysisResults: {
    summary: {
      total_rows: number;
      total_columns: number;
      missing_percentage: number;
    };
    correlations: Array<{
      column1: string;
      column2: string;
      correlation: number;
    }>;
    categorical_distribution?: Record<string, Record<string, number>>;
  };
}

export const StatisticalSummary: React.FC<StatisticalSummaryProps> = ({ analysisResults }) => {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h4 className="text-lg font-medium text-gray-900 mb-4">Statistical Summary</h4>
      
      <div className="space-y-4">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">{analysisResults.summary.total_rows.toLocaleString()}</div>
            <div className="text-sm text-gray-600">Total Rows</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">{analysisResults.summary.missing_percentage}%</div>
            <div className="text-sm text-gray-600">Missing Data</div>
          </div>
        </div>

        {/* Correlations */}
        {analysisResults.correlations.length > 0 && (
          <div>
            <h5 className="text-sm font-medium text-gray-900 mb-2">Strong Correlations</h5>
            <div className="space-y-2">
              {analysisResults.correlations.slice(0, 3).map((corr, idx) => (
                <div key={idx} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">
                    {corr.column1} ↔ {corr.column2}
                  </span>
                  <span className={`text-sm font-medium ${corr.correlation > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {corr.correlation > 0 ? '+' : ''}{corr.correlation}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Categorical Distribution */}
        {analysisResults.categorical_distribution && (
          <div>
            <h5 className="text-sm font-medium text-gray-900 mb-2">Category Distributions</h5>
            <div className="space-y-3">
              {Object.entries(analysisResults.categorical_distribution).slice(0, 2).map(([column, distribution]) => (
                <div key={column}>
                  <div className="text-xs text-gray-500 mb-1">{column}</div>
                  <div className="space-y-1">
                    {Object.entries(distribution).slice(0, 3).map(([value, count]) => (
                      <div key={value} className="flex justify-between text-xs">
                        <span className="text-gray-600">{value}</span>
                        <span className="font-medium">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};