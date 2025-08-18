import React from 'react';
import Plot from 'react-plotly.js';

interface BarChartProps {
  data: Record<string, Record<string, number>>;
  title: string;
}

export const BarChart: React.FC<BarChartProps> = ({ data, title }) => {
  // Take the first categorical column for the chart
  const [columnName, columnData] = Object.entries(data)[0] || ['', {}];
  
  const x = Object.keys(columnData);
  const y = Object.values(columnData);

  const plotData = [{
    x,
    y,
    type: 'bar' as const,
    marker: {
      color: '#3b82f6',
      opacity: 0.8,
    },
    name: columnName,
  }];

  const layout = {
    title: {
      text: title,
      font: { size: 16 }
    },
    xaxis: {
      title: columnName,
      tickangle: -45,
    },
    yaxis: {
      title: 'Count'
    },
    margin: { t: 50, r: 30, b: 80, l: 50 },
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
    <div className="w-full">
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