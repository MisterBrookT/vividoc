import apiClient from './client';
import type {
  SpecGenerateRequest,
  SpecGenerateResponse,
  DocumentSpec,
  DocumentGenerateRequest,
  DocumentGenerateResponse,
  JobStatus,
  GeneratedDocument,
  DocumentHtmlResponse,
} from '../types/models';

export interface HistoryItem {
  id: string;
  topic: string;
  timestamp: string;
}

export interface HistoryResponse {
  history: HistoryItem[];
}

// Spec Management APIs

export const generateSpec = async (topic: string): Promise<SpecGenerateResponse> => {
  const response = await apiClient.post<SpecGenerateResponse>('/api/spec/generate', {
    topic,
  } as SpecGenerateRequest);
  return response.data;
};

export const getSpec = async (specId: string): Promise<{ spec: DocumentSpec }> => {
  const response = await apiClient.get<{ spec: DocumentSpec }>(`/api/spec/${specId}`);
  return response.data;
};

export const getHistory = async (): Promise<{ history: HistoryItem[] }> => {
  const response = await apiClient.get<HistoryResponse>('/api/history');
  return response.data;
};

export const getSpecHtml = async (specId: string): Promise<string | null> => {
  try {
    const response = await apiClient.get<DocumentHtmlResponse>(`/api/spec/${specId}/html`);
    return response.data.html;
  } catch (error) {
    return null;
  }
};

export const getChatHistory = async (specId: string): Promise<any[]> => {
  try {
    const response = await apiClient.get<{ messages: any[] }>(`/api/spec/${specId}/chat`);
    return response.data.messages;
  } catch (error) {
    return [];
  }
};

export const saveChatHistory = async (specId: string, messages: any[]): Promise<void> => {
  await apiClient.put(`/api/spec/${specId}/chat`, { messages });
};

export const updateSpec = async (
  specId: string,
  spec: DocumentSpec
): Promise<{ spec: DocumentSpec }> => {
  const response = await apiClient.put<{ spec: DocumentSpec }>(`/api/spec/${specId}`, {
    spec,
  });
  return response.data;
};

// Document Generation APIs

export const generateDocument = async (specId: string): Promise<DocumentGenerateResponse> => {
  const response = await apiClient.post<DocumentGenerateResponse>('/api/document/generate', {
    spec_id: specId,
  } as DocumentGenerateRequest);
  return response.data;
};

export const getDocument = async (documentId: string): Promise<GeneratedDocument> => {
  const response = await apiClient.get<GeneratedDocument>(`/api/document/${documentId}`);
  return response.data;
};

export const getDocumentHtml = async (documentId: string): Promise<string> => {
  const response = await apiClient.get<DocumentHtmlResponse>(
    `/api/document/${documentId}/html`
  );
  return response.data.html;
};

export const getDocumentDownloadUrl = (documentId: string): string => {
  return `${apiClient.defaults.baseURL}/api/document/${documentId}/download`;
};

// Job Management APIs

export const getJobStatus = async (jobId: string): Promise<JobStatus> => {
  const response = await apiClient.get<JobStatus>(`/api/jobs/${jobId}/status`);
  return response.data;
};

export const getJobHtml = async (jobId: string): Promise<{ html: string | null; status: string }> => {
  const response = await apiClient.get<{ html: string | null; status: string }>(
    `/api/jobs/${jobId}/html`
  );
  return response.data;
};

// Configuration APIs

export const getConfig = async (): Promise<{ llm_model: string; available_models: string[] }> => {
  const response = await apiClient.get<{ llm_model: string; available_models: string[] }>('/api/config');
  return response.data;
};

export const updateConfig = async (llmModel: string): Promise<{ llm_model: string; available_models: string[] }> => {
  const response = await apiClient.put<{ llm_model: string; available_models: string[] }>('/api/config', {
    llm_model: llmModel,
  });
  return response.data;
};

export const getStyleOptions = async (): Promise<{ options: Record<string, any> }> => {
  const response = await apiClient.get<{ options: Record<string, any> }>('/api/style/options');
  return response.data;
};

export const getStyle = async (specId: string): Promise<Record<string, any>> => {
  try {
    const response = await apiClient.get<{ style: Record<string, any> }>(`/api/spec/${specId}/style`);
    return response.data.style;
  } catch {
    return {};
  }
};

export const saveStyle = async (specId: string, style: Record<string, any>): Promise<void> => {
  await apiClient.put(`/api/spec/${specId}/style`, { style });
};
// Chat Streaming API

export interface ChatStreamEvent {
  type: 'token' | 'html_updated' | 'done' | 'error' | 'edit_mode_start' | 'spec_updated';
  content?: string;
  html?: string;
  spec?: any;
}

export const streamChat = async (
  specId: string,
  message: string,
  onEvent: (event: ChatStreamEvent) => void,
  stage: 'spec' | 'doc' = 'doc',
  history: Array<{ role: string; content: string }> = []
): Promise<void> => {
  const baseURL = apiClient.defaults.baseURL || '';
  const response = await fetch(`${baseURL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ spec_id: specId, message, stage, history }),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const event: ChatStreamEvent = JSON.parse(line.slice(6));
          onEvent(event);
        } catch {
          // skip malformed lines
        }
      }
    }
  }

  // Process any remaining data in buffer after stream ends
  if (buffer.trim()) {
    for (const line of buffer.split('\n')) {
      if (line.startsWith('data: ')) {
        try {
          const event: ChatStreamEvent = JSON.parse(line.slice(6));
          onEvent(event);
        } catch {
          // skip malformed lines
        }
      }
    }
  }
};
