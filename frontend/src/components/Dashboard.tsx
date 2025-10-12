import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare } from 'lucide-react';
import { Stepper, StepperStep } from './common/Stepper';
import { apiService, UploadResponse, AnalysisStatus, AnalysisResults } from '../services/api';
import { ChartSelector } from './charts/ChartSelector';
import { ChatInterface } from './chat/ChatInterface';
import { Button } from './ui/button';

export const Dashboard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [uploadResponse, setUploadResponse] = useState<UploadResponse | null>(null);
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus | null>(null);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [chatGeneratedChart, setChatGeneratedChart] = useState<{
    data: any;
    type: string;
  } | null>(null);

  const [interfaceMode, setInterfaceMode] = useState<'charts' | 'chat' | 'both'>('charts');
  
  // FIXED: Consistent naming with ChartSelector expectations
  const [selectedChartFromAI, setSelectedChartFromAI] = useState<string | null>(null);

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
    // ADDED: Reset AI chart selection
    setSelectedChartFromAI(null);
    setChatGeneratedChart(null);
  };

  const handleChatChartGenerated = (chartData: any, chartType: string) => {
    setChatGeneratedChart({ data: chartData, type: chartType });
  };

  const handleChatChartSelected = (chartType: string) => {
    console.log('🤖 AI selected chart:', chartType);
    setSelectedChartFromAI(chartType);
    
    // Auto-switch to both mode if currently in chat-only mode
    if (interfaceMode === 'chat') {
      setInterfaceMode('both');
    }
  };

  // FIXED: Correct function signature to match ChartSelector expectations
  const handleManualChartChange = () => {
    console.log('👤 User manually changed chart, clearing AI selection');
    // Clear AI selection when user manually changes chart
    setSelectedChartFromAI(null);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header - matching landing page style */}
      <header className="sticky top-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <MessageSquare className="h-6 w-6 text-primary" />
              <span className="font-sans text-xl font-semibold">DataQuest</span>
            </Link>

            {currentStep > 0 && (
              <Button variant="outline" onClick={resetDashboard}>
                New Analysis
              </Button>
            )}
          </div>
        </div>
      </header>

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
        <div className="bg-card rounded-lg shadow border border-border p-6">
          {currentStep === 0 && (
            <div>
              <h2 className="text-xl font-semibold text-foreground mb-4">Upload Your Dataset</h2>
              <p className="text-muted-foreground mb-6">
                Upload your CSV file to get started with intelligent data analysis.
              </p>

              <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                isUploading ? 'border-primary/30 bg-primary/5' : 'border-border hover:border-primary/50'
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
                <div className="bg-gray-50 rounded-lg p-6 mb-8">
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

              {/* Interactive Interface with Chat and Charts */}
              <div className="mt-8">
                {/* Interface Mode Selector */}
                <div className="mb-6">
                  <div className="flex space-x-4 border-b border-gray-200">
                    <button
                      onClick={() => setInterfaceMode('charts')}
                      className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                        interfaceMode === 'charts'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      📊 Chart Selector
                    </button>
                    <button
                      onClick={() => setInterfaceMode('chat')}
                      className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                        interfaceMode === 'chat'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      🤖 AI Chat
                    </button>
                    <button
                      onClick={() => setInterfaceMode('both')}
                      className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                        interfaceMode === 'both'
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700'
                      }`}
                    >
                      🔄 Both
                    </button>
                  </div>
                </div>

                {/* Interface Content */}
                <div className="space-y-8">
                  {/* Chat Mode - Show first in 'both' mode */}
                  {(interfaceMode === 'both' || interfaceMode === 'chat') && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-6">
                        🤖 Chat with Your Data
                      </h3>
                      
                      {/* Chat Interface - always full width */}
                      <div className="mb-6">
                        <ChatInterface 
                          results={analysisResults} 
                          onChartGenerated={handleChatChartGenerated}
                          onChartSelected={handleChatChartSelected}
                        />
                      </div>
                      
                      {/* AI Analysis Status - only show in chat-only mode */}
                      {interfaceMode === 'chat' && (
                        <div className="bg-white border border-gray-200 rounded-lg p-4">
                          <h4 className="text-md font-semibold text-gray-900 mb-4">
                            AI Analysis Status
                          </h4>
                          {selectedChartFromAI ? (
                            <div className="text-center text-green-600">
                              <div className="text-4xl mb-2">✅</div>
                              <p className="font-medium">Chart Suggested!</p>
                              <p className="text-sm">Switch to 'Both' or 'Chart Selector' to view {selectedChartFromAI} chart</p>
                            </div>
                          ) : (
                            <div className="text-center text-gray-500">
                              <div className="text-4xl mb-2">🤖</div>
                              <p>Ask me to create a chart</p>
                              <p className="text-sm">I'll suggest the perfect visualization</p>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Charts Mode - Show second in 'both' mode */}
                  {(interfaceMode === 'both' || interfaceMode === 'charts') && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                        📊 Interactive Data Visualizations
                        {/* AI Selection Indicator */}
                        {selectedChartFromAI && (
                          <span className="ml-3 text-sm font-normal text-blue-600 bg-blue-50 px-2 py-1 rounded">
                            🤖 AI Selected: {selectedChartFromAI}
                          </span>
                        )}
                      </h3>
                      <ChartSelector 
                        results={analysisResults}
                        defaultSelectedChart={selectedChartFromAI}
                        onChartChange={handleManualChartChange}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
