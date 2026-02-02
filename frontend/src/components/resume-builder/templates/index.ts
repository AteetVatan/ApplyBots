/**
 * Resume templates registry.
 *
 * Exports all available templates with their configurations.
 * Inspired by Reactive Resume (https://github.com/AmruthPillai/Reactive-Resume)
 */

import type { TemplateConfig } from "./types";
import { Azurill } from "./Azurill";
import { Bronzor } from "./Bronzor";
import { Chikorita } from "./Chikorita";
import { Ditto } from "./Ditto";
import { Ditgar } from "./Ditgar";
import { Gengar } from "./Gengar";
import { Glalie } from "./Glalie";
import { Kakuna } from "./Kakuna";
import { Lapras } from "./Lapras";
import { Leafish } from "./Leafish";
import { Onyx } from "./Onyx";
import { Pikachu } from "./Pikachu";
import { Rhyhorn } from "./Rhyhorn";

export * from "./types";
export { Azurill } from "./Azurill";
export { Bronzor } from "./Bronzor";
export { Chikorita } from "./Chikorita";
export { Ditto } from "./Ditto";
export { Ditgar } from "./Ditgar";
export { Gengar } from "./Gengar";
export { Glalie } from "./Glalie";
export { Kakuna } from "./Kakuna";
export { Lapras } from "./Lapras";
export { Leafish } from "./Leafish";
export { Onyx } from "./Onyx";
export { Pikachu } from "./Pikachu";
export { Rhyhorn } from "./Rhyhorn";

/**
 * All available resume templates (13 total).
 * Names inspired by Pokemon, matching Reactive Resume's naming convention.
 */
export const TEMPLATES: TemplateConfig[] = [
  // Single-column templates (ATS Score: 95)
  {
    id: "bronzor",
    name: "Bronzor",
    description: "Clean, minimalist single-column design with profile picture left of name",
    atsScore: 95,
    component: Bronzor,
  },
  {
    id: "kakuna",
    name: "Kakuna",
    description: "Clean single-column design with subtle styling variations",
    atsScore: 95,
    component: Kakuna,
  },
  {
    id: "rhyhorn",
    name: "Rhyhorn",
    description: "Clean minimalist single-column design with professional layout",
    atsScore: 95,
    component: Rhyhorn,
  },
  {
    id: "onyx",
    name: "Onyx",
    description: "Single-column design with thin border and blue accent line",
    atsScore: 95,
    component: Onyx,
  },
  {
    id: "lapras",
    name: "Lapras",
    description: "Single-column layout with pink/magenta header accent and elegant serif typography",
    atsScore: 95,
    component: Lapras,
  },
  {
    id: "leafish",
    name: "Leafish",
    description: "Single-column layout with green accent bars and modern typography",
    atsScore: 95,
    component: Leafish,
  },
  // Two-column templates (ATS Score: 88)
  {
    id: "azurill",
    name: "Azurill",
    description: "Two-column layout with purple/magenta gradient sidebar",
    atsScore: 88,
    component: Azurill,
  },
  {
    id: "chikorita",
    name: "Chikorita",
    description: "Two-column layout with green sidebar for profile, skills, and certifications",
    atsScore: 88,
    component: Chikorita,
  },
  {
    id: "ditto",
    name: "Ditto",
    description: "Two-column layout with teal/cyan RIGHT sidebar - unique reversed layout",
    atsScore: 88,
    component: Ditto,
  },
  {
    id: "ditgar",
    name: "Ditgar",
    description: "Two-column layout with sky blue sidebar featuring skill progress bars",
    atsScore: 88,
    component: Ditgar,
  },
  {
    id: "gengar",
    name: "Gengar",
    description: "Two-column layout with blue sidebar for profile, skills, and certifications",
    atsScore: 88,
    component: Gengar,
  },
  {
    id: "glalie",
    name: "Glalie",
    description: "Two-column layout with dark emerald sidebar - compact professional design",
    atsScore: 88,
    component: Glalie,
  },
  {
    id: "pikachu",
    name: "Pikachu",
    description: "Two-column layout with vibrant yellow/gold sidebar",
    atsScore: 88,
    component: Pikachu,
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
  // Handle old template IDs for backward compatibility
  const oldTemplateIdMap: Record<string, string> = {
    "professional-modern": "bronzor",
    "classic-traditional": "bronzor",
    "tech-minimalist": "bronzor",
    "two-column": "chikorita",
    "ats-optimized": "bronzor",
  };
  
  const mappedId = oldTemplateIdMap[id] || id;
  const template = getTemplate(mappedId);
  
  // Always return a valid component, default to Bronzor
  if (!template || !template.component) {
    return Bronzor;
  }
  
  return template.component;
}
