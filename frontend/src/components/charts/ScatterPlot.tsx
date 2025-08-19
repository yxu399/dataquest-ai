import React, { useState } from 'react';
import Plot from 'react-plotly.js';

interface ScatterPlotProps {
  data: Record<string, any>[];
  correlations: Array<{
    column1: string;
    column2: string;
    correlation: number;
  }>;
  numericColumns: string[];
  title: string;
}

export const ScatterPlot: React.FC<ScatterPlotProps> = ({ 
  data, 
  correlations, 
  numericColumns, 
  title 
}) => {
  // Default to the strongest correlation
  const defaultCorrelation = correlations[0];
  const [xColumn, setXColumn] = useState(defaultCorrelation?.column1 || numericColumns[0]);
  const [yColumn, setYColumn] = useState(defaultCorrelation?.column2 || numericColumns[1]);

  // Get correlation value for current selection
  const currentCorrelation = correlations.find(
    corr => (corr.column1 === xColumn && corr.column2 === yColumn) ||
            (corr.column1 === yColumn && corr.column2 === xColumn)
  );

  // Extract x and y values from the data
  const xValues = data.map(row => row[xColumn]).filter(val => val != null);
  const yValues = data.map(row => row[yColumn]).filter(val => val != null);

  const plotData = [{
    x: xValues,
    y: yValues,
    mode: 'markers' as const,
    type: 'scatter' as const,
    marker: {
      color: currentCorrelation ? 
        (currentCorrelation.correlation > 0 ? '#10b981' : '#ef4444') : '#3b82f6',
      size: 8,
      opacity: 0.7,
    },
    name: `${xColumn} vs ${yColumn}`,
  }];

  const layout = {
    title: {
      text: `${title} - ${xColumn} vs ${yColumn}`,
      font: { size: 16, family: 'Arial, sans-serif' }
    },
    xaxis: {
      title: xColumn.replace('_', ' ').toUpperCase(),
    },
    yaxis: {
      title: yColumn.replace('_', ' ').toUpperCase(),
    },
    margin: { t: 50, r: 30, b: 50, l: 60 },
    height: 400,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: {
      family: 'Arial, sans-serif',
      size: 12
    }
  };

  const config = {
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
    responsive: true,
  };

  return (
    <div className="w-full space-y-4">
      {/* Column Selectors */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            X-Axis
          </label>
          <select
            value={xColumn}
            onChange={(e) => setXColumn(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            {numericColumns.map(column => (
              <option key={column} value={column}>
                {column.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Y-Axis
          </label>
          <select
            value={yColumn}
            onChange={(e) => setYColumn(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            {numericColumns.map(column => (
              <option key={column} value={column}>
                {column.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Correlation Info */}
      {currentCorrelation && (
        <div className={`p-3 rounded-lg ${
          currentCorrelation.correlation > 0 ? 'bg-green-50 border border-green-200' : 
          'bg-red-50 border border-red-200'
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">
              Correlation: 
            </span>
            <span className={`text-sm font-bold ${
              currentCorrelation.correlation > 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {currentCorrelation.correlation.toFixed(3)}
            </span>
          </div>
          <p className="text-xs text-gray-600 mt-1">
            {Math.abs(currentCorrelation.correlation) > 0.7 ? 'Strong' : 
             Math.abs(currentCorrelation.correlation) > 0.3 ? 'Moderate' : 'Weak'} 
            {currentCorrelation.correlation > 0 ? ' positive' : ' negative'} correlation
          </p>
        </div>
      )}

      {/* Chart */}
      <Plot
        data={plotData}
        layout={layout}
        config={config}
        style={{ width: '100%', height: '400px' }}
        useResizeHandler={true}
      />
    </div>
  );
};