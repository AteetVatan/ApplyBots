/**
 * Chikorita PDF template - Two-column, ATS-optimized.
 * Two-column layout with green sidebar for profile, skills, and certifications.
 */

import React from "react";
import type { PDFTemplateProps } from "./types";
import { TwoColumnBasePDF } from "./TwoColumnBasePDF";

export function ChikoritaPDF({ content, themeSettings }: PDFTemplateProps) {
  return (
    <TwoColumnBasePDF
      content={content}
      themeSettings={themeSettings}
      sidebarPosition="left"
      sidebarSections={["skills", "softSkills", "customSkills", "languages", "certifications"]}
      mainSections={["summary", "experience", "education", "projects", "awards"]}
    />
  );
}
