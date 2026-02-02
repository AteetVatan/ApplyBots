/**
 * Ditto PDF template - Two-column, ATS-optimized.
 * Two-column layout with teal/cyan RIGHT sidebar - unique reversed layout.
 */

import React from "react";
import type { PDFTemplateProps } from "./types";
import { TwoColumnBasePDF } from "./TwoColumnBasePDF";

export function DittoPDF({ content, themeSettings }: PDFTemplateProps) {
  return (
    <TwoColumnBasePDF
      content={content}
      themeSettings={themeSettings}
      sidebarPosition="right"
      sidebarSections={["skills", "softSkills", "customSkills", "languages", "certifications"]}
      mainSections={["summary", "experience", "education", "projects", "awards"]}
    />
  );
}
