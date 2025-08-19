import React, { useState } from 'react';
import Plot from 'react-plotly.js';

interface HistogramChartProps {
  data: Record<string, any>[];
  columns: string[];
  title: string;
}

export const HistogramChart: React.FC<HistogramChartProps> = ({ data, columns, title }) => {
  const [selectedColumn, setSelectedColumn] = useState(columns[0] || '');
  const [bins, setBins] = useState(20);

  if (!selectedColumn || !data.length) {
    return <div className="text-gray-500 text-center py-8">No numeric data available</div>;
  }

  const values = data.map(row => row[selectedColumn]).filter(val => val != null && !isNaN(val));

  if (values.length === 0) {
    return <div className="text-gray-500 text-center py-8">No valid numeric values found</div>;
  }

  // Calculate statistics
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const sorted = [...values].sort((a, b) => a - b);
  const median = sorted[Math.floor(sorted.length / 2)];
  const min = Math.min(...values);
  const max = Math.max(...values);
  const std = Math.sqrt(values.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / values.length);

  const plotData = [{
    x: values,
    type: 'histogram' as const,
    nbinsx: bins,
    marker: {
      color: '#3b82f6',
      opacity: 0.7,
      line: {
        color: '#1e40af',
        width: 1
      }
    },
    name: selectedColumn,
  }];

  const layout = {
    title: {
      text: `${title} - ${selectedColumn}`,
      font: { size: 16, family: 'Arial, sans-serif' }
    },
    xaxis: {
      title: selectedColumn.replace('_', ' ').toUpperCase(),
    },
    yaxis: {
      title: 'Frequency',
    },
    margin: { t: 50, r: 30, b: 50, l: 50 },
    height: 400,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: {
      family: 'Arial, sans-serif',
      size: 12
    },
    shapes: [
      // Mean line
      {
        type: 'line',
        x0: mean,
        y0: 0,
        x1: mean,
        y1: 1,
        yref: 'paper',
        line: {
          color: 'red',
          width: 2,
          dash: 'dash'
        }
      }
    ],
    annotations: [
      {
        x: mean,
        y: 0.9,
        yref: 'paper',
        text: `Mean: ${mean.toFixed(2)}`,
        showarrow: false,
        font: { color: 'red', size: 12 }
      }
    ]
  };

  const config = {
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
    responsive: true,
  };

  return (
    <div className="w-full space-y-4">
      {/* Controls */}
      <div className="grid grid-cols-2 gap-4">
        {/* Column Selector */}
        {columns.length > 1 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Column
            </label>
            <select
              value={selectedColumn}
              onChange={(e) => setSelectedColumn(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              {columns.map(column => (
                <option key={column} value={column}>
                  {column.replace('_', ' ').toUpperCase()}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Bins Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Number of Bins
          </label>
          <select
            value={bins}
            onChange={(e) => setBins(Number(e.target.value))}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value={10}>10</option>
            <option value={15}>15</option>
            <option value={20}>20</option>
            <option value={30}>30</option>
            <option value={50}>50</option>
          </select>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 p-4 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">{values.length}</div>
          <div className="text-sm text-gray-600">Count</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-blue-600">{mean.toFixed(2)}</div>
          <div className="text-sm text-gray-600">Mean</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-green-600">{median.toFixed(2)}</div>
          <div className="text-sm text-gray-600">Median</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-purple-600">{std.toFixed(2)}</div>
          <div className="text-sm text-gray-600">Std Dev</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-gray-600">{min.toFixed(2)} - {max.toFixed(2)}</div>
          <div className="text-sm text-gray-600">Range</div>
        </div>
      </div>

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