import React from 'react';
import { CheckCircleIcon, ExclamationTriangleIcon, InformationCircleIcon } from '@heroicons/react/24/outline';

interface InsightsListProps {
  insights: string[];
}

export const InsightsList: React.FC<InsightsListProps> = ({ insights }) => {
  const getInsightIcon = (insight: string) => {
    if (insight.includes('✓')) {
      return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
    } else if (insight.includes('⚠️')) {
      return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
    } else {
      return <InformationCircleIcon className="h-5 w-5 text-blue-500" />;
    }
  };

  return (
    <div className="space-y-4">
      <h4 className="text-lg font-medium text-gray-900">Key Insights</h4>
      
      <div className="space-y-3">
        {insights.map((insight, idx) => (
          <div key={idx} className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
            {getInsightIcon(insight)}
            <p className="text-sm text-gray-700 flex-1">{insight}</p>
          </div>
        ))}
      </div>

      {insights.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <InformationCircleIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
          <p>No insights generated for this dataset.</p>
        </div>
      )}
    </div>
  );
};