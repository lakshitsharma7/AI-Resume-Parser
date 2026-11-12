import axios from 'axios';
import { CandidateProfile, HealthStatus, CandidateSummary } from '../types/candidate';

const API_BASE = typeof window !== 'undefined' && window.location.port === '5173'
  ? 'http://127.0.0.1:8000/api/v1'
  : '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  getHealth: async (): Promise<HealthStatus> => {
    const res = await apiClient.get<HealthStatus>('/health');
    return res.data;
  },

  uploadResume: async (
    file: File,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<{
    status: string;
    resume_id: string;
    candidate_id: string;
    parsing_engine: string;
    candidate: CandidateProfile;
  }> => {
    const formData = new FormData();
    formData.append('file', file);

    const res = await apiClient.post('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return res.data;
  },

  getCandidate: async (candidateId: string): Promise<CandidateProfile> => {
    const res = await apiClient.get<CandidateProfile>(`/candidates/${candidateId}`);
    return res.data;
  },

  updateCandidate: async (
    candidateId: string,
    payload: Partial<CandidateProfile>
  ): Promise<CandidateProfile> => {
    const res = await apiClient.put<CandidateProfile>(`/candidates/${candidateId}`, payload);
    return res.data;
  },

  listCandidates: async (): Promise<CandidateSummary[]> => {
    const res = await apiClient.get<CandidateSummary[]>('/candidates/');
    return res.data;
  },

  downloadJson: async (candidateId: string, candidateName: string) => {
    const res = await apiClient.get(`/candidates/${candidateId}/export/json`, {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${candidateName.replace(/\s+/g, '_')}_profile.json`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  downloadExcel: async (candidateId: string, candidateName: string) => {
    const res = await apiClient.get(`/candidates/${candidateId}/export/excel`, {
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${candidateName.replace(/\s+/g, '_')}_profile.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
};

