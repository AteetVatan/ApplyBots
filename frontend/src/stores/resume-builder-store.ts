/**
 * Zustand store for resume builder state management.
 *
 * Standards: react_nextjs.mdc
 * - Zustand for global state
 * - Immer for immutable updates
 * - TypeScript strict mode
 */

import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { devtools, persist } from "zustand/middleware";

// ============================================================================
// Types
// ============================================================================

export interface WorkExperience {
  id: string;
  company: string;
  title: string;
  startDate: string | null;
  endDate: string | null;
  description: string | null;
  achievements: string[];
  location: string | null;
  isCurrent: boolean;
}

export interface Education {
  id: string;
  institution: string;
  degree: string;
  fieldOfStudy: string | null;
  graduationDate: string | null;
  gpa: number | null;
  location: string | null;
  achievements: string[];
}

export interface Project {
  id: string;
  name: string;
  description: string;
  url: string | null;
  technologies: string[];
  startDate: string | null;
  endDate: string | null;
  highlights: string[];
}

export interface Award {
  id: string;
  title: string;
  issuer: string;
  date: string | null;
  description: string | null;
}

export interface Certification {
  id: string;
  name: string;
  issuer: string;
  date: string | null;
  expiryDate: string | null;
  credentialId: string | null;
  url: string | null;
}

export interface LanguageSkill {
  id: string;
  language: string;
  proficiency: "native" | "fluent" | "conversational" | "basic";
}

export interface TechnicalSkillGroup {
  id: string;
  header: string;
  items: string[];
}

export interface SkillsSection {
  technical: TechnicalSkillGroup[];
  soft: string[];
  tools: string[];
  custom: TechnicalSkillGroup[];
  customSkillsHeader: string; // Editable header for the Custom Skills section
}

export interface CustomSection {
  id: string;
  title: string;
  items: string[];
}

export interface CustomLink {
  id: string;
  label: string;
  url: string;
}

export interface ResumeContent {
  // Contact
  fullName: string;
  email: string;
  phone: string | null;
  location: string | null;
  linkedinUrl: string | null;
  portfolioUrl: string | null;
  githubUrl: string | null;
  profilePictureUrl: string | null;
  customLinks: CustomLink[];

  // Summary
  professionalSummary: string | null;

  // Sections
  workExperience: WorkExperience[];
  education: Education[];
  skills: SkillsSection;
  projects: Project[];
  certifications: Certification[];
  awards: Award[];
  languages: LanguageSkill[];
  customSections: CustomSection[];

  // Metadata
  templateId: string;
  sectionOrder: string[];
  atsScore: number | null;
}

export type SectionKey =
  | "contact"
  | "summary"
  | "experience"
  | "education"
  | "skills"
  | "softSkills"
  | "customSkills"
  | "projects"
  | "certifications"
  | "awards"
  | "languages"
  | "custom";

// Theme customization settings
export interface ThemeSettings {
  primaryColor: string;
  fontFamily: string;
  fontSize: "small" | "medium" | "large";
  spacing: "compact" | "normal" | "spacious";
  pageSize: "a4" | "letter";
}

// Detailed ATS score breakdown
export interface DetailedATSScore {
  total: number;
  breakdown: {
    keywordMatch: { score: number; max: number };
    formatting: { score: number; max: number };
    sectionCompleteness: { score: number; max: number };
    quantifiedAchievements: { score: number; max: number };
    length: { score: number; max: number };
    contactInfo: { score: number; max: number };
  };
  matchedKeywords: string[];
  missingKeywords: string[];
  suggestions: string[];
  isCalculating: boolean;
  jobDescription: string;
}

// Sharing settings
export interface ShareSettings {
  isPublic: boolean;
  shareId: string | null;
  shareUrl: string | null;
}

// Default theme settings
const DEFAULT_THEME_SETTINGS: ThemeSettings = {
  primaryColor: "#3b82f6",
  fontFamily: "Inter",
  fontSize: "medium",
  spacing: "normal",
  pageSize: "letter",
};

// Default ATS score state
const DEFAULT_ATS_SCORE: DetailedATSScore = {
  total: 0,
  breakdown: {
    keywordMatch: { score: 0, max: 30 },
    formatting: { score: 0, max: 20 },
    sectionCompleteness: { score: 0, max: 20 },
    quantifiedAchievements: { score: 0, max: 15 },
    length: { score: 0, max: 10 },
    contactInfo: { score: 0, max: 5 },
  },
  matchedKeywords: [],
  missingKeywords: [],
  suggestions: [],
  isCalculating: false,
  jobDescription: "",
};

// Default share settings
const DEFAULT_SHARE_SETTINGS: ShareSettings = {
  isPublic: false,
  shareId: null,
  shareUrl: null,
};

interface ResumeBuilderState {
  // Draft data
  draftId: string | null;
  draftName: string;
  content: ResumeContent;
  templateId: string;
  atsScore: number | null;

  // Theme customization
  themeSettings: ThemeSettings;

  // Detailed ATS scoring
  detailedAtsScore: DetailedATSScore;

  // Sharing
  shareSettings: ShareSettings;

  // UI state
  activeSection: SectionKey;
  previewScale: number;
  isDirty: boolean;
  isSaving: boolean;
  lastSaved: Date | null;
  isAIDrawerOpen: boolean;
  isATSPanelVisible: boolean;

  // History for undo/redo
  history: ResumeContent[];
  historyIndex: number;
  maxHistoryLength: number;

  // Actions
  setDraftId: (id: string | null) => void;
  setDraftName: (name: string) => void;
  setContent: (content: ResumeContent) => void;
  setTemplateId: (templateId: string) => void;
  setActiveSection: (section: SectionKey) => void;
  setPreviewScale: (scale: number) => void;
  setAIDrawerOpen: (open: boolean) => void;
  setATSPanelVisible: (visible: boolean) => void;
  setATSScore: (score: number | null) => void;

  // Theme settings actions
  setThemeSettings: (settings: Partial<ThemeSettings>) => void;
  resetThemeSettings: () => void;

  // Detailed ATS score actions
  setDetailedATSScore: (score: Partial<DetailedATSScore>) => void;
  setATSJobDescription: (jd: string) => void;
  setATSCalculating: (calculating: boolean) => void;

  // Share settings actions
  setShareSettings: (settings: Partial<ShareSettings>) => void;

  // Content update actions
  updateContact: (data: Partial<Pick<ResumeContent, "fullName" | "email" | "phone" | "location" | "linkedinUrl" | "portfolioUrl" | "githubUrl" | "profilePictureUrl">>) => void;
  updateSummary: (summary: string | null) => void;
  updateSkills: (skills: SkillsSection) => void;
  updateSectionOrder: (order: string[]) => void;

  // Work experience actions
  addWorkExperience: (experience: Omit<WorkExperience, "id">) => void;
  updateWorkExperience: (id: string, data: Partial<WorkExperience>) => void;
  removeWorkExperience: (id: string) => void;
  reorderWorkExperience: (fromIndex: number, toIndex: number) => void;

  // Education actions
  addEducation: (education: Omit<Education, "id">) => void;
  updateEducation: (id: string, data: Partial<Education>) => void;
  removeEducation: (id: string) => void;
  reorderEducation: (fromIndex: number, toIndex: number) => void;

  // Project actions
  addProject: (project: Omit<Project, "id">) => void;
  updateProject: (id: string, data: Partial<Project>) => void;
  removeProject: (id: string) => void;
  reorderProjects: (fromIndex: number, toIndex: number) => void;

  // Certification actions
  addCertification: (certification: Omit<Certification, "id">) => void;
  updateCertification: (id: string, data: Partial<Certification>) => void;
  removeCertification: (id: string) => void;

  // Award actions
  addAward: (award: Omit<Award, "id">) => void;
  updateAward: (id: string, data: Partial<Award>) => void;
  removeAward: (id: string) => void;

  // Language actions
  addLanguage: (language: Omit<LanguageSkill, "id">) => void;
  updateLanguage: (id: string, data: Partial<LanguageSkill>) => void;
  removeLanguage: (id: string) => void;

  // Custom section actions
  addCustomSection: (title: string) => void;
  updateCustomSection: (id: string, data: Partial<CustomSection>) => void;
  removeCustomSection: (id: string) => void;

  // Custom link actions
  addCustomLink: (link: Omit<CustomLink, "id">) => void;
  updateCustomLink: (id: string, data: Partial<CustomLink>) => void;
  removeCustomLink: (id: string) => void;

  // History actions
  undo: () => void;
  redo: () => void;
  canUndo: () => boolean;
  canRedo: () => boolean;
  pushToHistory: () => void;

  // Save state
  markDirty: () => void;
  markSaved: () => void;
  setSaving: (saving: boolean) => void;

  // Reset
  reset: () => void;
  loadDraft: (draft: { id: string; name: string; content: ResumeContent; templateId: string; atsScore: number | null }) => void;
}

// ============================================================================
// Default values
// ============================================================================

const DEFAULT_SECTION_ORDER: string[] = [
  "contact",
  "summary",
  "experience",
  "education",
  "skills",
  "softSkills",
  "customSkills",
  "projects",
  "certifications",
  "awards",
  "languages",
];

const createDefaultContent = (): ResumeContent => ({
  fullName: "",
  email: "",
  phone: null,
  location: null,
  linkedinUrl: null,
  portfolioUrl: null,
  githubUrl: null,
  profilePictureUrl: null,
  customLinks: [],
  professionalSummary: null,
  workExperience: [],
  education: [],
  skills: { technical: [], soft: [], tools: [], custom: [] as TechnicalSkillGroup[], customSkillsHeader: "Custom Skills" },
  projects: [],
  certifications: [],
  awards: [],
  languages: [],
  customSections: [],
  templateId: "bronzor",
  sectionOrder: DEFAULT_SECTION_ORDER,
  atsScore: null,
});

// ============================================================================
// Helper functions
// ============================================================================

const generateId = () => crypto.randomUUID();

// Helper to migrate old technical skills format (string[]) to new format (TechnicalSkillGroup[])
const migrateTechnicalSkills = (technical: unknown): TechnicalSkillGroup[] => {
  if (Array.isArray(technical)) {
    // Check if it's the old format (string[])
    if (technical.length > 0 && typeof technical[0] === "string") {
      // Migrate: create a single group with all skills
      return [{
        id: generateId(),
        header: "Technical Skills",
        items: technical as string[],
      }];
    }
    // Already in new format
    return technical as TechnicalSkillGroup[];
  }
  return [];
};

// Helper to migrate old custom skills format (string[]) to new format (TechnicalSkillGroup[])
const migrateCustomSkills = (custom: unknown): TechnicalSkillGroup[] => {
  if (Array.isArray(custom)) {
    // Check if it's the old format (string[])
    if (custom.length > 0 && typeof custom[0] === "string") {
      // Migrate: create a single group with all skills
      return [{
        id: generateId(),
        header: "Custom Skills",
        items: custom as string[],
      }];
    }
    // Already in new format (TechnicalSkillGroup[])
    if (custom.length > 0 && typeof custom[0] === "object" && "id" in custom[0] && "header" in custom[0]) {
      return custom as TechnicalSkillGroup[];
    }
  }
  return [];
};

const reorderArray = <T>(array: T[], fromIndex: number, toIndex: number): T[] => {
  const result = [...array];
  const [removed] = result.splice(fromIndex, 1);
  result.splice(toIndex, 0, removed);
  return result;
};

// ============================================================================
// Store
// ============================================================================

export const useResumeBuilderStore = create<ResumeBuilderState>()(
  devtools(
    persist(
      immer((set, get) => {
        // Helper to ensure customLinks exists
        const ensureCustomLinks = (content: ResumeContent): ResumeContent => ({
          ...content,
          customLinks: content.customLinks || [],
        });

        return {
        // Initial state
        draftId: null,
        draftName: "Untitled Resume",
        content: createDefaultContent(),
        templateId: "bronzor",
        atsScore: null,
        themeSettings: DEFAULT_THEME_SETTINGS,
        detailedAtsScore: DEFAULT_ATS_SCORE,
        shareSettings: DEFAULT_SHARE_SETTINGS,
        activeSection: "contact",
        previewScale: 0.75,
        isDirty: false,
        isSaving: false,
        lastSaved: null,
        isAIDrawerOpen: false,
        isATSPanelVisible: false,
        history: [],
        historyIndex: -1,
        maxHistoryLength: 50,

        // Basic setters
        setDraftId: (id) => set((state) => { state.draftId = id; }),
        setDraftName: (name) => set((state) => { state.draftName = name; state.isDirty = true; }),
        setContent: (content) => set((state) => {
          state.content = content;
          state.isDirty = true;
        }),
        setTemplateId: (templateId) => set((state) => {
          state.templateId = templateId;
          state.content.templateId = templateId;
          state.isDirty = true;
        }),
        setActiveSection: (section) => set((state) => { state.activeSection = section; }),
        setPreviewScale: (scale) => set((state) => { state.previewScale = scale; }),
        setAIDrawerOpen: (open) => set((state) => { state.isAIDrawerOpen = open; }),
        setATSPanelVisible: (visible) => set((state) => { state.isATSPanelVisible = visible; }),
        setATSScore: (score) => set((state) => {
          state.atsScore = score;
          state.content.atsScore = score;
        }),

        // Theme settings actions
        setThemeSettings: (settings) => set((state) => {
          state.themeSettings = { ...state.themeSettings, ...settings };
          state.isDirty = true;
        }),
        resetThemeSettings: () => set((state) => {
          state.themeSettings = DEFAULT_THEME_SETTINGS;
          state.isDirty = true;
        }),

        // Detailed ATS score actions
        setDetailedATSScore: (score) => set((state) => {
          state.detailedAtsScore = { ...state.detailedAtsScore, ...score };
          if (score.total !== undefined) {
            state.atsScore = score.total;
            state.content.atsScore = score.total;
          }
        }),
        setATSJobDescription: (jd) => set((state) => {
          state.detailedAtsScore.jobDescription = jd;
        }),
        setATSCalculating: (calculating) => set((state) => {
          state.detailedAtsScore.isCalculating = calculating;
        }),

        // Share settings actions
        setShareSettings: (settings) => set((state) => {
          state.shareSettings = { ...state.shareSettings, ...settings };
        }),

        // Contact update
        updateContact: (data) => set((state) => {
          get().pushToHistory();
          Object.assign(state.content, data);
          state.isDirty = true;
        }),

        // Summary update
        updateSummary: (summary) => set((state) => {
          get().pushToHistory();
          state.content.professionalSummary = summary;
          state.isDirty = true;
        }),

        // Skills update
        updateSkills: (skills) => set((state) => {
          get().pushToHistory();
          state.content.skills = skills;
          state.isDirty = true;
        }),

        // Section order
        updateSectionOrder: (order) => set((state) => {
          state.content.sectionOrder = order;
          state.isDirty = true;
        }),

        // Work experience
        addWorkExperience: (experience) => set((state) => {
          get().pushToHistory();
          state.content.workExperience.push({ ...experience, id: generateId() });
          state.isDirty = true;
        }),
        updateWorkExperience: (id, data) => set((state) => {
          get().pushToHistory();
          const index = state.content.workExperience.findIndex((e) => e.id === id);
          if (index !== -1) {
            Object.assign(state.content.workExperience[index], data);
            state.isDirty = true;
          }
        }),
        removeWorkExperience: (id) => set((state) => {
          get().pushToHistory();
          state.content.workExperience = state.content.workExperience.filter((e) => e.id !== id);
          state.isDirty = true;
        }),
        reorderWorkExperience: (fromIndex, toIndex) => set((state) => {
          get().pushToHistory();
          state.content.workExperience = reorderArray(state.content.workExperience, fromIndex, toIndex);
          state.isDirty = true;
        }),

        // Education
        addEducation: (education) => set((state) => {
          get().pushToHistory();
          state.content.education.push({ ...education, id: generateId() });
          state.isDirty = true;
        }),
        updateEducation: (id, data) => set((state) => {
          get().pushToHistory();
          const index = state.content.education.findIndex((e) => e.id === id);
          if (index !== -1) {
            Object.assign(state.content.education[index], data);
            state.isDirty = true;
          }
        }),
        removeEducation: (id) => set((state) => {
          get().pushToHistory();
          state.content.education = state.content.education.filter((e) => e.id !== id);
          state.isDirty = true;
        }),
        reorderEducation: (fromIndex, toIndex) => set((state) => {
          get().pushToHistory();
          state.content.education = reorderArray(state.content.education, fromIndex, toIndex);
          state.isDirty = true;
        }),

        // Projects
        addProject: (project) => set((state) => {
          get().pushToHistory();
          state.content.projects.push({ ...project, id: generateId() });
          state.isDirty = true;
        }),
        updateProject: (id, data) => set((state) => {
          get().pushToHistory();
          const index = state.content.projects.findIndex((p) => p.id === id);
          if (index !== -1) {
            Object.assign(state.content.projects[index], data);
            state.isDirty = true;
          }
        }),
        removeProject: (id) => set((state) => {
          get().pushToHistory();
          state.content.projects = state.content.projects.filter((p) => p.id !== id);
          state.isDirty = true;
        }),
        reorderProjects: (fromIndex, toIndex) => set((state) => {
          get().pushToHistory();
          state.content.projects = reorderArray(state.content.projects, fromIndex, toIndex);
          state.isDirty = true;
        }),

        // Certifications
        addCertification: (certification) => set((state) => {
          get().pushToHistory();
          state.content.certifications.push({ ...certification, id: generateId() });
          state.isDirty = true;
          // #region agent log
          fetch('http://127.0.0.1:7242/ingest/478687fd-7ff3-4069-9a5d-c1e34f5138df',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'resume-builder-store.ts:569',message:'addCertification called',data:{certificationCount:state.content.certifications.length,certificationIds:state.content.certifications.map(c=>c.id),newCertId:state.content.certifications[state.content.certifications.length-1]?.id},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A,E'})}).catch(()=>{});
          // #endregion
        }),
        updateCertification: (id, data) => set((state) => {
          get().pushToHistory();
          const index = state.content.certifications.findIndex((c) => c.id === id);
          if (index !== -1) {
            Object.assign(state.content.certifications[index], data);
            state.isDirty = true;
          }
        }),
        removeCertification: (id) => set((state) => {
          get().pushToHistory();
          state.content.certifications = state.content.certifications.filter((c) => c.id !== id);
          state.isDirty = true;
        }),

        // Awards
        addAward: (award) => set((state) => {
          get().pushToHistory();
          state.content.awards.push({ ...award, id: generateId() });
          state.isDirty = true;
        }),
        updateAward: (id, data) => set((state) => {
          get().pushToHistory();
          const index = state.content.awards.findIndex((a) => a.id === id);
          if (index !== -1) {
            Object.assign(state.content.awards[index], data);
            state.isDirty = true;
          }
        }),
        removeAward: (id) => set((state) => {
          get().pushToHistory();
          state.content.awards = state.content.awards.filter((a) => a.id !== id);
          state.isDirty = true;
        }),

        // Languages
        addLanguage: (language) => set((state) => {
          get().pushToHistory();
          state.content.languages.push({ ...language, id: generateId() });
          state.isDirty = true;
        }),
        updateLanguage: (id, data) => set((state) => {
          get().pushToHistory();
          const index = state.content.languages.findIndex((l) => l.id === id);
          if (index !== -1) {
            Object.assign(state.content.languages[index], data);
            state.isDirty = true;
          }
        }),
        removeLanguage: (id) => set((state) => {
          get().pushToHistory();
          state.content.languages = state.content.languages.filter((l) => l.id !== id);
          state.isDirty = true;
        }),

        // Custom sections
        addCustomSection: (title) => set((state) => {
          get().pushToHistory();
          state.content.customSections.push({
            id: generateId(),
            title,
            items: [],
          });
          state.isDirty = true;
        }),
        updateCustomSection: (id, data) => set((state) => {
          get().pushToHistory();
          const index = state.content.customSections.findIndex((s) => s.id === id);
          if (index !== -1) {
            Object.assign(state.content.customSections[index], data);
            state.isDirty = true;
          }
        }),
        removeCustomSection: (id) => set((state) => {
          get().pushToHistory();
          state.content.customSections = state.content.customSections.filter((s) => s.id !== id);
          state.isDirty = true;
        }),

        // Custom link actions
        addCustomLink: (link) => set((state) => {
          get().pushToHistory();
          state.content.customLinks.push({ ...link, id: generateId() });
          state.isDirty = true;
        }),
        updateCustomLink: (id, data) => set((state) => {
          get().pushToHistory();
          const index = state.content.customLinks.findIndex((l) => l.id === id);
          if (index !== -1) {
            Object.assign(state.content.customLinks[index], data);
            state.isDirty = true;
          }
        }),
        removeCustomLink: (id) => set((state) => {
          get().pushToHistory();
          state.content.customLinks = state.content.customLinks.filter((l) => l.id !== id);
          state.isDirty = true;
        }),

        // History / Undo-Redo
        pushToHistory: () => set((state) => {
          // Remove any future history if we're not at the end
          const newHistory = state.history.slice(0, state.historyIndex + 1);
          // Add current state to history
          newHistory.push(JSON.parse(JSON.stringify(state.content)));
          // Limit history length
          if (newHistory.length > state.maxHistoryLength) {
            newHistory.shift();
          }
          state.history = newHistory;
          state.historyIndex = newHistory.length - 1;
        }),

        undo: () => set((state) => {
          if (state.historyIndex > 0) {
            state.historyIndex -= 1;
            state.content = JSON.parse(JSON.stringify(state.history[state.historyIndex]));
            state.isDirty = true;
          }
        }),

        redo: () => set((state) => {
          if (state.historyIndex < state.history.length - 1) {
            state.historyIndex += 1;
            state.content = JSON.parse(JSON.stringify(state.history[state.historyIndex]));
            state.isDirty = true;
          }
        }),

        canUndo: () => get().historyIndex > 0,
        canRedo: () => get().historyIndex < get().history.length - 1,

        // Save state
        markDirty: () => set((state) => { state.isDirty = true; }),
        markSaved: () => set((state) => {
          state.isDirty = false;
          state.lastSaved = new Date();
        }),
        setSaving: (saving) => set((state) => { state.isSaving = saving; }),

        // Reset
        reset: () => set((state) => {
          state.draftId = null;
          state.draftName = "Untitled Resume";
          state.content = createDefaultContent();
          state.templateId = "bronzor";
          state.atsScore = null;
          state.themeSettings = DEFAULT_THEME_SETTINGS;
          state.detailedAtsScore = DEFAULT_ATS_SCORE;
          state.shareSettings = DEFAULT_SHARE_SETTINGS;
          state.isDirty = false;
          state.history = [];
          state.historyIndex = -1;
          state.lastSaved = null;
        }),

        // Load draft
        loadDraft: (draft) => set((state) => {
          state.draftId = draft.id;
          state.draftName = draft.name;
          // Ensure customLinks exists for backward compatibility
          const content = ensureCustomLinks(draft.content);
          state.content = content;
          state.templateId = draft.templateId;
          state.atsScore = draft.atsScore;
          state.isDirty = false;
          state.history = [JSON.parse(JSON.stringify(content))];
          state.historyIndex = 0;
        }),
      };
      }),
      {
        name: "resume-builder-storage",
        partialize: (state) => ({
          // Only persist these fields
          draftId: state.draftId,
          draftName: state.draftName,
          content: {
            ...state.content,
            // Ensure customLinks is always an array
            customLinks: state.content.customLinks || [],
          },
          templateId: state.templateId,
          themeSettings: state.themeSettings,
          shareSettings: state.shareSettings,
        }),
        merge: (persistedState, currentState) => {
          // Migration: ensure customLinks exists
          const merged = { ...currentState, ...persistedState } as typeof currentState;
          if (merged.content && !merged.content.customLinks) {
            merged.content.customLinks = [];
          }
          
          // Migration: ensure themeSettings exists with defaults
          if (!merged.themeSettings) {
            merged.themeSettings = DEFAULT_THEME_SETTINGS;
          } else {
            merged.themeSettings = { ...DEFAULT_THEME_SETTINGS, ...merged.themeSettings };
          }
          
          // Migration: ensure shareSettings exists
          if (!merged.shareSettings) {
            merged.shareSettings = DEFAULT_SHARE_SETTINGS;
          }
          
          // Migration: ensure detailedAtsScore exists
          if (!merged.detailedAtsScore) {
            merged.detailedAtsScore = DEFAULT_ATS_SCORE;
          }
          
          // Migration: ensure skills object exists and has all required fields
          if (merged.content) {
            if (!merged.content.skills) {
              merged.content.skills = { technical: [], soft: [], tools: [], custom: [] as TechnicalSkillGroup[], customSkillsHeader: "Custom Skills" };
            } else {
              // Migration: convert old technical skills format (string[]) to new format (TechnicalSkillGroup[])
              merged.content.skills.technical = migrateTechnicalSkills(merged.content.skills.technical);
              // Migration: convert old custom skills format (string[]) to new format (TechnicalSkillGroup[])
              merged.content.skills.custom = migrateCustomSkills(merged.content.skills.custom);
              // Migration: ensure all skill arrays exist
              if (!merged.content.skills.soft) {
                merged.content.skills.soft = [];
              }
              if (!merged.content.skills.tools) {
                merged.content.skills.tools = [];
              }
              // Migration: ensure customSkillsHeader exists
              if (!merged.content.skills.customSkillsHeader) {
                merged.content.skills.customSkillsHeader = "Custom Skills";
              }
            }
            
            // Migration: ensure sectionOrder includes softSkills and customSkills
            if (merged.content.sectionOrder) {
              const order = merged.content.sectionOrder as string[];
              const hasSoftSkills = order.includes("softSkills");
              const hasCustomSkills = order.includes("customSkills");
              
              if (!hasSoftSkills || !hasCustomSkills) {
                // Find the index of "skills" to insert after it
                const skillsIndex = order.indexOf("skills");
                const newOrder = [...order];
                
                if (!hasSoftSkills) {
                  // Insert softSkills right after skills
                  newOrder.splice(skillsIndex + 1, 0, "softSkills");
                }
                
                if (!hasCustomSkills) {
                  // Insert customSkills after softSkills (or after skills if softSkills wasn't added)
                  const insertIndex = newOrder.indexOf("softSkills") !== -1 
                    ? newOrder.indexOf("softSkills") + 1 
                    : skillsIndex + 1;
                  newOrder.splice(insertIndex, 0, "customSkills");
                }
                
                merged.content.sectionOrder = newOrder;
              }
            } else {
              // If sectionOrder doesn't exist, use the default
              merged.content.sectionOrder = DEFAULT_SECTION_ORDER;
            }
          }
          
          // Migration: convert old template IDs to new ones
          const oldTemplateIdMap: Record<string, string> = {
            "professional-modern": "bronzor",
            "classic-traditional": "bronzor",
            "tech-minimalist": "bronzor",
            "two-column": "chikorita",
            "ats-optimized": "bronzor",
          };
          
          if (merged.templateId && oldTemplateIdMap[merged.templateId]) {
            merged.templateId = oldTemplateIdMap[merged.templateId];
            if (merged.content) {
              merged.content.templateId = merged.templateId;
            }
          } else if (!merged.templateId || !["azurill", "bronzor", "chikorita", "ditto", "ditgar", "gengar", "glalie", "kakuna", "lapras", "leafish", "onyx", "pikachu", "rhyhorn"].includes(merged.templateId)) {
            // Fallback to bronzor if template ID is invalid
            merged.templateId = "bronzor";
            if (merged.content) {
              merged.content.templateId = "bronzor";
            }
          }
          
          return merged;
        },
      }
    ),
    { name: "resume-builder" }
  )
);
