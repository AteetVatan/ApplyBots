/**
 * Utility functions for converting theme settings to CSS values.
 */

import type { ThemeSettings } from "@/stores/resume-builder-store";

/**
 * Get font size in points based on theme setting.
 * This is the base font size that relative units (%) scale from.
 */
export function getFontSize(themeSettings: ThemeSettings): string {
  const baseSizes = {
    small: "10pt",
    medium: "11pt",
    large: "12pt",
  };
  return baseSizes[themeSettings.fontSize];
}

/**
 * Get base font size multiplier for scaling.
 */
export function getFontSizeMultiplier(themeSettings: ThemeSettings): number {
  const multipliers = {
    small: 0.91,
    medium: 1.0,
    large: 1.09,
  };
  return multipliers[themeSettings.fontSize];
}

/**
 * Get relative font size for body text (scaled from base).
 */
export function getBodyFontSize(themeSettings: ThemeSettings): string {
  const baseSizes = {
    small: "9pt",
    medium: "10pt",
    large: "11pt",
  };
  return baseSizes[themeSettings.fontSize];
}

/**
 * Get relative font size for small text (scaled from base).
 */
export function getSmallFontSize(themeSettings: ThemeSettings): string {
  const baseSizes = {
    small: "8pt",
    medium: "9pt",
    large: "10pt",
  };
  return baseSizes[themeSettings.fontSize];
}

/**
 * Get relative font size for extra small text (scaled from base).
 */
export function getExtraSmallFontSize(themeSettings: ThemeSettings): string {
  const baseSizes = {
    small: "7.5pt",
    medium: "8.5pt",
    large: "9.5pt",
  };
  return baseSizes[themeSettings.fontSize];
}

/**
 * Get relative font size for section headers (scaled from base).
 */
export function getSectionHeaderFontSize(themeSettings: ThemeSettings): string {
  const baseSizes = {
    small: "11pt",
    medium: "12pt",
    large: "13pt",
  };
  return baseSizes[themeSettings.fontSize];
}

/**
 * Get spacing multiplier based on theme setting.
 */
export function getSpacingMultiplier(themeSettings: ThemeSettings): number {
  const multipliers = {
    compact: 0.75,
    normal: 1.0,
    spacious: 1.25,
  };
  return multipliers[themeSettings.spacing];
}

/**
 * Get font family string with fallbacks.
 */
export function getFontFamily(themeSettings: ThemeSettings): string {
  const font = themeSettings.fontFamily;
  // Add common fallbacks based on font type
  if (font === "Georgia" || font === "Merriweather") {
    return `'${font}', serif`;
  }
  return `'${font}', 'Helvetica Neue', Helvetica, Arial, sans-serif`;
}

/**
 * Get primary color from theme settings.
 */
export function getPrimaryColor(themeSettings: ThemeSettings): string {
  return themeSettings.primaryColor;
}

/**
 * Convert hex color to RGB values.
 */
function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
}

/**
 * Get a darker shade of the primary color.
 */
export function getPrimaryColorDark(themeSettings: ThemeSettings, factor = 0.7): string {
  const rgb = hexToRgb(themeSettings.primaryColor);
  if (!rgb) return themeSettings.primaryColor;
  return `rgb(${Math.round(rgb.r * factor)}, ${Math.round(rgb.g * factor)}, ${Math.round(rgb.b * factor)})`;
}

/**
 * Get a lighter shade of the primary color.
 */
export function getPrimaryColorLight(themeSettings: ThemeSettings, factor = 1.3): string {
  const rgb = hexToRgb(themeSettings.primaryColor);
  if (!rgb) return themeSettings.primaryColor;
  return `rgb(${Math.min(255, Math.round(rgb.r * factor))}, ${Math.min(255, Math.round(rgb.g * factor))}, ${Math.min(255, Math.round(rgb.b * factor))})`;
}

/**
 * Get primary color with opacity.
 */
export function getPrimaryColorWithOpacity(themeSettings: ThemeSettings, opacity: number): string {
  const rgb = hexToRgb(themeSettings.primaryColor);
  if (!rgb) return themeSettings.primaryColor;
  return `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, ${opacity})`;
}

/**
 * Get gradient colors for sidebars (primary color to darker variant).
 */
export function getPrimaryGradient(themeSettings: ThemeSettings): string {
  const primary = themeSettings.primaryColor;
  const darker = getPrimaryColorDark(themeSettings, 0.8);
  return `linear-gradient(to bottom, ${primary}, ${darker})`;
}

/**
 * CSS Custom Properties for font sizes.
 * These don't compound like percentages - they always reference the root value.
 * Use with style={{ ...getThemeCSSVariables(themeSettings) }} on root element.
 */
export function getThemeCSSVariables(themeSettings: ThemeSettings): Record<string, string> {
  const sizes = {
    small: {
      base: "10pt",
      body: "9.5pt",
      small: "8.5pt",
      xs: "8pt",
      header: "11pt",
      title: "12pt",
    },
    medium: {
      base: "11pt",
      body: "10.5pt",
      small: "9.5pt",
      xs: "9pt",
      header: "12pt",
      title: "13pt",
    },
    large: {
      base: "12pt",
      body: "11.5pt",
      small: "10.5pt",
      xs: "10pt",
      header: "13pt",
      title: "14pt",
    },
  };
  const s = sizes[themeSettings.fontSize];
  return {
    "--font-base": s.base,
    "--font-body": s.body,
    "--font-small": s.small,
    "--font-xs": s.xs,
    "--font-header": s.header,
    "--font-title": s.title,
  };
}
