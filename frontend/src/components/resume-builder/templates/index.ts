/**
 * Resume templates registry.
 *
 * Exports all available templates with their configurations.
 */

import type { TemplateConfig } from "./types";
import { ProfessionalModern } from "./ProfessionalModern";
import { ClassicTraditional } from "./ClassicTraditional";
import { TechMinimalist } from "./TechMinimalist";
import { TwoColumn } from "./TwoColumn";
import { ATSOptimized } from "./ATSOptimized";

export * from "./types";
export { ProfessionalModern } from "./ProfessionalModern";
export { ClassicTraditional } from "./ClassicTraditional";
export { TechMinimalist } from "./TechMinimalist";
export { TwoColumn } from "./TwoColumn";
export { ATSOptimized } from "./ATSOptimized";

/**
 * All available resume templates.
 */
export const TEMPLATES: TemplateConfig[] = [
  {
    id: "professional-modern",
    name: "Professional Modern",
    description: "Clean, modern design with blue accents and balanced whitespace",
    atsScore: 95,
    component: ProfessionalModern,
  },
  {
    id: "classic-traditional",
    name: "Classic Traditional",
    description: "Timeless serif design suitable for conservative industries",
    atsScore: 98,
    component: ClassicTraditional,
  },
  {
    id: "tech-minimalist",
    name: "Tech Minimalist",
    description: "Monospace font with grid layout, perfect for developers",
    atsScore: 92,
    component: TechMinimalist,
  },
  {
    id: "two-column",
    name: "Two Column",
    description: "Space-efficient two-column layout with sidebar",
    atsScore: 88,
    component: TwoColumn,
  },
  {
    id: "ats-optimized",
    name: "ATS Optimized",
    description: "Ultra-simple format designed for maximum ATS compatibility",
    atsScore: 100,
    component: ATSOptimized,
  },
  // Additional template placeholders (use ProfessionalModern as fallback)
  {
    id: "creative-designer",
    name: "Creative Designer",
    description: "Bold typography and creative layout for design roles",
    atsScore: 85,
    component: ProfessionalModern, // TODO: Create dedicated template
  },
  {
    id: "executive-premium",
    name: "Executive Premium",
    description: "Sophisticated design for senior leadership positions",
    atsScore: 94,
    component: ClassicTraditional, // TODO: Create dedicated template
  },
  {
    id: "academic-research",
    name: "Academic/Research",
    description: "Detailed format for academic and research positions",
    atsScore: 90,
    component: ClassicTraditional, // TODO: Create dedicated template
  },
  {
    id: "entry-level",
    name: "Entry Level",
    description: "Focus on education and skills for new graduates",
    atsScore: 96,
    component: ProfessionalModern, // TODO: Create dedicated template
  },
  {
    id: "compact-dense",
    name: "Compact Dense",
    description: "Maximum content in minimum space",
    atsScore: 91,
    component: TechMinimalist, // TODO: Create dedicated template
  },
];

/**
 * Get template by ID.
 */
export function getTemplate(id: string): TemplateConfig | undefined {
  return TEMPLATES.find((t) => t.id === id);
}

/**
 * Get template component by ID, with fallback.
 */
export function getTemplateComponent(id: string): TemplateConfig["component"] {
  const template = getTemplate(id);
  return template?.component ?? ProfessionalModern;
}
