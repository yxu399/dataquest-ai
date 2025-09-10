// Export all type definitions for centralized imports

// API Response Types
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

// Chat Types
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

export interface ConversationContext {
  analysis_id: number;
  data_profile: any;
  analysis_history: ChatMessage[];
  current_dataset?: any;
}

// Chart Types
export interface ChartData {
  type: 'bar' | 'line' | 'scatter' | 'histogram' | 'box' | 'heatmap';
  data: any;
  config?: any;
}

// Component Props Types
export interface StepperProps {
  steps: string[];
  currentStep: number;
  onStepChange?: (step: number) => void;
}

export interface TabsProps {
  tabs: Array<{
    id: string;
    label: string;
    content: React.ReactNode;
  }>;
  activeTab?: string;
  onTabChange?: (tabId: string) => void;
}

// Re-export from chat.ts for backward compatibility (if needed)
export * from './chat';
