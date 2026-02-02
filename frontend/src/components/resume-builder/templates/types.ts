/**
 * Resume template type definitions.
 */

import type { ResumeContent, ThemeSettings } from "@/stores/resume-builder-store";

export interface ResumeTemplateProps {
  content: ResumeContent;
  scale?: number;
  highlightSection?: string;
  themeSettings?: ThemeSettings;
}

export interface TemplateConfig {
  id: string;
  name: string;
  description: string;
  thumbnail?: string;
  atsScore: number;
  component: React.ComponentType<ResumeTemplateProps>;
}
