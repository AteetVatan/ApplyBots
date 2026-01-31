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

export interface SkillsSection {
  technical: string[];
  soft: string[];
  tools: string[];
}

export interface CustomSection {
  id: string;
  title: string;
  items: string[];
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
  | "projects"
  | "certifications"
  | "awards"
  | "languages"
  | "custom";

interface ResumeBuilderState {
  // Draft data
  draftId: string | null;
  draftName: string;
  content: ResumeContent;
  templateId: string;
  atsScore: number | null;

  // UI state
  activeSection: SectionKey;
  previewScale: number;
  isDirty: boolean;
  isSaving: boolean;
  lastSaved: Date | null;
  isAIDrawerOpen: boolean;

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
  setATSScore: (score: number | null) => void;

  // Content update actions
  updateContact: (data: Partial<Pick<ResumeContent, "fullName" | "email" | "phone" | "location" | "linkedinUrl" | "portfolioUrl" | "githubUrl">>) => void;
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
  professionalSummary: null,
  workExperience: [],
  education: [],
  skills: { technical: [], soft: [], tools: [] },
  projects: [],
  certifications: [],
  awards: [],
  languages: [],
  customSections: [],
  templateId: "professional-modern",
  sectionOrder: DEFAULT_SECTION_ORDER,
  atsScore: null,
});

// ============================================================================
// Helper functions
// ============================================================================

const generateId = () => crypto.randomUUID();

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
      immer((set, get) => ({
        // Initial state
        draftId: null,
        draftName: "Untitled Resume",
        content: createDefaultContent(),
        templateId: "professional-modern",
        atsScore: null,
        activeSection: "contact",
        previewScale: 0.75,
        isDirty: false,
        isSaving: false,
        lastSaved: null,
        isAIDrawerOpen: false,
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
        setATSScore: (score) => set((state) => {
          state.atsScore = score;
          state.content.atsScore = score;
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
          state.templateId = "professional-modern";
          state.atsScore = null;
          state.isDirty = false;
          state.history = [];
          state.historyIndex = -1;
          state.lastSaved = null;
        }),

        // Load draft
        loadDraft: (draft) => set((state) => {
          state.draftId = draft.id;
          state.draftName = draft.name;
          state.content = draft.content;
          state.templateId = draft.templateId;
          state.atsScore = draft.atsScore;
          state.isDirty = false;
          state.history = [JSON.parse(JSON.stringify(draft.content))];
          state.historyIndex = 0;
        }),
      })),
      {
        name: "resume-builder-storage",
        partialize: (state) => ({
          // Only persist these fields
          draftId: state.draftId,
          draftName: state.draftName,
          content: state.content,
          templateId: state.templateId,
        }),
      }
    ),
    { name: "resume-builder" }
  )
);
