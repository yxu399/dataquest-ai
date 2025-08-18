import React, { useState } from 'react';
import { AnalysisResults as IAnalysisResults } from '../../types';
import { DataProfileCard } from './DataProfileCard';
import { StatisticalSummary } from './StatisticalSummary';
import { InsightsList } from './InsightsList';
import { ChartGrid } from '../charts/ChartGrid';
import { Tabs, Tab } from '../common/Tabs';

interface AnalysisResultsProps {
  results: IAnalysisResults;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ results }) => {
  const [activeTab, setActiveTab] = useState('overview');

  const tabs: Tab[] = [
    { id: 'overview', name: 'Overview', icon: '📊' },
    { id: 'charts', name: 'Visualizations', icon: '📈' },
    { id: 'insights', name: 'Insights', icon: '💡' },
    { id: 'data', name: 'Raw Data', icon: '📋' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">{results.filename}</h3>
          <p className="text-sm text-gray-500">
            Analyzed {results.data_profile?.shape[0]} rows × {results.data_profile?.shape[1]} columns
          </p>
        </div>
        <div className="text-sm text-gray-500">
          Completed {new Date(results.completed_at!).toLocaleString()}
        </div>
      </div>

      {/* Tabs */}
      <Tabs tabs={tabs} activeTab={activeTab} onChange={setActiveTab} />

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DataProfileCard dataProfile={results.data_profile!} />
            <StatisticalSummary analysisResults={results.analysis_results!} />
          </div>
        )}

        {activeTab === 'charts' && (
          <ChartGrid results={results} />
        )}

        {activeTab === 'insights' && (
          <InsightsList insights={results.insights || []} />
        )}

        {activeTab === 'data' && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium mb-4">Sample Data Preview</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {results.data_profile?.columns.map((column) => (
                      <th
                        key={column}
                        className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {results.data_profile?.sample_data.map((row, idx) => (
                    <tr key={idx}>
                      {results.data_profile?.columns.map((column) => (
                        <td key={column} className="px-4 py-2 whitespace-nowrap text-sm text-gray-900">
                          {row[column]}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};