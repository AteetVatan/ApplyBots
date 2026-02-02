/**
 * Base component for two-column PDF templates.
 * Provides shared structure for sidebar + main content layouts.
 */

import React from "react";
import {
  Document,
  Page,
  View,
  Text,
  Link,
  Image,
  StyleSheet,
} from "@react-pdf/renderer";
import type { ResumeContent, ThemeSettings } from "@/stores/resume-builder-store";
import { getPDFFontFamily, getPDFBaseFontSize, getPDFSpacingMultiplier, getDarkerColor } from "./styles";
import { stripHtml, formatDateRange, capitalize } from "./utils";

interface TwoColumnPDFProps {
  content: ResumeContent;
  themeSettings: ThemeSettings;
  sidebarPosition?: "left" | "right";
  sidebarSections?: string[];
  mainSections?: string[];
}

const DEFAULT_SIDEBAR_SECTIONS = ["skills", "softSkills", "customSkills", "languages", "certifications"];
const DEFAULT_MAIN_SECTIONS = ["summary", "experience", "education", "projects", "awards"];

export function TwoColumnBasePDF({ 
  content, 
  themeSettings, 
  sidebarPosition = "left",
  sidebarSections = DEFAULT_SIDEBAR_SECTIONS,
  mainSections = DEFAULT_MAIN_SECTIONS,
}: TwoColumnPDFProps) {
  const pageSize = themeSettings.pageSize === "a4" ? "A4" : "LETTER";
  const baseFontSize = getPDFBaseFontSize(themeSettings);
  const spacing = getPDFSpacingMultiplier(themeSettings);
  const fontFamily = getPDFFontFamily(themeSettings);
  const primaryColor = themeSettings.primaryColor;
  const darkerColor = getDarkerColor(primaryColor, 0.85);

  const styles = StyleSheet.create({
    page: {
      fontFamily,
      fontSize: baseFontSize,
      lineHeight: 1.4,
      color: "#1f2937",
      flexDirection: sidebarPosition === "left" ? "row" : "row-reverse",
    },
    sidebar: {
      width: "33%",
      backgroundColor: primaryColor,
      padding: 20 * spacing,
      color: "#ffffff",
    },
    main: {
      width: "67%",
      padding: 24 * spacing,
    },
    // Sidebar styles
    sidebarProfileImage: {
      width: 90,
      height: 90,
      borderRadius: 45,
      borderWidth: 3,
      borderColor: "rgba(255,255,255,0.3)",
      alignSelf: "center",
      marginBottom: 14,
      objectFit: "cover",
    },
    sidebarName: {
      fontSize: baseFontSize * 1.5,
      fontWeight: 700,
      color: "#ffffff",
      textAlign: "center",
      marginBottom: 4,
    },
    sidebarTitle: {
      fontSize: baseFontSize,
      color: "rgba(255,255,255,0.85)",
      textAlign: "center",
      marginBottom: 12,
    },
    sidebarContact: {
      fontSize: baseFontSize - 1,
      color: "rgba(255,255,255,0.9)",
      marginBottom: 3,
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
      gap: 3,
    },
    sidebarSkillTag: {
      fontSize: baseFontSize - 1.5,
      backgroundColor: "rgba(255,255,255,0.2)",
      color: "#ffffff",
      paddingHorizontal: 5,
      paddingVertical: 2,
      borderRadius: 2,
      marginBottom: 2,
    },
    sidebarText: {
      fontSize: baseFontSize - 1,
      color: "#ffffff",
      marginBottom: 3,
    },
    sidebarLink: {
      color: "#ffffff",
      textDecoration: "none",
    },
    sidebarCertItem: {
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
    // Main content styles
    mainSection: {
      marginBottom: 14 * spacing,
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
      color: primaryColor,
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
      fontSize: baseFontSize,
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
      color: primaryColor,
      marginTop: 2,
    },
    mainLink: {
      color: primaryColor,
      textDecoration: "none",
    },
    mainAwardItem: {
      marginBottom: 6,
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
    mainSkillTags: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: 4,
    },
    mainSkillTag: {
      fontSize: baseFontSize - 1.5,
      backgroundColor: `${primaryColor}15`,
      color: primaryColor,
      paddingHorizontal: 6,
      paddingVertical: 2,
      borderRadius: 2,
    },
  });

  // Sidebar content renderer
  const renderSidebarSection = (sectionKey: string) => {
    switch (sectionKey) {
      case "skills":
        if (!content.skills.technical?.length) return null;
        return (
          <View key={sectionKey} style={styles.sidebarSection}>
            <Text style={styles.sidebarSectionTitle}>Technical Skills</Text>
            {content.skills.technical.map((group, idx) => (
              <View key={idx} style={styles.sidebarSkillGroup}>
                <Text style={styles.sidebarSkillHeader}>{group.header}</Text>
                <View style={styles.sidebarSkillTags}>
                  {group.items.map((skill, i) => (
                    <Text key={i} style={styles.sidebarSkillTag}>{skill}</Text>
                  ))}
                </View>
              </View>
            ))}
          </View>
        );

      case "softSkills":
        if (!content.skills.soft?.length) return null;
        return (
          <View key={sectionKey} style={styles.sidebarSection}>
            <Text style={styles.sidebarSectionTitle}>Soft Skills</Text>
            <View style={styles.sidebarSkillTags}>
              {content.skills.soft.map((skill, i) => (
                <Text key={i} style={styles.sidebarSkillTag}>{skill}</Text>
              ))}
            </View>
          </View>
        );

      case "customSkills":
        if (!content.skills.custom?.length) return null;
        return (
          <View key={sectionKey} style={styles.sidebarSection}>
            <Text style={styles.sidebarSectionTitle}>{content.skills.customSkillsHeader || "Custom Skills"}</Text>
            {content.skills.custom.map((group, idx) => (
              <View key={idx} style={styles.sidebarSkillGroup}>
                <Text style={styles.sidebarSkillHeader}>{group.header}</Text>
                <View style={styles.sidebarSkillTags}>
                  {group.items.map((skill, i) => (
                    <Text key={i} style={styles.sidebarSkillTag}>{skill}</Text>
                  ))}
                </View>
              </View>
            ))}
          </View>
        );

      case "languages":
        if (content.languages.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.sidebarSection}>
            <Text style={styles.sidebarSectionTitle}>Languages</Text>
            {content.languages.map((lang, idx) => (
              <Text key={idx} style={styles.sidebarText}>
                {lang.language} ({capitalize(lang.proficiency)})
              </Text>
            ))}
          </View>
        );

      case "certifications":
        if (content.certifications.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.sidebarSection}>
            <Text style={styles.sidebarSectionTitle}>Certifications</Text>
            {content.certifications.map((cert, idx) => (
              <View key={idx} style={styles.sidebarCertItem}>
                <Text style={styles.sidebarCertName}>{cert.name}</Text>
                {cert.issuer && <Text style={styles.sidebarCertIssuer}>{cert.issuer}</Text>}
                {cert.date && <Text style={styles.sidebarCertIssuer}>{cert.date}</Text>}
              </View>
            ))}
          </View>
        );

      default:
        return null;
    }
  };

  // Main content renderer
  const renderMainSection = (sectionKey: string) => {
    switch (sectionKey) {
      case "summary":
        if (!content.professionalSummary) return null;
        return (
          <View key={sectionKey} style={styles.mainSection}>
            <Text style={styles.mainSectionTitle}>Professional Summary</Text>
            <Text style={styles.mainSummary}>{stripHtml(content.professionalSummary)}</Text>
          </View>
        );

      case "experience":
        if (content.workExperience.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.mainSection}>
            <Text style={styles.mainSectionTitle}>Experience</Text>
            {content.workExperience.map((exp, idx) => (
              <View key={idx} style={styles.mainExperienceItem}>
                <View style={styles.mainExperienceHeader}>
                  <View style={{ flex: 1 }}>
                    <Text>
                      <Text style={styles.mainJobTitle}>{exp.title}</Text>
                      <Text style={styles.mainCompany}> @ {exp.company}</Text>
                    </Text>
                  </View>
                  <Text style={styles.mainDate}>
                    {formatDateRange(exp.startDate, exp.endDate, exp.isCurrent)}
                  </Text>
                </View>
                {exp.achievements.length > 0 && (
                  <View style={styles.mainBulletList}>
                    {exp.achievements.map((ach, i) => (
                      <View key={i} style={styles.mainBulletItem}>
                        <Text style={styles.mainBullet}>•</Text>
                        <Text style={styles.mainBulletText}>{stripHtml(ach)}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </View>
            ))}
          </View>
        );

      case "education":
        if (content.education.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.mainSection}>
            <Text style={styles.mainSectionTitle}>Education</Text>
            {content.education.map((edu, idx) => (
              <View key={idx} style={styles.mainEducationItem}>
                <View style={styles.mainExperienceHeader}>
                  <View>
                    <Text style={styles.mainDegree}>
                      {edu.degree}
                      {edu.fieldOfStudy && ` in ${edu.fieldOfStudy}`}
                    </Text>
                    <Text style={styles.mainInstitution}>{edu.institution}</Text>
                  </View>
                  <Text style={styles.mainDate}>
                    {edu.graduationDate}
                    {edu.gpa && ` • GPA: ${edu.gpa}`}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        );

      case "projects":
        if (content.projects.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.mainSection}>
            <Text style={styles.mainSectionTitle}>Projects</Text>
            {content.projects.map((proj, idx) => (
              <View key={idx} style={styles.mainProjectItem}>
                <Text>
                  <Text style={styles.mainProjectName}>{proj.name}</Text>
                  {proj.url && <Link src={proj.url} style={styles.mainLink}> [Link]</Link>}
                </Text>
                {proj.description && (
                  <Text style={styles.mainProjectDesc}>{stripHtml(proj.description)}</Text>
                )}
                {proj.technologies.length > 0 && (
                  <Text style={styles.mainProjectTech}>{proj.technologies.join(" • ")}</Text>
                )}
              </View>
            ))}
          </View>
        );

      case "awards":
        if (content.awards.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.mainSection}>
            <Text style={styles.mainSectionTitle}>Awards & Achievements</Text>
            {content.awards.map((award, idx) => (
              <View key={idx} style={styles.mainAwardItem}>
                <Text>
                  <Text style={styles.mainAwardTitle}>{award.title}</Text>
                  {award.issuer && ` - ${award.issuer}`}
                  {award.date && ` (${award.date})`}
                </Text>
                {award.description && (
                  <Text style={styles.mainAwardDesc}>{award.description}</Text>
                )}
              </View>
            ))}
          </View>
        );

      // Skills in main area (for templates that want it there)
      case "skills":
        if (!content.skills.technical?.length) return null;
        return (
          <View key={sectionKey} style={styles.mainSection}>
            <Text style={styles.mainSectionTitle}>Technical Skills</Text>
            {content.skills.technical.map((group, idx) => (
              <View key={idx} style={{ marginBottom: 6 }}>
                <Text style={{ fontSize: baseFontSize - 2, color: primaryColor, marginBottom: 4 }}>{group.header}</Text>
                <View style={styles.mainSkillTags}>
                  {group.items.map((skill, i) => (
                    <Text key={i} style={styles.mainSkillTag}>{skill}</Text>
                  ))}
                </View>
              </View>
            ))}
          </View>
        );

      case "certifications":
        if (content.certifications.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.mainSection}>
            <Text style={styles.mainSectionTitle}>Certifications</Text>
            {content.certifications.map((cert, idx) => (
              <View key={idx} style={{ marginBottom: 6, fontSize: baseFontSize - 2 }}>
                <Text>
                  <Text style={{ fontWeight: 600 }}>{cert.name}</Text>
                  {cert.issuer && ` - ${cert.issuer}`}
                  {cert.date && ` (${cert.date})`}
                </Text>
              </View>
            ))}
          </View>
        );

      case "languages":
        if (content.languages.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.mainSection}>
            <Text style={styles.mainSectionTitle}>Languages</Text>
            <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 12 }}>
              {content.languages.map((lang, idx) => (
                <Text key={idx} style={{ fontSize: baseFontSize - 2 }}>
                  {lang.language} ({capitalize(lang.proficiency)})
                </Text>
              ))}
            </View>
          </View>
        );

      default:
        return null;
    }
  };

  const currentTitle = content.workExperience[0]?.title;

  return (
    <Document>
      <Page size={pageSize} style={styles.page}>
        {/* Sidebar */}
        <View style={styles.sidebar}>
          {/* Profile */}
          {content.profilePictureUrl && (
            <Image src={content.profilePictureUrl} style={styles.sidebarProfileImage} />
          )}
          <Text style={styles.sidebarName}>{content.fullName || "John Doe"}</Text>
          {currentTitle && <Text style={styles.sidebarTitle}>{currentTitle}</Text>}
          
          {/* Contact */}
          {content.email && <Text style={styles.sidebarContact}>{content.email}</Text>}
          {content.phone && <Text style={styles.sidebarContact}>{content.phone}</Text>}
          {content.location && <Text style={styles.sidebarContact}>{content.location}</Text>}
          {content.linkedinUrl && (
            <Link src={content.linkedinUrl} style={{ ...styles.sidebarContact, ...styles.sidebarLink }}>LinkedIn</Link>
          )}
          {content.portfolioUrl && (
            <Link src={content.portfolioUrl} style={{ ...styles.sidebarContact, ...styles.sidebarLink }}>Portfolio</Link>
          )}
          {content.githubUrl && (
            <Link src={content.githubUrl} style={{ ...styles.sidebarContact, ...styles.sidebarLink }}>GitHub</Link>
          )}
          {content.customLinks?.map((link, idx) => (
            link.url && (
              <Link key={idx} src={link.url} style={{ ...styles.sidebarContact, ...styles.sidebarLink }}>
                {link.label || "Link"}
              </Link>
            )
          ))}

          {/* Sidebar Sections */}
          {sidebarSections.map(renderSidebarSection)}
        </View>

        {/* Main Content */}
        <View style={styles.main}>
          {mainSections.map(renderMainSection)}
        </View>
      </Page>
    </Document>
  );
}
