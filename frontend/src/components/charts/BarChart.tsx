import React, { useState } from 'react';
import Plot from 'react-plotly.js';

interface BarChartProps {
  data: Record<string, Record<string, number>>;
  title: string;
}

export const BarChart: React.FC<BarChartProps> = ({ data, title }) => {
  // Use state to manage selected category
  const [selectedCategory, setSelectedCategory] = useState(Object.keys(data)[0] || 'department');
  
  // Get the data for the selected category
  const categoryData = data[selectedCategory];
  
  if (!categoryData) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No categorical data available for {selectedCategory}</p>
      </div>
    );
  }

  const categories = Object.keys(categoryData);
  const values = Object.values(categoryData);

  const plotData = [{
    x: categories,
    y: values,
    type: 'bar' as const,
    marker: {
      color: '#3b82f6',
      opacity: 0.8,
    },
    name: selectedCategory,
  }];

  const layout = {
    title: {
      text: `${title} - ${selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)}`,
      font: { size: 16, family: 'Arial, sans-serif' }
    },
    xaxis: {
      title: selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1),
      tickangle: -45,
    },
    yaxis: {
      title: 'Count'
    },
    margin: { t: 50, r: 30, b: 80, l: 50 },
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
    <div className="w-full">
      {/* Category Selector */}
      {Object.keys(data).length > 1 && (
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Category
          </label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="block w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            {Object.keys(data).map(category => (
              <option key={category} value={category}>
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </option>
            ))}
          </select>
        </div>
      )}

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