export interface ScoringWeights {
  weight_skills: number;
  weight_semantic: number;
  weight_experience: number;
  weight_education: number;
  weight_responsibility: number;
}

export interface JobRequirement {
  id: string;
  job_id: string;
  category: 'technical_skill' | 'responsibility' | 'education' | 'experience';
  requirement_text: string;
  weight: number;
  is_mandatory: boolean;
}

export interface Job {
  id: string;
  title: string;
  description: string;
  department: string;
  location: string;
  required_experience_years: number;
  scoring_weights?: ScoringWeights;
  created_at: string;
  updated_at: string;
  requirements: JobRequirement[];
}

export interface JobSummary {
  job_id: string;
  job_title: string;
  total_resumes_uploaded: number;
  total_candidates_processed: number;
  average_match_score: number;
  strong_matches_count: number;
  moderate_matches_count: number;
  low_matches_count: number;
}

export interface ResumeStatusItem {
  id: string;
  filename: string;
  status: 'pending' | 'parsing' | 'matching' | 'completed' | 'failed';
  file_size: number;
  error_message?: string | null;
  created_at: string;
}

export interface ProcessingStatus {
  job_id: string;
  total_resumes: number;
  processed_resumes: number;
  completed_resumes: number;
  failed_resumes: number;
  pending_resumes: number;
  is_complete: boolean;
  resumes: ResumeStatusItem[];
}

export interface MatchResultItem {
  id: string;
  job_id: string;
  candidate_id: string;
  resume_id: string;
  candidate_name: string;
  overall_score: number;
  skill_score: number;
  semantic_score: number;
  experience_score: number;
  education_score: number;
  responsibility_score: number;
  status_label: 'Strong' | 'Moderate' | 'Low';
  matched_skills: string[];
  missing_skills: string[];
  related_skills: { skill: string; confidence: number }[];
  created_at: string;
}

export interface MatchEvidenceItem {
  id: string;
  dimension: string;
  requirement_text: string;
  resume_excerpt: string;
  similarity_score: number;
  explanation: string;
}

export interface CandidateDetailAnalysis {
  candidate_id: string;
  candidate_name: string;
  email?: string;
  phone?: string;
  resume_id: string;
  resume_filename: string;
  overall_score: number;
  status_label: string;
  component_scores: {
    technical_skills: number;
    semantic_similarity: number;
    relevant_experience: number;
    education: number;
    responsibilities: number;
  };
  weights_used: Record<string, number>;
  matched_skills: {
    skill: string;
    canonical: string;
    type: string;
    value: number;
    evidence: string;
  }[];
  missing_skills: string[];
  related_skills: {
    required_skill: string;
    related_skill_found: string;
    type: string;
    value: number;
    evidence: string;
  }[];
  experience_analysis: {
    calculated_years: number;
    explicit_stated_years?: number;
    final_years: number;
    detected_date_ranges: string[];
    has_overlapping_intervals: boolean;
  };
  education_analysis: {
    degree_level: number;
    degree_name: string;
    field_of_study?: string;
    evidence?: string;
  };
  evidence_items: MatchEvidenceItem[];
  why_matched: string[];
  areas_of_concern: string[];
  fairness_statement: string;
}
