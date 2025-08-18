import React from 'react';
import { AnalysisStatus } from '../../types';

interface AnalysisProgressProps {
  status: AnalysisStatus;
  filename: string;
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ status, filename }) => {
  const getProgressPercentage = () => {
    switch (status.status) {
      case 'uploaded': return 10;
      case 'processing': return 50;
      case 'completed': return 100;
      case 'failed': return 0;
      default: return 0;
    }
  };

  const getStatusMessage = () => {
    switch (status.status) {
      case 'uploaded': return 'File uploaded successfully';
      case 'processing': return 'Analyzing your data...';
      case 'completed': return 'Analysis completed!';
      case 'failed': return 'Analysis failed';
      default: return 'Unknown status';
    }
  };

  const progress = getProgressPercentage();

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900">{filename}</h3>
        <p className="text-sm text-gray-500 mt-1">{getStatusMessage()}</p>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-primary-600 h-2 rounded-full transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Analysis Steps */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${progress >= 10 ? 'bg-green-500' : 'bg-gray-300'}`} />
          <span className="text-sm text-gray-600">Data Profiling</span>
        </div>
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${progress >= 50 ? 'bg-green-500' : 'bg-gray-300'}`} />
          <span className="text-sm text-gray-600">Statistical Analysis</span>
        </div>
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${progress >= 100 ? 'bg-green-500' : 'bg-gray-300'}`} />
          <span className="text-sm text-gray-600">Insights Generation</span>
        </div>
      </div>

      {status.status === 'processing' && (
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      )}
    </div>
  );
};