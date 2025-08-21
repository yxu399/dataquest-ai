export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  analysisId?: string;
  chartData?: any;
  chartType?: string;
  error?: string;
}

export interface ChatResponse {
  message: ChatMessage;
  analysis?: {
    chart_type?: string;
    chart_data?: any;
    insights?: string[];
    explanation?: string;
  };
  error?: string;
}

export interface ConversationContext {
  fileId: string;
  dataProfile: any;
  analysisHistory: ChatMessage[];
  currentDataset?: any;
}

// Extend existing API service interface
export interface ChatRequest {
  file_id: string;
  message: string;
  conversation_history: ChatMessage[];
}