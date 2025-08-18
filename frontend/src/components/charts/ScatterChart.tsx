import React from 'react';
import Plot from 'react-plotly.js';

interface ScatterChartProps {
  data: Record<string, any>[];
  xColumn: string;
  yColumn: string;
  title: string;
}

export const ScatterChart: React.FC<ScatterChartProps> = ({ data, xColumn, yColumn, title }) => {
  const x = data.map(row => row[xColumn]).filter(val => val != null);
  const y = data.map(row => row[yColumn]).filter(val => val != null);

  const plotData = [{
    x,
    y,
    mode: 'markers' as const,
    type: 'scatter' as const,
    marker: {
      color: '#3b82f6',
      size: 8,
      opacity: 0.7,
    },
    name: `${xColumn} vs ${yColumn}`,
  }];

  const layout = {
    title: {
      text: title,
      font: { size: 16 }
    },
    xaxis: {
      title: xColumn,
    },
    yaxis: {
      title: yColumn,
    },
    margin: { t: 50, r: 30, b: 50, l: 60 },
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