import React, { useState } from 'react';
import { AnalysisResults } from '../../services/api';
import { BarChart } from './BarChart';
import { ScatterPlot } from './ScatterPlot';
import { HistogramChart } from './HistogramChart';
import { CorrelationHeatmap } from './CorrelationHeatmap';
import { BoxPlot } from './BoxPlot';

interface ChartSelectorProps {
  results: AnalysisResults;
  defaultSelectedChart?: string | null;  
  onChartChange?: () => void;            
}

interface ChartOption {
  id: string;
  name: string;
  description: string;
  icon: string;
  requiresNumeric?: boolean;
  requiresCategorical?: boolean;
  requiresCorrelations?: boolean;
}

const chartOptions: ChartOption[] = [
  {
    id: 'bar',
    name: 'Bar Chart',
    description: 'Distribution of categorical data',
    icon: '📊',
    requiresCategorical: true
  },
  {
    id: 'scatter',
    name: 'Scatter Plot',
    description: 'Correlation between numeric variables',
    icon: '📈',
    requiresNumeric: true
  },
  {
    id: 'histogram',
    name: 'Histogram',
    description: 'Distribution of numeric data',
    icon: '📉',
    requiresNumeric: true
  },
  {
    id: 'correlation',
    name: 'Correlation Heatmap',
    description: 'Matrix of all correlations',
    icon: '🔥',
    requiresCorrelations: true
  },
  {
    id: 'boxplot',
    name: 'Box Plot',
    description: 'Statistical distribution summary',
    icon: '📦',
    requiresNumeric: true
  }
];

export const ChartSelector: React.FC<ChartSelectorProps> = ({ 
  results, 
  defaultSelectedChart,  // CHANGED: renamed from externalSelectedChart
  onChartChange 
}) => {
  const { data_profile, analysis_results } = results;

  // Check data availability
  const hasNumericData = data_profile?.numeric_columns?.length > 0;
  const hasCategoricalData = data_profile?.categorical_columns?.length > 0;
  const hasCorrelations = analysis_results?.correlations?.length > 0;
  const hasCategoricalDistribution = analysis_results?.categorical_distribution;

  // Filter available charts based on data
  const availableCharts = chartOptions.filter(chart => {
    if (chart.requiresNumeric && !hasNumericData) return false;
    if (chart.requiresCategorical && !hasCategoricalData) return false;
    if (chart.requiresCorrelations && !hasCorrelations) return false;
    if (chart.id === 'bar' && !hasCategoricalDistribution) return false;
    return true;
  });

  console.log('🎯 ChartSelector component rendered!', { 
    availableCharts: availableCharts.length,
    hasNumericData: hasNumericData ? data_profile?.numeric_columns?.length : 0,
    hasCategoricalData: hasCategoricalData ? data_profile?.categorical_columns?.length : 0,
    hasCorrelations: hasCorrelations ? analysis_results?.correlations?.length : 0,
    defaultSelectedChart  // ADD: log AI selection
  });

  const [internalSelectedChart, setInternalSelectedChart] = useState<string>(availableCharts[0]?.id || 'bar');
  const [isAISelected, setIsAISelected] = useState<boolean>(false);  // ADD: track AI selection
  
  // Use AI selection if provided, otherwise use internal state
  const selectedChart = defaultSelectedChart || internalSelectedChart;

  // Set default chart if current selection is not available
  React.useEffect(() => {
    if (!availableCharts.find(c => c.id === selectedChart)) {
      const defaultChart = availableCharts[0]?.id || 'bar';
      if (!defaultSelectedChart) {
        setInternalSelectedChart(defaultChart);
        setIsAISelected(false);
      }
    }
  }, [availableCharts, selectedChart, defaultSelectedChart]);

  // Handle AI chart selection changes
  React.useEffect(() => {
    if (defaultSelectedChart && defaultSelectedChart !== internalSelectedChart) {
      // AI made a selection
      if (availableCharts.find(c => c.id === defaultSelectedChart)) {
        setInternalSelectedChart(defaultSelectedChart);
        setIsAISelected(true);
        console.log('🤖 AI selected chart:', defaultSelectedChart);
      }
    } else if (!defaultSelectedChart && isAISelected) {
      // AI selection was cleared
      setIsAISelected(false);
      console.log('🧹 AI selection cleared');
    }
  }, [defaultSelectedChart, availableCharts, internalSelectedChart, isAISelected]);

  const renderSelectedChart = () => {
    const fullData = data_profile?.full_data || data_profile?.sample_data || [];
    
    switch (selectedChart) {
      case 'bar':
        return (
          <BarChart 
            data={analysis_results?.categorical_distribution || {}}
            title="Category Distribution"
          />
        );
      
      case 'scatter':
        return (
          <ScatterPlot 
            data={fullData}
            correlations={analysis_results?.correlations || []}
            numericColumns={data_profile?.numeric_columns || []}
            title="Scatter Plot Analysis"
          />
        );
      
      case 'histogram':
        return (
          <HistogramChart 
            data={fullData}
            columns={data_profile?.numeric_columns || []}
            title="Data Distribution"
          />
        );
      
      case 'correlation':
        return (
          <CorrelationHeatmap 
            correlations={analysis_results?.correlations || []}
            numericColumns={data_profile?.numeric_columns || []}
            title="Correlation Matrix"
          />
        );
      
      case 'boxplot':
        return (
          <BoxPlot 
            data={fullData}
            columns={data_profile?.numeric_columns || []}
            title="Statistical Summary"
          />
        );
      
      default:
        return <div>Chart not available</div>;
    }
  };

  if (!data_profile || !analysis_results) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No data available for visualization</p>
      </div>
    );
  }

  const selectedChartInfo = availableCharts.find(c => c.id === selectedChart);

  return (
    <div className="space-y-6">
      {/* Chart Type Selector */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-medium text-gray-900">Visualization Type</h4>
          <div className="text-sm text-gray-500">
            {`${data_profile?.full_data?.length || data_profile?.sample_data?.length || 0} data points`}
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
          {/* Dropdown */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Chart Type
            </label>
            <select
              value={selectedChart}
              onChange={(e) => {
                const newChart = e.target.value;
                setInternalSelectedChart(newChart);
                setIsAISelected(false);  // CHANGED: user manually changed, clear AI flag
                console.log('👤 User manually selected chart:', newChart);
                if (onChartChange) {
                  onChartChange();  // CHANGED: removed parameter
                }
              }}
              className="block w-full px-3 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base"
            >
              {availableCharts.map((chart) => (
                <option key={chart.id} value={chart.id}>
                  {chart.icon} {chart.name} - {chart.description}
                </option>
              ))}
            </select>
          </div>

          {/* Chart Info */}
          {selectedChartInfo && (
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-3">
                <div className="text-3xl">{selectedChartInfo.icon}</div>
                <div>
                  <div className="font-medium text-gray-900">{selectedChartInfo.name}</div>
                  <div className="text-sm text-gray-600">{selectedChartInfo.description}</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Data Availability Info with AI Indicator */}
        <div className="mt-4 text-sm text-gray-600 bg-blue-50 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div>
              <span className="font-medium">Available data:</span>
              {' '}
              {hasNumericData && `${data_profile?.numeric_columns?.length || 0} numeric columns`}
              {hasNumericData && hasCategoricalData && ', '}
              {hasCategoricalData && `${data_profile?.categorical_columns?.length || 0} categorical columns`}
              {hasCorrelations && `, ${analysis_results?.correlations?.length || 0} strong correlations`}
            </div>
            {/* NEW: AI Selection Indicator */}
            {isAISelected && (
              <div className="text-xs text-blue-600 bg-blue-200 px-2 py-1 rounded font-medium">
                🤖 AI Selected
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Selected Chart Display */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        {renderSelectedChart()}
      </div>
    </div>
  );
};
