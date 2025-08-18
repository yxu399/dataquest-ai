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

class ApiService {
  private baseURL = process.env.NODE_ENV === 'production' 
    ? '' 
    : 'http://localhost:8000';

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

  // Polling for real-time updates
  startPolling(analysisId: number, onUpdate: (status: AnalysisStatus) => void, interval = 2000): () => void {
    const poll = async () => {
      try {
        const status = await this.getAnalysisStatus(analysisId);
        onUpdate(status);
        
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    const pollInterval = setInterval(poll, interval);
    poll(); // Initial call

    return () => clearInterval(pollInterval);
  }
}

export const apiService = new ApiService();