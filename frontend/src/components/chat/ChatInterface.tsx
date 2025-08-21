import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage, ChatResponse, AnalysisResults } from '../../types';
import { apiService } from '../../services/api';

interface ChatInterfaceProps {
  results: AnalysisResults;
  onChartGenerated?: (chartData: any, chartType: string) => void;
  onChartSelected?: (chartType: string) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  results, 
  onChartGenerated,
  onChartSelected 
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Add welcome message on component mount
  useEffect(() => {
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      type: 'assistant',
      content: `Hi! I'm your AI data analyst. I've analyzed your dataset "${results.filename || 'dataset'}" with ${results.data_profile?.shape[0]} rows and ${results.data_profile?.shape[1]} columns. 

I can help you:
• Explore correlations between variables
• Create visualizations (bar charts, scatter plots, histograms)
• Explain statistical findings in business terms
• Answer questions about your data patterns

What would you like to know about your data?`,
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, [results]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Call real API
      const response: ChatResponse = await apiService.sendChatMessage({
        analysis_id: results.id,
        message: inputMessage,
        conversation_history: messages.slice(-6) // Send last 6 messages for context
      });

      // Add assistant response
      setMessages(prev => [...prev, response.message]);

      // Handle chart suggestions
      if (response.chart_suggestion && onChartSelected) {
        onChartSelected(response.chart_suggestion);
      }

      // Legacy chart data callback
      if (response.message.chart_data && response.message.chart_type && onChartGenerated) {
        onChartGenerated(response.message.chart_data, response.message.chart_type);
      }

    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: 'I apologize, but I encountered an error processing your request. Please make sure your backend is running and try again.',
        timestamp: new Date(),
        error: error instanceof Error ? error.message : 'Unknown error'
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
  };

  // Get dynamic suggestions based on actual data
  const getDynamicSuggestions = () => {
    const suggestions = ["Show me the key insights"];
    
    if (results.analysis_results?.correlations?.length > 0) {
      suggestions.push("Show correlations");
    }
    
    if (results.data_profile?.categorical_columns?.length > 0) {
      suggestions.push("Create a bar chart");
    }
    
    if (results.data_profile?.numeric_columns?.length > 0) {
      suggestions.push("Show me a scatter plot");
      suggestions.push("Display histogram");
    }
    
    // Add specific column suggestions
    const columns = [
      ...(results.data_profile?.numeric_columns || []),
      ...(results.data_profile?.categorical_columns || [])
    ].slice(0, 2); // First 2 columns
    
    columns.forEach(col => {
      suggestions.push(`Analyze ${col}`);
    });
    
    return suggestions.slice(0, 5); // Limit to 5 suggestions
  };

  return (
    <div className="flex flex-col h-96 bg-white border border-gray-200 rounded-lg">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-3">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          🤖 AI Data Analyst
          <span className="ml-2 text-sm font-normal text-gray-500">
            Powered by Claude AI
          </span>
        </h3>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.type === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-500 text-white'
                  : message.error
                  ? 'bg-red-50 text-red-900 border border-red-200'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="whitespace-pre-wrap text-sm">{message.content}</div>
              {message.chart_type && (
                <div className="mt-2 text-xs opacity-75">
                  📊 Suggested: {message.chart_type} chart
                </div>
              )}
              {message.error && (
                <div className="mt-2 text-xs text-red-600">
                  ⚠️ Error: {message.error}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
              <div className="flex items-center space-x-2">
                <div className="animate-spin h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent"></div>
                <span className="text-sm">AI is analyzing...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about your data..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isLoading}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
        
        {/* Dynamic suggestion buttons */}
        <div className="mt-2 flex flex-wrap gap-2">
          {getDynamicSuggestions().map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => handleSuggestionClick(suggestion)}
              className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors"
              disabled={isLoading}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};