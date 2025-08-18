import React from 'react';
import Plot from 'react-plotly.js';

interface CorrelationHeatmapProps {
  correlations: Array<{
    column1: string;
    column2: string;
    correlation: number;
  }>;
  title: string;
}

export const CorrelationHeatmap: React.FC<CorrelationHeatmapProps> = ({ correlations, title }) => {
  if (!correlations.length) {
    return <div className="text-gray-500 text-center py-8">No correlations found</div>;
  }

  // Create a simple correlation visualization
  const columns = Array.from(new Set([
    ...correlations.map(c => c.column1),
    ...correlations.map(c => c.column2)
  ]));

  const plotData = [{
    x: correlations.map(c => c.column1),
    y: correlations.map(c => c.column2),
    z: correlations.map(c => c.correlation),
    type: 'scatter' as const,
    mode: 'markers' as const,
    marker: {
      size: correlations.map(c => Math.abs(c.correlation) * 20 + 10),
      color: correlations.map(c => c.correlation),
      colorscale: 'RdBu',
      showscale: true,
      colorbar: {
        title: 'Correlation'
      }
    },
    text: correlations.map(c => `${c.correlation.toFixed(3)}`),
    textposition: 'middle center',
  }];

  const layout = {
    title: {
      text: title,
      font: { size: 16 }
    },
    xaxis: {
      title: 'Feature 1',
    },
    yaxis: {
      title: 'Feature 2',
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