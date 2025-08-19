import React, { useState } from 'react';
import Plot from 'react-plotly.js';

interface BoxPlotProps {
  data: Record<string, any>[];
  columns: string[];
  title: string;
}

export const BoxPlot: React.FC<BoxPlotProps> = ({ data, columns, title }) => {
  const [selectedColumns, setSelectedColumns] = useState<string[]>(
    columns.slice(0, Math.min(4, columns.length)) // Default to first 4 columns
  );
  const [showOutliers, setShowOutliers] = useState(true);

  if (!columns.length || !data.length) {
    return <div className="text-gray-500 text-center py-8">No numeric data available</div>;
  }

  // Prepare data for box plots
  const plotData = selectedColumns.map(column => {
    const values = data.map(row => row[column]).filter(val => val != null && !isNaN(val));
    
    return {
      y: values,
      type: 'box' as const,
      name: column.replace('_', ' ').toUpperCase(),
      boxpoints: showOutliers ? 'outliers' : false,
      marker: {
        color: `hsl(${selectedColumns.indexOf(column) * 360 / selectedColumns.length}, 70%, 50%)`,
        size: 4
      },
      line: {
        width: 2
      }
    };
  });

  const layout = {
    title: {
      text: title,
      font: { size: 16, family: 'Arial, sans-serif' }
    },
    yaxis: {
      title: 'Values',
      zeroline: false
    },
    xaxis: {
      title: 'Variables'
    },
    margin: { t: 50, r: 30, b: 80, l: 60 },
    height: 400,
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: {
      family: 'Arial, sans-serif',
      size: 12
    },
    showlegend: false
  };

  const config = {
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
    responsive: true,
  };

  // Calculate statistics for selected columns
  const getStats = (column: string) => {
    const values = data.map(row => row[column]).filter(val => val != null && !isNaN(val));
    if (values.length === 0) return null;

    const sorted = [...values].sort((a, b) => a - b);
    const q1 = sorted[Math.floor(sorted.length * 0.25)];
    const median = sorted[Math.floor(sorted.length * 0.5)];
    const q3 = sorted[Math.floor(sorted.length * 0.75)];
    const iqr = q3 - q1;
    
    return {
      min: Math.min(...values),
      q1,
      median,
      q3,
      max: Math.max(...values),
      iqr,
      mean: values.reduce((a, b) => a + b, 0) / values.length
    };
  };

  return (
    <div className="w-full space-y-4">
      {/* Controls */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Column Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Columns (max 6)
          </label>
          <div className="space-y-2 max-h-32 overflow-y-auto">
            {columns.map(column => (
              <label key={column} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedColumns.includes(column)}
                  onChange={(e) => {
                    if (e.target.checked && selectedColumns.length < 6) {
                      setSelectedColumns([...selectedColumns, column]);
                    } else if (!e.target.checked) {
                      setSelectedColumns(selectedColumns.filter(c => c !== column));
                    }
                  }}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">
                  {column.replace('_', ' ').toUpperCase()}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Options */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Display Options
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={showOutliers}
              onChange={(e) => setShowOutliers(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">Show Outliers</span>
          </label>
        </div>
      </div>

      {/* Statistics Table */}
      {selectedColumns.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 bg-gray-50 rounded-lg">
            <thead>
              <tr>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Variable</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Min</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Q1</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Median</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Q3</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Max</th>
                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">IQR</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {selectedColumns.map(column => {
                const stats = getStats(column);
                if (!stats) return null;
                
                return (
                  <tr key={column}>
                    <td className="px-4 py-2 text-sm font-medium text-gray-900">
                      {column.replace('_', ' ').toUpperCase()}
                    </td>
                    <td className="px-4 py-2 text-sm text-gray-700">{stats.min.toFixed(2)}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{stats.q1.toFixed(2)}</td>
                    <td className="px-4 py-2 text-sm font-medium text-blue-600">{stats.median.toFixed(2)}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{stats.q3.toFixed(2)}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{stats.max.toFixed(2)}</td>
                    <td className="px-4 py-2 text-sm text-gray-700">{stats.iqr.toFixed(2)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Chart */}
      {selectedColumns.length > 0 ? (
        <Plot
          data={plotData}
          layout={layout}
          config={config}
          style={{ width: '100%', height: '400px' }}
          useResizeHandler={true}
        />
      ) : (
        <div className="text-gray-500 text-center py-8">
          Please select at least one column to display
        </div>
      )}
    </div>
  );
};