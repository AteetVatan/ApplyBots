/**
 * Shared PDF styles factory for @react-pdf/renderer.
 * Creates theme-aware StyleSheet for consistent PDF rendering.
 */

import { StyleSheet, Font } from "@react-pdf/renderer";
import type { ThemeSettings } from "@/stores/resume-builder-store";

// Register fonts for PDF rendering
// Using system fonts that are widely available
Font.register({
  family: "Inter",
  fonts: [
    { src: "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfAZ9hjp-Ek-_EeA.woff", fontWeight: 400 },
    { src: "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuI6fAZ9hjp-Ek-_EeA.woff", fontWeight: 500 },
    { src: "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuGKYAZ9hjp-Ek-_EeA.woff", fontWeight: 600 },
    { src: "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuFuYAZ9hjp-Ek-_EeA.woff", fontWeight: 700 },
  ],
});

Font.register({
  family: "Georgia",
  src: "https://fonts.cdnfonts.com/s/14915/georgia.woff",
});

// Hyphenation callback to prevent word-breaking issues
Font.registerHyphenationCallback((word) => [word]);

/**
 * Get font family for PDF based on theme setting.
 */
export function getPDFFontFamily(themeSettings: ThemeSettings): string {
  if (themeSettings.fontFamily === "Georgia" || themeSettings.fontFamily === "Merriweather") {
    return "Georgia";
  }
  return "Inter";
}

/**
 * Get base font size in points based on theme setting.
 */
export function getPDFBaseFontSize(themeSettings: ThemeSettings): number {
  const sizes = { small: 10, medium: 11, large: 12 };
  return sizes[themeSettings.fontSize];
}

/**
 * Get spacing multiplier based on theme setting.
 */
export function getPDFSpacingMultiplier(themeSettings: ThemeSettings): number {
  const multipliers = { compact: 0.8, normal: 1.0, spacious: 1.2 };
  return multipliers[themeSettings.spacing];
}

/**
 * Convert hex color to RGB object.
 */
export function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
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
 * Get darker shade of a color.
 */
export function getDarkerColor(hex: string, factor = 0.8): string {
  const rgb = hexToRgb(hex);
  if (!rgb) return hex;
  return `rgb(${Math.round(rgb.r * factor)}, ${Math.round(rgb.g * factor)}, ${Math.round(rgb.b * factor)})`;
}

/**
 * Create base styles for single-column PDF templates.
 */
export function createSingleColumnStyles(theme: ThemeSettings) {
  const baseFontSize = getPDFBaseFontSize(theme);
  const spacing = getPDFSpacingMultiplier(theme);
  const fontFamily = getPDFFontFamily(theme);

  return StyleSheet.create({
    page: {
      padding: 36 * spacing,
      fontFamily,
      fontSize: baseFontSize,
      lineHeight: 1.4,
      color: "#1f2937",
    },
    header: {
      marginBottom: 12 * spacing,
      paddingBottom: 8 * spacing,
      borderBottomWidth: 1,
      borderBottomColor: "#d1d5db",
    },
    headerWithPhoto: {
      flexDirection: "row",
      alignItems: "flex-start",
      gap: 12,
    },
    profileImage: {
      width: 60,
      height: 60,
      borderRadius: 30,
      objectFit: "cover",
    },
    headerContent: {
      flex: 1,
    },
    name: {
      fontSize: baseFontSize * 2.2,
      fontWeight: 700,
      color: "#111827",
      marginBottom: 4,
    },
    contactRow: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: 8,
      fontSize: baseFontSize,
      color: "#4b5563",
    },
    contactItem: {
      color: "#4b5563",
    },
    contactSeparator: {
      color: "#9ca3af",
    },
    linksRow: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: 12,
      marginTop: 4,
      fontSize: baseFontSize,
    },
    link: {
      color: theme.primaryColor,
      textDecoration: "none",
    },
    section: {
      marginBottom: 10 * spacing,
    },
    sectionTitle: {
      fontSize: baseFontSize + 1,
      fontWeight: 700,
      textTransform: "uppercase",
      letterSpacing: 0.5,
      marginBottom: 6 * spacing,
      color: "#111827",
    },
    summaryText: {
      color: "#374151",
      lineHeight: 1.5,
    },
    experienceItem: {
      marginBottom: 8 * spacing,
    },
    experienceHeader: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "flex-start",
      marginBottom: 2,
    },
    experienceTitleRow: {
      flexDirection: "row",
      flexWrap: "wrap",
      flex: 1,
    },
    jobTitle: {
      fontWeight: 600,
      color: "#111827",
    },
    company: {
      color: "#4b5563",
    },
    dateLocation: {
      fontSize: baseFontSize - 1,
      color: "#6b7280",
      textAlign: "right",
    },
    bulletList: {
      paddingLeft: 12,
      marginTop: 4,
    },
    bulletItem: {
      marginBottom: 2,
      color: "#374151",
      flexDirection: "row",
    },
    bullet: {
      width: 10,
      color: "#6b7280",
    },
    bulletText: {
      flex: 1,
      color: "#374151",
    },
    educationItem: {
      marginBottom: 6 * spacing,
    },
    skillsRow: {
      marginBottom: 4,
    },
    skillHeader: {
      fontWeight: 600,
      color: "#111827",
    },
    skillItems: {
      color: "#374151",
    },
    certificationItem: {
      marginBottom: 4,
    },
    certName: {
      fontWeight: 600,
      color: "#111827",
    },
    certDetails: {
      color: "#4b5563",
    },
    languagesRow: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: 16,
    },
    languageItem: {
      color: "#374151",
    },
    languageProficiency: {
      color: "#6b7280",
      fontStyle: "italic",
    },
    projectItem: {
      marginBottom: 6 * spacing,
    },
    projectName: {
      fontWeight: 600,
      color: "#111827",
    },
    projectDescription: {
      color: "#374151",
      marginTop: 2,
    },
    projectTech: {
      fontSize: baseFontSize - 1,
      color: "#6b7280",
      fontStyle: "italic",
      marginTop: 2,
    },
    awardItem: {
      marginBottom: 4,
    },
    awardTitle: {
      fontWeight: 600,
      color: "#111827",
    },
    awardDescription: {
      fontSize: baseFontSize - 1,
      color: "#6b7280",
      marginTop: 2,
    },
  });
}

/**
 * Create base styles for two-column PDF templates.
 */
export function createTwoColumnStyles(theme: ThemeSettings, sidebarPosition: "left" | "right" = "left") {
  const baseFontSize = getPDFBaseFontSize(theme);
  const spacing = getPDFSpacingMultiplier(theme);
  const fontFamily = getPDFFontFamily(theme);

  return StyleSheet.create({
    page: {
      fontFamily,
      fontSize: baseFontSize,
      lineHeight: 1.4,
      color: "#1f2937",
      flexDirection: sidebarPosition === "left" ? "row" : "row-reverse",
    },
    sidebar: {
      width: "33%",
      backgroundColor: theme.primaryColor,
      padding: 20 * spacing,
      color: "#ffffff",
    },
    main: {
      width: "67%",
      padding: 24 * spacing,
    },
    // Sidebar styles
    sidebarProfileImage: {
      width: 80,
      height: 80,
      borderRadius: 40,
      borderWidth: 2,
      borderColor: "rgba(255,255,255,0.3)",
      alignSelf: "center",
      marginBottom: 12,
      objectFit: "cover",
    },
    sidebarName: {
      fontSize: baseFontSize * 1.6,
      fontWeight: 700,
      color: "#ffffff",
      textAlign: "center",
      marginBottom: 12,
    },
    sidebarContact: {
      fontSize: baseFontSize - 1,
      color: "rgba(255,255,255,0.9)",
      marginBottom: 4,
    },
    sidebarSection: {
      marginTop: 16 * spacing,
    },
    sidebarSectionTitle: {
      fontSize: baseFontSize,
      fontWeight: 700,
      textTransform: "uppercase",
      letterSpacing: 0.5,
      color: "#ffffff",
      marginBottom: 8,
      paddingBottom: 4,
      borderBottomWidth: 1,
      borderBottomColor: "rgba(255,255,255,0.3)",
    },
    sidebarSkillGroup: {
      marginBottom: 8,
    },
    sidebarSkillHeader: {
      fontSize: baseFontSize - 1,
      textTransform: "uppercase",
      color: "rgba(255,255,255,0.8)",
      marginBottom: 4,
    },
    sidebarSkillTags: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: 4,
    },
    sidebarSkillTag: {
      fontSize: baseFontSize - 1.5,
      backgroundColor: "rgba(255,255,255,0.2)",
      color: "#ffffff",
      paddingHorizontal: 6,
      paddingVertical: 2,
      borderRadius: 3,
    },
    sidebarLanguage: {
      fontSize: baseFontSize - 1,
      color: "#ffffff",
      marginBottom: 4,
    },
    sidebarCertification: {
      marginBottom: 8,
    },
    sidebarCertName: {
      fontSize: baseFontSize - 1,
      fontWeight: 600,
      color: "#ffffff",
    },
    sidebarCertIssuer: {
      fontSize: baseFontSize - 1.5,
      color: "rgba(255,255,255,0.8)",
    },
    sidebarLink: {
      color: "#ffffff",
      textDecoration: "none",
    },
    // Main content styles
    mainSection: {
      marginBottom: 12 * spacing,
    },
    mainSectionTitle: {
      fontSize: baseFontSize + 1,
      fontWeight: 700,
      textTransform: "uppercase",
      letterSpacing: 0.5,
      color: "#374151",
      marginBottom: 8,
      paddingBottom: 4,
      borderBottomWidth: 1,
      borderBottomColor: "#e5e7eb",
    },
    mainSummary: {
      fontSize: baseFontSize,
      color: "#4b5563",
      lineHeight: 1.5,
    },
    mainExperienceItem: {
      marginBottom: 10 * spacing,
    },
    mainExperienceHeader: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "flex-start",
      marginBottom: 2,
    },
    mainJobTitle: {
      fontWeight: 600,
      color: "#111827",
    },
    mainCompany: {
      color: theme.primaryColor,
    },
    mainDate: {
      fontSize: baseFontSize - 1,
      color: "#6b7280",
    },
    mainBulletList: {
      paddingLeft: 12,
      marginTop: 4,
    },
    mainBulletItem: {
      flexDirection: "row",
      marginBottom: 2,
      fontSize: baseFontSize - 1,
    },
    mainBullet: {
      width: 8,
      color: "#6b7280",
    },
    mainBulletText: {
      flex: 1,
      color: "#4b5563",
    },
    mainEducationItem: {
      marginBottom: 8 * spacing,
    },
    mainDegree: {
      fontWeight: 600,
      color: "#111827",
    },
    mainInstitution: {
      fontSize: baseFontSize - 1,
      color: "#4b5563",
    },
    mainGPA: {
      fontSize: baseFontSize - 1,
      color: "#6b7280",
    },
    mainProjectItem: {
      marginBottom: 8 * spacing,
    },
    mainProjectName: {
      fontWeight: 600,
      color: "#111827",
    },
    mainProjectDesc: {
      fontSize: baseFontSize - 1,
      color: "#4b5563",
      marginTop: 2,
    },
    mainProjectTech: {
      fontSize: baseFontSize - 1.5,
      color: theme.primaryColor,
      marginTop: 2,
    },
    mainSkillTags: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: 4,
    },
    mainSkillTag: {
      fontSize: baseFontSize - 1.5,
      backgroundColor: `${theme.primaryColor}20`,
      color: theme.primaryColor,
      paddingHorizontal: 6,
      paddingVertical: 2,
      borderRadius: 3,
    },
    mainAwardItem: {
      marginBottom: 4,
      fontSize: baseFontSize - 1,
    },
    mainAwardTitle: {
      fontWeight: 600,
      color: "#111827",
    },
    mainAwardDesc: {
      fontSize: baseFontSize - 1.5,
      color: "#6b7280",
      marginTop: 2,
    },
  });
}
