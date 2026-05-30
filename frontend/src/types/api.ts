// Mirrors backend Pydantic DTOs.

export type Role = "user" | "recruiter" | "admin";

export interface Me {
  id: string;
  email: string;
  full_name: string;
  role: Role;
  profile: Record<string, unknown>;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ATSBreakdown {
  score: number;
  section_completeness: number;
  contact_info: number;
  length: number;
  skill_density: number;
  jd_match: number;
}

export interface ResumeAnalysis {
  id: string;
  file_name: string;
  ats: ATSBreakdown;
  skills: string[];
  missing_skills: string[];
  quality_notes: string[];
  suggestions: string[];
  predicted_role?: string | null;
  created_at: string;
}

export interface ResumeListItem {
  id: string;
  file_name: string;
  ats_score: number | null;
  created_at: string;
}

export type Algo = "bm25" | "word2vec" | "bert";

export interface RankedCandidate {
  resume_id: string;
  file_name: string;
  bm25: number | null;
  word2vec: number | null;
  bert: number | null;
  composite: number;
  is_good_fit: boolean | null;
  explanation: string | null;
}

export interface RankingResponse {
  job_match_id: string;
  job_title: string;
  algorithms: string[];
  ranked: RankedCandidate[];
  created_at: string;
}

export interface AnalyticsSummary {
  total_resumes: number;
  average_ats: number;
  top_skills: { skill: string; count: number }[];
  ats_trend: { date: string; score: number }[];
}

export interface MLPerformance {
  model_name: string;
  algorithm: string;
  vectorizer: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  train_size: number;
  test_size: number;
  num_classes: number;
  created_at: string;
  metrics: { metric: string; value: number }[];
}

// --- Interview ---
export interface InterviewQuestion {
  question: string;
  category: string;          // technical | behavioral | system_design
  expected_topics: string[];
  answer?: string;
  score?: number;
  feedback?: string;
}

export interface InterviewSession {
  interview_id: string;
  questions: InterviewQuestion[];
}

export interface AnswerResult {
  score: number;
  feedback: string;
  strengths: string[];
  improvements: string[];
}

// --- Good Fit ML Pipeline ---
export interface GoodFitMetricsSummary {
  id: string;
  model_name: string;
  algorithm: string;
  dataset_size: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  roc_auc: number;
  created_at: string;
}

export interface GoodFitMetrics extends GoodFitMetricsSummary {
  train_size: number;
  test_size: number;
  feature_count: number;
  confusion_matrix: number[][];
  roc_curve: { fpr: number[]; tpr: number[] };
  cv_mean: number;
  cv_std: number;
  cleaning_stats: Record<string, number>;
  feature_info: Record<string, number>;
  metrics: { metric: string; value: number }[];
}

// --- Roadmap ---
export interface RoadmapMilestone {
  week: number;
  title: string;
  description: string;
  skills: string[];
}

export interface RoadmapResource {
  title: string;
  url: string;
  type: string;
}

export interface RoadmapPlan {
  id: string;
  target_role: string;
  skill_gaps: string[];
  milestones: RoadmapMilestone[];
  resources: RoadmapResource[];
}
