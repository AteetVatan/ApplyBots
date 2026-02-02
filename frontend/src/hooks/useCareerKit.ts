/**
 * CareerKit Expert Apply hooks using TanStack Query.
 *
 * Standards: react_coding.mdc
 * - Custom hooks for reusable logic
 * - TanStack Query for server state
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";

// =============================================================================
// Types
// =============================================================================

export interface ResumeSource {
  source_type: "uploaded" | "draft";
  resume_id: string;
}

export interface CustomJD {
  title: string;
  company: string;
  description: string;
  location?: string;
  url?: string;
}

export interface AnalyzeRequest {
  job_id?: string;
  custom_jd?: CustomJD;
  resume_source: ResumeSource;
}

export interface QuestionnaireAnswer {
  question_id: string;
  answer: string | string[];
}

export interface GenerateRequest {
  session_id: string;
  answers: QuestionnaireAnswer[];
}

export interface Requirement {
  name: string;
  level: "must" | "nice";
  category: string;
  keywords: string[];
  original_text?: string;
}

export interface Evidence {
  source: string;
  quote: string;
  cv_section?: string;
}

export interface GapMapItem {
  requirement_name: string;
  status: "covered" | "partial" | "missing" | "unclear";
  evidence: Evidence[];
  risk_note?: string;
  question_needed: boolean;
}

export interface Question {
  id: string;
  topic: string;
  question: string;
  answer_type: "text" | "yes_no" | "scale" | "multi_select";
  why_asked: string;
  options?: string[];
}

export interface Bullet {
  text: string;
  confidence_score: "high" | "medium" | "low";
  source_ref?: string;
  needs_verification: boolean;
}

export interface DeltaInstruction {
  bullet_id: string;
  action: "keep" | "rewrite" | "remove" | "add";
  original_text?: string;
  new_text?: string;
  confidence_score: "high" | "medium" | "low";
  reason?: string;
}

export interface TailoredCV {
  targeted_title: string;
  summary: string;
  skills: string[];
  experience_bullets: Record<string, Bullet[]>;
  projects: Bullet[];
  education: string[];
  truth_notes: string[];
}

export interface STARStory {
  title: string;
  situation: string;
  task: string;
  action: string;
  result: string;
  applicable_to: string[];
}

export interface InterviewQuestion {
  question: string;
  category: string;
  difficulty: "easy" | "medium" | "hard";
  suggested_answer?: string;
}

export interface PrepPlanDay {
  day: number;
  focus: string;
  tasks: string[];
  time_estimate_minutes: number;
}

export interface InterviewPrep {
  role_understanding: string;
  likely_questions: InterviewQuestion[];
  suggested_answers: Record<string, string>;
  story_bank: STARStory[];
  tech_deep_dive_topics: string[];
  seven_day_prep_plan: PrepPlanDay[];
}

export interface AnalyzeResponse {
  session_id: string;
  session_name: string;
  phase: "analyze" | "questionnaire" | "generate" | "complete";
  is_custom_job: boolean;
  requirements: Requirement[];
  gap_map: GapMapItem[];
  questionnaire: Question[];
  tailored_cv: TailoredCV | null;
  interview_prep: InterviewPrep | null;
}

export interface GenerateResponse {
  session_id: string;
  session_name: string;
  phase: "analyze" | "questionnaire" | "generate" | "complete";
  is_custom_job: boolean;
  requirements: Requirement[];
  gap_map: GapMapItem[];
  questionnaire: Question[];
  delta_instructions: DeltaInstruction[];
  tailored_cv: TailoredCV;
  generated_cv_draft_id?: string;
  interview_prep: InterviewPrep;
}

export interface ResumeOption {
  id: string;
  name: string;
  source_type: "uploaded" | "draft";
  is_primary: boolean;
  updated_at?: string;
  preview?: string;
}

export interface AvailableResumes {
  uploaded_resumes: ResumeOption[];
  builder_drafts: ResumeOption[];
}

export interface SessionSummary {
  id: string;
  session_name: string;
  phase: string;
  is_custom_job: boolean;
  job_title: string;
  company: string;
  created_at: string;
  updated_at?: string;
}

export interface SessionListResponse {
  items: SessionSummary[];
  total: number;
}

// =============================================================================
// API Client
// =============================================================================

const careerKitApi = {
  getResumes: async (): Promise<AvailableResumes> => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/career-kit/resumes`, {
      credentials: "include",
    });
    if (!response.ok) throw new Error("Failed to fetch resumes");
    return response.json();
  },

  analyze: async (request: AnalyzeRequest): Promise<AnalyzeResponse> => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/career-kit/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Analysis failed" }));
      throw new Error(error.detail || "Analysis failed");
    }
    return response.json();
  },

  generate: async (request: GenerateRequest): Promise<GenerateResponse> => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/career-kit/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Generation failed" }));
      throw new Error(error.detail || "Generation failed");
    }
    return response.json();
  },

  getSessions: async (): Promise<SessionListResponse> => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/career-kit/sessions`, {
      credentials: "include",
    });
    if (!response.ok) throw new Error("Failed to fetch sessions");
    return response.json();
  },

  getSession: async (sessionId: string): Promise<AnalyzeResponse> => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/career-kit/sessions/${sessionId}`, {
      credentials: "include",
    });
    if (!response.ok) throw new Error("Failed to fetch session");
    return response.json();
  },

  saveAnswers: async (sessionId: string, answers: QuestionnaireAnswer[]): Promise<void> => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/career-kit/sessions/${sessionId}/answers`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ answers }),
    });
    if (!response.ok) throw new Error("Failed to save answers");
  },

  deleteSession: async (sessionId: string): Promise<void> => {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/career-kit/sessions/${sessionId}`, {
      method: "DELETE",
      credentials: "include",
    });
    if (!response.ok) throw new Error("Failed to delete session");
  },
};

// =============================================================================
// Hooks
// =============================================================================

/**
 * Fetch available resumes for selection.
 */
export function useCareerKitResumes() {
  return useQuery({
    queryKey: ["careerkit", "resumes"],
    queryFn: careerKitApi.getResumes,
  });
}

/**
 * Phase 1: Analyze JD vs CV.
 */
export function useAnalyze() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerKitApi.analyze,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["careerkit", "sessions"] });
    },
  });
}

/**
 * Phase 2: Generate tailored CV and interview prep.
 */
export function useGenerate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerKitApi.generate,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["careerkit", "sessions"] });
      queryClient.setQueryData(["careerkit", "session", data.session_id], data);
    },
  });
}

/**
 * Fetch user's CareerKit sessions.
 */
export function useCareerKitSessions() {
  return useQuery({
    queryKey: ["careerkit", "sessions"],
    queryFn: careerKitApi.getSessions,
  });
}

/**
 * Fetch a specific session.
 */
export function useCareerKitSession(sessionId: string | null) {
  return useQuery({
    queryKey: ["careerkit", "session", sessionId],
    queryFn: () => (sessionId ? careerKitApi.getSession(sessionId) : null),
    enabled: !!sessionId,
  });
}

/**
 * Auto-save questionnaire answers.
 */
export function useSaveAnswers(sessionId: string) {
  return useMutation({
    mutationFn: (answers: QuestionnaireAnswer[]) =>
      careerKitApi.saveAnswers(sessionId, answers),
  });
}

/**
 * Delete a session.
 */
export function useDeleteSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: careerKitApi.deleteSession,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["careerkit", "sessions"] });
    },
  });
}
