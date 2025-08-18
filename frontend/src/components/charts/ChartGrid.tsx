import React from 'react';
import { AnalysisResults } from '../../types';
import { BarChart } from './BarChart';
import { ScatterChart } from './ScatterChart';
import { HistogramChart } from './HistogramChart';
import { CorrelationHeatmap } from './CorrelationHeatmap';

interface ChartGridProps {
  results: AnalysisResults;
}

export const ChartGrid: React.FC<ChartGridProps> = ({ results }) => {
  const { data_profile, analysis_results } = results;

  if (!data_profile || !analysis_results) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No data available for visualization</p>
      </div>
    );
  }

  const hasNumericData = data_profile.numeric_columns.length > 0;
  const hasCategoricalData = data_profile.categorical_columns.length > 0;
  const hasCorrelations = analysis_results.correlations && analysis_results.correlations.length > 0;
  const hasCategoricalDistribution = analysis_results.categorical_distribution;

  return (
    <div className="space-y-8">
      {/* Phase 1 Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Bar Chart for Categorical Data */}
        {hasCategoricalData && hasCategoricalDistribution && (
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h4 className="text-lg font-medium text-gray-900 mb-4">Category Distribution</h4>
            <BarChart 
              data={analysis_results.categorical_distribution}
              title="Most Common Values by Category"
            />
          </div>
        )}

        {/* Histogram for Numeric Data */}
        {hasNumericData && data_profile.sample_data && (
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h4 className="text-lg font-medium text-gray-900 mb-4">Data Distribution</h4>
            <HistogramChart 
              data={data_profile.sample_data}
              columns={data_profile.numeric_columns}
              title="Numeric Data Distribution"
            />
          </div>
        )}

        {/* Scatter Plot for Correlations */}
        {hasNumericData && data_profile.numeric_columns.length >= 2 && data_profile.sample_data && (
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h4 className="text-lg font-medium text-gray-900 mb-4">Correlation Analysis</h4>
            <ScatterChart 
              data={data_profile.sample_data}
              xColumn={data_profile.numeric_columns[0]}
              yColumn={data_profile.numeric_columns[1]}
              title={`${data_profile.numeric_columns[0]} vs ${data_profile.numeric_columns[1]}`}
            />
          </div>
        )}

        {/* Correlation Heatmap */}
        {hasCorrelations && (
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h4 className="text-lg font-medium text-gray-900 mb-4">Correlation Matrix</h4>
            <CorrelationHeatmap 
              correlations={analysis_results.correlations}
              title="Feature Correlations"
            />
          </div>
        )}
      </div>

      {/* No charts message */}
      {!hasNumericData && !hasCategoricalData && (
        <div className="text-center py-12 text-gray-500">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Visualizations Available</h3>
          <p>Upload a dataset with numeric or categorical data to see interactive charts.</p>
        </div>
      )}
    </div>
  );
};