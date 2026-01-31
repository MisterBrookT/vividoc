// Data models matching the backend API

export interface DocumentSpec {
  id: string;
  topic: string;
  knowledge_units: KnowledgeUnit[];
  metadata?: SpecMetadata;
}

export interface KnowledgeUnit {
  id: string;
  title: string;
  description: string;
  learning_objectives: string[];
  prerequisites: string[];
}

export interface SpecMetadata {
  created_at: string;
  updated_at: string;
}

export interface JobStatus {
  job_id: string;
  status: 'running' | 'completed' | 'failed';
  progress: ProgressInfo;
  result?: {
    document_id: string;
  };
  error?: string;
}

export interface ProgressInfo {
  phase: 'planning' | 'executing' | 'evaluating';
  overall_percent: number;
  current_ku?: string;
  ku_stage?: 'stage1' | 'stage2';
  ku_progress: KUProgress[];
}

export interface KUProgress {
  ku_id: string;
  title: string;
  status: 'pending' | 'stage1' | 'stage2' | 'completed';
}

export interface GeneratedDocument {
  document_id: string;
  created_at: string;
  spec_id: string;
}

// API Request/Response types

export interface SpecGenerateRequest {
  topic: string;
}

export interface SpecGenerateResponse {
  spec_id: string;
  spec: DocumentSpec;
}

export interface SpecUpdateRequest {
  spec: DocumentSpec;
}

export interface DocumentGenerateRequest {
  spec_id: string;
}

export interface DocumentGenerateResponse {
  job_id: string;
}

export interface DocumentHtmlResponse {
  html: string;
}

export interface ApiError {
  error: string;
  detail?: string;
}

export interface Config {
  llm_model: string;
  available_models: string[];
}
