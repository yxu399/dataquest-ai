import React from 'react';
import Plot from 'react-plotly.js';

interface CorrelationHeatmapProps {
  correlations: Array<{
    column1: string;
    column2: string;
    correlation: number;
  }>;
  numericColumns: string[];
  title: string;
}

export const CorrelationHeatmap: React.FC<CorrelationHeatmapProps> = ({ 
  correlations, 
  numericColumns, 
  title 
}) => {
  if (!correlations.length || numericColumns.length < 2) {
    return (
      <div className="text-gray-500 text-center py-8">
        <div className="text-lg mb-2">No correlations found</div>
        <div className="text-sm">Need at least 2 numeric columns with strong correlations (&gt; 0.7)</div>
      </div>
    );
  }

  // Create correlation matrix
  const createCorrelationMatrix = () => {
    // Initialize matrix with 1.0 on diagonal
    const matrix: number[][] = [];
    const columns = numericColumns;
    
    for (let i = 0; i < columns.length; i++) {
      matrix[i] = new Array(columns.length).fill(0);
      matrix[i][i] = 1.0; // Diagonal is always 1
    }

    // Fill in correlations
    correlations.forEach(corr => {
      const idx1 = columns.indexOf(corr.column1);
      const idx2 = columns.indexOf(corr.column2);
      
      if (idx1 !== -1 && idx2 !== -1) {
        matrix[idx1][idx2] = corr.correlation;
        matrix[idx2][idx1] = corr.correlation; // Symmetric
      }
    });

    return { matrix, columns };
  };

  const { matrix, columns } = createCorrelationMatrix();

  // Create hover text
  const hoverText = matrix.map((row, i) =>
    row.map((val, j) => `${columns[i]} vs ${columns[j]}<br>Correlation: ${val.toFixed(3)}`)
  );

  const plotData = [{
    z: matrix,
    x: columns.map(col => col.replace('_', ' ').toUpperCase()),
    y: columns.map(col => col.replace('_', ' ').toUpperCase()),
    type: 'heatmap' as const,
    colorscale: [
      [0, '#d73027'],     // Strong negative (-1)
      [0.25, '#f46d43'],  // Moderate negative
      [0.5, '#ffffff'],   // No correlation (0)
      [0.75, '#74add1'],  // Moderate positive
      [1, '#313695']      // Strong positive (+1)
    ],
    zmin: -1,
    zmax: 1,
    colorbar: {
      title: 'Correlation',
      titleside: 'right',
      tickmode: 'array',
      tickvals: [-1, -0.5, 0, 0.5, 1],
      ticktext: ['-1.0', '-0.5', '0.0', '0.5', '1.0']
    },
    hovertemplate: '%{text}<extra></extra>',
    text: hoverText,
    showscale: true
  }];

  const layout = {
    title: {
      text: title,
      font: { size: 16, family: 'Arial, sans-serif' }
    },
    xaxis: {
      title: '',
      tickangle: -45,
      side: 'bottom'
    },
    yaxis: {
      title: '',
      autorange: 'reversed' // This makes the heatmap start from top-left
    },
    margin: { t: 50, r: 100, b: 100, l: 100 },
    height: 500,
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
      {/* Correlation Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">{correlations.length}</div>
          <div className="text-sm text-gray-600">Strong Correlations</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-green-600">
            {correlations.filter(c => c.correlation > 0).length}
          </div>
          <div className="text-sm text-gray-600">Positive</div>
        </div>
        <div className="text-center">
          <div className="text-lg font-bold text-red-600">
            {correlations.filter(c => c.correlation < 0).length}
          </div>
          <div className="text-sm text-gray-600">Negative</div>
        </div>
      </div>

      {/* Top Correlations List */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h5 className="font-medium text-gray-900 mb-3">Strongest Correlations</h5>
        <div className="space-y-2">
          {correlations
            .sort((a, b) => Math.abs(b.correlation) - Math.abs(a.correlation))
            .slice(0, 5)
            .map((corr, idx) => (
            <div key={idx} className="flex items-center justify-between text-sm">
              <span className="text-gray-700">
                {corr.column1.replace('_', ' ')} ↔ {corr.column2.replace('_', ' ')}
              </span>
              <span className={`font-bold ${
                corr.correlation > 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {corr.correlation > 0 ? '+' : ''}{corr.correlation.toFixed(3)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Heatmap */}
      <Plot
        data={plotData}
        layout={layout}
        config={config}
        style={{ width: '100%', height: '500px' }}
        useResizeHandler={true}
      />
    </div>
  );
};