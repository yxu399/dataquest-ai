import React, { useState } from 'react';
import Plot from 'react-plotly.js';

interface HistogramChartProps {
  data: Record<string, any>[];
  columns: string[];
  title: string;
}

export const HistogramChart: React.FC<HistogramChartProps> = ({ data, columns, title }) => {
  const [selectedColumn, setSelectedColumn] = useState(columns[0] || '');

  if (!selectedColumn || !data.length) {
    return <div className="text-gray-500 text-center py-8">No numeric data available</div>;
  }

  const values = data.map(row => row[selectedColumn]).filter(val => val != null && !isNaN(val));

  const plotData = [{
    x: values,
    type: 'histogram' as const,
    marker: {
      color: '#3b82f6',
      opacity: 0.7,
    },
    name: selectedColumn,
  }];

  const layout = {
    title: {
      text: `${title} - ${selectedColumn}`,
      font: { size: 16 }
    },
    xaxis: {
      title: selectedColumn,
    },
    yaxis: {
      title: 'Frequency',
    },
    margin: { t: 50, r: 30, b: 50, l: 50 },
    height: 400,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
  };

  const config = {
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
    responsive: true,
  };

  return (
    <div className="w-full space-y-4">
      {/* Column Selector */}
      {columns.length > 1 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Column
          </label>
          <select
            value={selectedColumn}
            onChange={(e) => setSelectedColumn(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
          >
            {columns.map(column => (
              <option key={column} value={column}>{column}</option>
            ))}
          </select>
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