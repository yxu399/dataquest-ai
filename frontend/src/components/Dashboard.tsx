import React, { useState } from 'react';
import { Stepper, StepperStep } from './common/Stepper';
import { apiService, UploadResponse, AnalysisStatus, AnalysisResults } from '../services/api';

export const Dashboard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [uploadResponse, setUploadResponse] = useState<UploadResponse | null>(null);
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus | null>(null);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const steps: StepperStep[] = [
    {
      id: 'upload',
      name: 'Upload',
      status: currentStep > 0 ? 'complete' : currentStep === 0 ? 'current' : 'upcoming'
    },
    {
      id: 'analyze',
      name: 'Analyze',
      status: currentStep > 1 ? 'complete' : currentStep === 1 ? 'current' : 'upcoming'
    },
    {
      id: 'results',
      name: 'Results',
      status: currentStep > 2 ? 'complete' : currentStep === 2 ? 'current' : 'upcoming'
    }
  ];

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setError(null);
    
    try {
      // Upload file
      const response = await apiService.uploadFile(file);
      setUploadResponse(response);
      setCurrentStep(1);
      
      // Start analysis
      await apiService.startAnalysis(response.file_id!);
      
      // Start polling for status updates
      apiService.startPolling(response.file_id!, (status) => {
        setAnalysisStatus(status);
        
        if (status.status === 'completed') {
          setCurrentStep(2);
          loadResults(response.file_id!);
        } else if (status.status === 'failed') {
          setError(status.error_message || 'Analysis failed');
        }
      });
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
      setIsUploading(false);
    }
  };

  const loadResults = async (analysisId: number) => {
    try {
      const results = await apiService.getAnalysisResults(analysisId);
      setAnalysisResults(results);
      setIsUploading(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load results');
      setIsUploading(false);
    }
  };

  const resetDashboard = () => {
    setCurrentStep(0);
    setUploadResponse(null);
    setAnalysisStatus(null);
    setAnalysisResults(null);
    setError(null);
    setIsUploading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">DataQuest AI</h1>
              <p className="text-gray-600">Intelligent Data Analysis Platform</p>
            </div>
            {currentStep > 0 && (
              <button
                onClick={resetDashboard}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                New Analysis
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Stepper */}
        <div className="mb-8">
          <Stepper steps={steps} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600">{error}</p>
            <button
              onClick={() => setError(null)}
              className="mt-2 text-sm text-red-500 hover:text-red-700"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow p-6">
          {currentStep === 0 && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Upload Your Dataset</h2>
              <p className="text-gray-600 mb-6">
                Upload your CSV file to get started with intelligent data analysis.
              </p>
              
              <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                isUploading ? 'border-blue-300 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
              }`}>
                <div className="text-4xl mb-4">📊</div>
                <input 
                  type="file" 
                  accept=".csv"
                  onChange={handleFileSelect}
                  disabled={isUploading}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
                />
                <p className="text-sm text-gray-500 mt-2">CSV files up to 10MB</p>
                {isUploading && (
                  <div className="mt-4 flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <span className="ml-2 text-sm text-blue-600">Uploading...</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {currentStep === 1 && analysisStatus && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Analyzing Your Data</h2>
              <div className="text-center space-y-4">
                <h3 className="text-lg font-medium text-gray-900">{uploadResponse?.filename}</h3>
                <p className="text-sm text-gray-500">Status: {analysisStatus.status}</p>
                
                {/* Progress indicator */}
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                  <span className="ml-4 text-gray-600">Processing your dataset...</span>
                </div>

                {/* Analysis steps */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                  <div className="flex items-center space-x-3">
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                    <span className="text-sm text-gray-600">Data Profiling</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${analysisStatus.status === 'processing' ? 'bg-yellow-500' : 'bg-gray-300'}`} />
                    <span className="text-sm text-gray-600">Statistical Analysis</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${analysisStatus.status === 'completed' ? 'bg-green-500' : 'bg-gray-300'}`} />
                    <span className="text-sm text-gray-600">Insights Generation</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {currentStep === 2 && analysisResults && (
            <div>
              <h2 className="text-xl font-semibold mb-4">Analysis Complete!</h2>
              
              {/* Results Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-blue-900">Dataset</h3>
                  <p className="text-2xl font-bold text-blue-600">
                    {analysisResults.data_profile?.shape[0]} × {analysisResults.data_profile?.shape[1]}
                  </p>
                  <p className="text-sm text-blue-700">rows × columns</p>
                </div>
                
                <div className="bg-green-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-green-900">Data Quality</h3>
                  <p className="text-2xl font-bold text-green-600">
                    {analysisResults.analysis_results?.summary.missing_percentage}%
                  </p>
                  <p className="text-sm text-green-700">missing data</p>
                </div>
                
                <div className="bg-purple-50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-purple-900">Insights</h3>
                  <p className="text-2xl font-bold text-purple-600">{analysisResults.insights?.length || 0}</p>
                  <p className="text-sm text-purple-700">key findings</p>
                </div>
              </div>

              {/* Insights */}
              {analysisResults.insights && analysisResults.insights.length > 0 && (
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h3>
                  <div className="space-y-3">
                    {analysisResults.insights.map((insight, idx) => (
                      <div key={idx} className="flex items-start space-x-3">
                        <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-xs font-medium text-blue-600">{idx + 1}</span>
                        </div>
                        <p className="text-sm text-gray-700">{insight}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};