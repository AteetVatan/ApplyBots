/**
 * PDF templates registry for @react-pdf/renderer.
 * Exports all available PDF templates and helper functions.
 */

export * from "./types";
export * from "./utils";

// Single-column templates (ATS Score: 95)
export { BronzorPDF } from "./BronzorPDF";
export { KakunaPDF } from "./KakunaPDF";
export { RhyhornPDF } from "./RhyhornPDF";
export { OnyxPDF } from "./OnyxPDF";
export { LaprasPDF } from "./LaprasPDF";
export { LeafishPDF } from "./LeafishPDF";

// Two-column templates (ATS Score: 88)
export { AzurillPDF } from "./AzurillPDF";
export { ChikoritaPDF } from "./ChikoritaPDF";
export { DittoPDF } from "./DittoPDF";
export { DitgarPDF } from "./DitgarPDF";
export { GengarPDF } from "./GengarPDF";
export { GlaliePDF } from "./GlaliePDF";
export { PikachuPDF } from "./PikachuPDF";

import type { PDFTemplateProps } from "./types";
import { BronzorPDF } from "./BronzorPDF";
import { KakunaPDF } from "./KakunaPDF";
import { RhyhornPDF } from "./RhyhornPDF";
import { OnyxPDF } from "./OnyxPDF";
import { LaprasPDF } from "./LaprasPDF";
import { LeafishPDF } from "./LeafishPDF";
import { AzurillPDF } from "./AzurillPDF";
import { ChikoritaPDF } from "./ChikoritaPDF";
import { DittoPDF } from "./DittoPDF";
import { DitgarPDF } from "./DitgarPDF";
import { GengarPDF } from "./GengarPDF";
import { GlaliePDF } from "./GlaliePDF";
import { PikachuPDF } from "./PikachuPDF";

/**
 * Map of template IDs to PDF components.
 */
export const PDF_TEMPLATES: Record<string, React.ComponentType<PDFTemplateProps>> = {
  // Single-column
  bronzor: BronzorPDF,
  kakuna: KakunaPDF,
  rhyhorn: RhyhornPDF,
  onyx: OnyxPDF,
  lapras: LaprasPDF,
  leafish: LeafishPDF,
  // Two-column
  azurill: AzurillPDF,
  chikorita: ChikoritaPDF,
  ditto: DittoPDF,
  ditgar: DitgarPDF,
  gengar: GengarPDF,
  glalie: GlaliePDF,
  pikachu: PikachuPDF,
};

/**
 * Get PDF template component by ID.
 * Falls back to BronzorPDF if template not found.
 */
export function getPDFTemplateComponent(templateId: string): React.ComponentType<PDFTemplateProps> {
  // Handle legacy template IDs
  const legacyMap: Record<string, string> = {
    "professional-modern": "bronzor",
    "classic-traditional": "bronzor",
    "tech-minimalist": "bronzor",
    "two-column": "chikorita",
    "ats-optimized": "bronzor",
  };

  const mappedId = legacyMap[templateId] || templateId;
  return PDF_TEMPLATES[mappedId] || BronzorPDF;
}
