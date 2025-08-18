import React from 'react';
import { DataProfile } from '../../types';

interface DataProfileCardProps {
  dataProfile: DataProfile;
}

export const DataProfileCard: React.FC<DataProfileCardProps> = ({ dataProfile }) => {
  const totalMissing = Object.values(dataProfile.missing_data).reduce((sum, count) => sum + count, 0);
  const totalCells = dataProfile.shape[0] * dataProfile.shape[1];
  const missingPercentage = ((totalMissing / totalCells) * 100).toFixed(1);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h4 className="text-lg font-medium text-gray-900 mb-4">Data Profile</h4>
      
      <div className="space-y-4">
        {/* Shape */}
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">Dataset Shape</span>
          <span className="text-sm font-medium">{dataProfile.shape[0]} rows × {dataProfile.shape[1]} columns</span>
        </div>

        {/* Data Quality */}
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">Data Completeness</span>
          <span className={`text-sm font-medium ${totalMissing === 0 ? 'text-green-600' : 'text-yellow-600'}`}>
            {(100 - parseFloat(missingPercentage)).toFixed(1)}%
          </span>
        </div>

        {/* Column Types */}
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Numeric Columns</span>
            <span className="text-sm font-medium">{dataProfile.numeric_columns.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Categorical Columns</span>
            <span className="text-sm font-medium">{dataProfile.categorical_columns.length}</span>
          </div>
        </div>

        {/* Column Names */}
        <div>
          <span className="text-sm text-gray-600">Columns</span>
          <div className="mt-2 flex flex-wrap gap-1">
            {dataProfile.columns.map((column) => (
              <span
                key={column}
                className={`
                  inline-flex items-center px-2 py-1 rounded-full text-xs font-medium
                  ${dataProfile.numeric_columns.includes(column)
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-purple-100 text-purple-800'
                  }
                `}
              >
                {column}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};