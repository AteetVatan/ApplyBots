/**
 * Hook for real-time ATS score calculation with debouncing.
 *
 * Features:
 * - Debounced calculation (500ms delay)
 * - Calls backend ATS scoring endpoint
 * - Manages loading and error states
 * - Returns detailed breakdown
 */

"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import type { ResumeContent } from "@/stores/resume-builder-store";

export interface ScoreBreakdown {
  keywordMatch: { score: number; max: number };
  formatting: { score: number; max: number };
  sectionCompleteness: { score: number; max: number };
  quantifiedAchievements: { score: number; max: number };
  length: { score: number; max: number };
  contactInfo: { score: number; max: number };
}

export interface ATSScoreResult {
  totalScore: number;
  breakdown: ScoreBreakdown;
  matchedKeywords: string[];
  missingKeywords: string[];
  suggestions: string[];
}

interface UseATSScoreOptions {
  debounceMs?: number;
  autoCalculate?: boolean;
  jobDescription?: string;
}

interface UseATSScoreReturn {
  result: ATSScoreResult | null;
  isCalculating: boolean;
  error: string | null;
  calculate: () => Promise<void>;
  setJobDescription: (jd: string) => void;
}

// ATS scoring weights (matching backend)
const ATS_WEIGHTS = {
  keywordMatch: 30,
  formatting: 20,
  sectionCompleteness: 20,
  quantifiedAchievements: 15,
  length: 10,
  contactInfo: 5,
};

/**
 * Calculate ATS score locally (client-side fallback).
 * This mirrors the backend logic for instant feedback.
 */
function calculateLocalATSScore(
  content: ResumeContent,
  jobDescription?: string
): ATSScoreResult {
  // Keyword match (30 points)
  let keywordScore = 0;
  const matchedKeywords: string[] = [];
  const missingKeywords: string[] = [];
  
  if (jobDescription && jobDescription.trim()) {
    // Extract keywords from job description (simplified)
    const jdWords = jobDescription.toLowerCase().match(/\b[a-z]{3,}\b/g) || [];
    const uniqueJdWords = [...new Set(jdWords)].filter(
      (w) => !["the", "and", "for", "are", "this", "that", "with", "from", "have", "been", "will", "your"].includes(w)
    );
    
    // Check resume content for keywords
    const resumeText = [
      content.fullName,
      content.professionalSummary,
      ...content.workExperience.flatMap((e) => [e.title, e.company, e.description, ...e.achievements]),
      ...content.education.map((e) => `${e.degree} ${e.fieldOfStudy} ${e.institution}`),
      ...content.skills.technical.flatMap((g) => g.items),
      ...content.skills.soft,
      ...content.skills.custom.flatMap((g) => g.items),
      ...content.skills.tools,
      ...content.projects.flatMap((p) => [p.name, p.description, ...p.technologies]),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    
    uniqueJdWords.slice(0, 20).forEach((kw) => {
      if (resumeText.includes(kw)) {
        matchedKeywords.push(kw);
      } else {
        missingKeywords.push(kw);
      }
    });
    
    const matchRate = uniqueJdWords.length > 0 
      ? matchedKeywords.length / Math.min(uniqueJdWords.length, 20) 
      : 0.5;
    keywordScore = Math.round(matchRate * ATS_WEIGHTS.keywordMatch);
  } else {
    // Without job description, give partial credit based on common tech keywords
    const commonKeywords = ["experience", "skills", "team", "project", "development", "management"];
    const resumeText = content.professionalSummary?.toLowerCase() || "";
    const hasKeywords = commonKeywords.filter((kw) => resumeText.includes(kw)).length;
    keywordScore = Math.round((hasKeywords / commonKeywords.length) * ATS_WEIGHTS.keywordMatch * 0.7);
  }

  // Formatting (20 points) - clean structure
  let formattingScore = ATS_WEIGHTS.formatting;
  // Deduct for missing structure
  if (!content.professionalSummary) formattingScore -= 5;
  if (content.workExperience.length === 0) formattingScore -= 5;

  // Section completeness (20 points)
  let sectionScore = 0;
  if (content.fullName && content.email) sectionScore += 5;
  if (content.workExperience.length > 0) sectionScore += 5;
  if (content.education.length > 0) sectionScore += 5;
  if (content.skills.technical.length > 0 || content.skills.soft.length > 0) {
    sectionScore += 5;
  }

  // Quantified achievements (15 points)
  let quantifiedScore = 0;
  const achievements = content.workExperience.flatMap((e) => e.achievements);
  const numberedAchievements = achievements.filter((a) => /\d+%?|\$[\d,]+|\d+[kKmM]/.test(a));
  if (achievements.length > 0) {
    quantifiedScore = Math.round(
      (numberedAchievements.length / achievements.length) * ATS_WEIGHTS.quantifiedAchievements
    );
  }

  // Length (10 points)
  let lengthScore = ATS_WEIGHTS.length;
  const totalText = [
    content.professionalSummary,
    ...content.workExperience.flatMap((e) => e.achievements),
  ]
    .filter(Boolean)
    .join(" ");
  const wordCount = totalText.split(/\s+/).length;
  if (wordCount < 150) lengthScore = 3;
  else if (wordCount < 300) lengthScore = 7;
  else if (wordCount > 1000) lengthScore = 5;

  // Contact info (5 points)
  let contactScore = 0;
  if (content.fullName) contactScore += 2;
  if (content.email) contactScore += 2;
  if (content.phone) contactScore += 1;

  const totalScore = Math.min(
    100,
    keywordScore + formattingScore + sectionScore + quantifiedScore + lengthScore + contactScore
  );

  // Generate suggestions
  const suggestions: string[] = [];
  if (keywordScore < ATS_WEIGHTS.keywordMatch * 0.7) {
    if (missingKeywords.length > 0) {
      suggestions.push(`Add keywords: ${missingKeywords.slice(0, 5).join(", ")}`);
    } else {
      suggestions.push("Add a job description to get keyword suggestions");
    }
  }
  if (formattingScore < ATS_WEIGHTS.formatting) {
    if (!content.professionalSummary) {
      suggestions.push("Add a professional summary");
    }
  }
  if (sectionScore < ATS_WEIGHTS.sectionCompleteness) {
    if (content.workExperience.length === 0) {
      suggestions.push("Add work experience");
    }
    if (content.education.length === 0) {
      suggestions.push("Add education history");
    }
    if (content.skills.technical.length === 0 || content.skills.technical.every((g) => g.items.length === 0)) {
      suggestions.push("Add technical skills");
    }
  }
  if (quantifiedScore < ATS_WEIGHTS.quantifiedAchievements * 0.6 && achievements.length > 0) {
    suggestions.push("Add numbers/percentages to achievements (e.g., 'Increased sales by 25%')");
  }
  if (lengthScore < ATS_WEIGHTS.length * 0.7) {
    suggestions.push("Add more detail - resume may be too short or too long");
  }
  if (contactScore < ATS_WEIGHTS.contactInfo) {
    suggestions.push("Complete contact information (name, email, phone)");
  }

  return {
    totalScore,
    breakdown: {
      keywordMatch: { score: keywordScore, max: ATS_WEIGHTS.keywordMatch },
      formatting: { score: formattingScore, max: ATS_WEIGHTS.formatting },
      sectionCompleteness: { score: sectionScore, max: ATS_WEIGHTS.sectionCompleteness },
      quantifiedAchievements: { score: quantifiedScore, max: ATS_WEIGHTS.quantifiedAchievements },
      length: { score: lengthScore, max: ATS_WEIGHTS.length },
      contactInfo: { score: contactScore, max: ATS_WEIGHTS.contactInfo },
    },
    matchedKeywords,
    missingKeywords,
    suggestions,
  };
}

export function useATSScore(
  content: ResumeContent,
  options: UseATSScoreOptions = {}
): UseATSScoreReturn {
  const { debounceMs = 500, autoCalculate = true, jobDescription: initialJd = "" } = options;

  const [result, setResult] = useState<ATSScoreResult | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobDescription, setJobDescription] = useState(initialJd);

  const debounceRef = useRef<NodeJS.Timeout>();
  const contentRef = useRef(content);
  contentRef.current = content;

  const calculate = useCallback(async () => {
    setIsCalculating(true);
    setError(null);

    try {
      // Get auth token
      const token = typeof window !== "undefined" 
        ? localStorage.getItem("ApplyBots_access_token") 
        : null;

      // Build headers
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      // Convert content to snake_case for backend API
      const c = contentRef.current;
      const apiContent = {
        full_name: c.fullName,
        email: c.email,
        phone: c.phone,
        location: c.location,
        linkedin_url: c.linkedinUrl,
        portfolio_url: c.portfolioUrl,
        github_url: c.githubUrl,
        profile_picture_url: c.profilePictureUrl,
        custom_links: c.customLinks.map((link) => ({
          id: link.id,
          label: link.label,
          url: link.url,
        })),
        professional_summary: c.professionalSummary,
        work_experience: c.workExperience.map((exp) => ({
          company: exp.company,
          title: exp.title,
          start_date: exp.startDate,
          end_date: exp.endDate,
          description: exp.description,
          achievements: exp.achievements,
          location: exp.location,
          is_current: exp.isCurrent,
        })),
        education: c.education.map((edu) => ({
          institution: edu.institution,
          degree: edu.degree,
          field_of_study: edu.fieldOfStudy,
          graduation_date: edu.graduationDate,
          gpa: edu.gpa,
          location: edu.location,
          achievements: edu.achievements,
        })),
        skills: {
          technical: c.skills.technical.flatMap((g) => g.items),
          soft: c.skills.soft,
          tools: c.skills.tools,
        },
        projects: c.projects.map((proj) => ({
          name: proj.name,
          description: proj.description,
          url: proj.url,
          technologies: proj.technologies,
          start_date: proj.startDate,
          end_date: proj.endDate,
          highlights: proj.highlights,
        })),
        certifications: c.certifications.map((cert) => ({
          name: cert.name,
          issuer: cert.issuer,
          date: cert.date,
          expiry_date: cert.expiryDate,
          credential_id: cert.credentialId,
          url: cert.url,
        })),
        awards: c.awards.map((award) => ({
          title: award.title,
          issuer: award.issuer,
          date: award.date,
          description: award.description,
        })),
        languages: c.languages.map((lang) => ({
          language: lang.language,
          proficiency: lang.proficiency,
        })),
        custom_sections: c.customSections.map((cs) => ({
          id: cs.id,
          title: cs.title,
          items: cs.items,
        })),
        template_id: c.templateId || "professional-modern",
        section_order: c.sectionOrder,
        ats_score: c.atsScore,
      };

      // Try backend API first
      const response = await fetch("/api/v1/resume-builder/ats-score", {
        method: "POST",
        headers,
        body: JSON.stringify({
          content: apiContent,
          job_description: jobDescription || null,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setResult({
          totalScore: data.total_score,
          breakdown: {
            keywordMatch: { score: data.keyword_match_score, max: 30 },
            formatting: { score: data.formatting_score, max: 20 },
            sectionCompleteness: { score: data.section_completeness_score, max: 20 },
            quantifiedAchievements: { score: data.quantified_achievements_score, max: 15 },
            length: { score: data.length_score, max: 10 },
            contactInfo: { score: data.contact_info_score, max: 5 },
          },
          matchedKeywords: data.matched_keywords || [],
          missingKeywords: data.missing_keywords || [],
          suggestions: data.suggestions || [],
        });
      } else {
        // Fallback to local calculation
        const localResult = calculateLocalATSScore(contentRef.current, jobDescription);
        setResult(localResult);
      }
    } catch {
      // Fallback to local calculation on error
      const localResult = calculateLocalATSScore(contentRef.current, jobDescription);
      setResult(localResult);
    } finally {
      setIsCalculating(false);
    }
  }, [jobDescription]);

  // Auto-calculate with debounce
  useEffect(() => {
    if (!autoCalculate) return;

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      calculate();
    }, debounceMs);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [content, autoCalculate, debounceMs, calculate]);

  return {
    result,
    isCalculating,
    error,
    calculate,
    setJobDescription,
  };
}
