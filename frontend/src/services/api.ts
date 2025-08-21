import axios from 'axios';

export interface UploadResponse {
  success: boolean;
  message: string;
  file_id?: number;
  filename?: string;
  file_size?: number;
}

export interface AnalysisStatus {
  id: number;
  status: string;
  filename: string;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface AnalysisResults {
  id: number;
  filename: string;
  status: string;
  data_profile?: {
    shape: [number, number];
    columns: string[];
    dtypes: Record<string, string>;
    missing_data: Record<string, number>;
    numeric_columns: string[];
    categorical_columns: string[];
    sample_data: Record<string, any>[];
    full_data?: Record<string, any>[];
  };
  analysis_results?: {
    summary: {
      total_rows: number;
      total_columns: number;
      missing_percentage: number;
    };
    correlations: Array<{
      column1: string;
      column2: string;
      correlation: number;
    }>;
    categorical_distribution?: Record<string, Record<string, number>>;
  };
  insights?: string[];
  created_at: string;
  completed_at?: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  analysis_id?: number;
  chart_data?: any;
  chart_type?: string;
  error?: string;
}

export interface ChatRequest {
  analysis_id: number;
  message: string;
  conversation_history: ChatMessage[];
}

export interface ChatResponse {
  message: ChatMessage;
  analysis?: any;
  chart_suggestion?: string;
  error?: string;
}

class ApiService {
  private baseURL = process.env.NODE_ENV === 'production' 
    ? '' 
    : '';

  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post(`${this.baseURL}/api/v1/files/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  async startAnalysis(analysisId: number): Promise<any> {
    const response = await axios.post(`${this.baseURL}/api/v1/files/analysis/${analysisId}/start`);
    return response.data;
  }

  async getAnalysisStatus(analysisId: number): Promise<AnalysisStatus> {
    const response = await axios.get(`${this.baseURL}/api/v1/files/analysis/${analysisId}/status`);
    return response.data;
  }

  async getAnalysisResults(analysisId: number): Promise<AnalysisResults> {
    const response = await axios.get(`${this.baseURL}/api/v1/files/analysis/${analysisId}`);
    return response.data;
  }

  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseURL}/api/v1/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...request,
        // Convert Date objects to ISO strings for API
        conversation_history: request.conversation_history.map(msg => ({
          ...msg,
          timestamp: msg.timestamp.toISOString()
        }))
      }),
    });

    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.status}`);
    }

    const data = await response.json();
    
    // Convert timestamp back to Date object
    if (data.message && data.message.timestamp) {
      data.message.timestamp = new Date(data.message.timestamp);
    }

    return data;
  }

  async getConversationHistory(analysisId: number): Promise<{
    analysis_id: number;
    conversation: ChatMessage[];
    data_summary: any;
  }> {
    const response = await fetch(`${this.baseURL}/api/v1/chat/conversation/${analysisId}`);

    if (!response.ok) {
      throw new Error(`Failed to get conversation history: ${response.status}`);
    }

    return await response.json();
  }

  startPolling(analysisId: number, onStatusUpdate: (status: AnalysisStatus) => void): void {
    const pollInterval = setInterval(async () => {
      try {
        const status = await this.getAnalysisStatus(analysisId);
        onStatusUpdate(status);
        
        // Stop polling when analysis is completed or failed
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Polling error:', error);
        clearInterval(pollInterval);
      }
    }, 1000); // Poll every second
  }
}


export const apiService = new ApiService();
