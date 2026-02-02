/**
 * PDF template type definitions for @react-pdf/renderer.
 */

import type { ResumeContent, ThemeSettings } from "@/stores/resume-builder-store";

export interface PDFTemplateProps {
  content: ResumeContent;
  themeSettings: ThemeSettings;
}

export interface PDFTemplateConfig {
  id: string;
  name: string;
  component: React.ComponentType<PDFTemplateProps>;
}
