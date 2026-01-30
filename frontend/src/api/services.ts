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
