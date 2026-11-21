import { Job, JobSummary, ProcessingStatus, MatchResultItem, CandidateDetailAnalysis } from './types';

const API_BASE = '/api/v1';

export const api = {
  // Jobs
  async getJobs(): Promise<Job[]> {
    const res = await fetch(`${API_BASE}/jobs`);
    if (!res.ok) throw new Error('Failed to fetch jobs');
    return res.json();
  },

  async getJob(id: string): Promise<Job> {
    const res = await fetch(`${API_BASE}/jobs/${id}`);
    if (!res.ok) throw new Error('Failed to fetch job');
    return res.json();
  },

  async createJob(payload: {
    title: string;
    description: string;
    department?: string;
    location?: string;
    scoring_weights?: any;
  }): Promise<Job> {
    const res = await fetch(`${API_BASE}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to create job');
    return res.json();
  },

  async updateJob(id: string, payload: any): Promise<Job> {
    const res = await fetch(`${API_BASE}/jobs/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to update job');
    return res.json();
  },

  async deleteJob(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/jobs/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete job');
  },

  // Upload
  async uploadResumes(jobId: string, files: File[]): Promise<any[]> {
    const formData = new FormData();
    files.forEach((f) => formData.append('files', f));
    const res = await fetch(`${API_BASE}/jobs/${jobId}/resumes`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload resumes');
    return res.json();
  },

  async loadSampleResumes(jobId: string): Promise<any[]> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/load-sample-resumes`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to load sample resumes');
    return res.json();
  },

  // Status
  async getProcessingStatus(jobId: string): Promise<ProcessingStatus> {
    const res = await fetch(`${API_BASE}/jobs/${jobId}/status`);
    if (!res.ok) throw new Error('Failed to get processing status');
    return res.json();
  },

  async deleteResume(resumeId: string): Promise<void> {
    const res = await fetch(`${API_BASE}/resumes/${resumeId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete resume');
  },

  // Candidates & Ranking
  async getRankedCandidates(jobId: string, statusFilter?: string): Promise<MatchResultItem[]> {
    const url = new URL(`${window.location.origin}${API_BASE}/jobs/${jobId}/candidates`);
    if (statusFilter && statusFilter !== 'All') {
      url.searchParams.append('status_filter', statusFilter);
    }
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error('Failed to get candidate rankings');
    return res.json();
  },

  async getCandidateExplanation(candidateId: string, jobId: string): Promise<CandidateDetailAnalysis> {
    const res = await fetch(`${API_BASE}/candidates/${candidateId}/explanation?job_id=${jobId}`);
    if (!res.ok) throw new Error('Failed to get candidate explanation');
    return res.json();
  },

  // Summary
  async getJobSummary(jobId: string): Promise<JobSummary> {
    const res = await fetch(`${API_BASE}/analysis/jobs/${jobId}/summary`);
    if (!res.ok) throw new Error('Failed to get job summary');
    return res.json();
  },

  async reprocessJob(jobId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/analysis/jobs/${jobId}/reprocess`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to trigger reprocessing');
    return res.json();
  }
};
