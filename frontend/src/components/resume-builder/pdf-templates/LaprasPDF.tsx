/**
 * Lapras PDF template - Single-column, ATS-optimized.
 * Single-column layout with pink/magenta header accent and elegant serif typography.
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
import type { PDFTemplateProps } from "./types";
import { getPDFBaseFontSize, getPDFSpacingMultiplier } from "./styles";
import { stripHtml, formatDateRange, capitalize } from "./utils";

export function LaprasPDF({ content, themeSettings }: PDFTemplateProps) {
  const pageSize = themeSettings.pageSize === "a4" ? "A4" : "LETTER";
  const baseFontSize = getPDFBaseFontSize(themeSettings);
  const spacing = getPDFSpacingMultiplier(themeSettings);
  const primaryColor = themeSettings.primaryColor;
  // Use Georgia for elegant serif look
  const fontFamily = "Georgia";

  const styles = StyleSheet.create({
    page: {
      padding: 40 * spacing,
      fontFamily,
      fontSize: baseFontSize,
      lineHeight: 1.5,
      color: "#1f2937",
    },
    headerAccent: {
      height: 4,
      backgroundColor: primaryColor,
      marginBottom: 20,
    },
    header: {
      marginBottom: 16 * spacing,
      textAlign: "center",
    },
    profileImage: {
      width: 80,
      height: 80,
      borderRadius: 40,
      objectFit: "cover",
      alignSelf: "center",
      marginBottom: 12,
      borderWidth: 2,
      borderColor: primaryColor,
    },
    name: {
      fontSize: baseFontSize * 2.6,
      fontWeight: 700,
      color: "#111827",
      marginBottom: 8,
      textAlign: "center",
    },
    contactRow: {
      fontSize: baseFontSize,
      color: "#4b5563",
      textAlign: "center",
      marginBottom: 4,
    },
    linksRow: {
      flexDirection: "row",
      justifyContent: "center",
      gap: 16,
      marginTop: 8,
      fontSize: baseFontSize,
    },
    link: {
      color: primaryColor,
      textDecoration: "none",
    },
    divider: {
      height: 1,
      backgroundColor: "#e5e7eb",
      marginVertical: 12,
    },
    section: {
      marginBottom: 12 * spacing,
    },
    sectionTitle: {
      fontSize: baseFontSize + 2,
      fontWeight: 700,
      marginBottom: 8 * spacing,
      color: primaryColor,
      textAlign: "center",
      textTransform: "uppercase",
      letterSpacing: 2,
    },
    summaryText: {
      fontSize: baseFontSize,
      color: "#374151",
      lineHeight: 1.6,
      textAlign: "center",
      fontStyle: "italic",
    },
    experienceItem: {
      marginBottom: 10 * spacing,
    },
    experienceHeader: {
      marginBottom: 4,
    },
    jobTitleRow: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "flex-start",
    },
    jobTitle: {
      fontWeight: 700,
      color: "#111827",
      fontSize: baseFontSize + 0.5,
    },
    company: {
      color: primaryColor,
      fontStyle: "italic",
    },
    dateLocation: {
      fontSize: baseFontSize - 1,
      color: "#6b7280",
    },
    bulletList: {
      paddingLeft: 16,
      marginTop: 6,
    },
    bulletItem: {
      flexDirection: "row",
      marginBottom: 3,
      fontSize: baseFontSize,
    },
    bullet: {
      width: 12,
      color: primaryColor,
    },
    bulletText: {
      flex: 1,
      color: "#374151",
    },
    educationItem: {
      marginBottom: 8 * spacing,
    },
    skillsRow: {
      marginBottom: 6,
      fontSize: baseFontSize,
    },
    skillHeader: {
      fontWeight: 700,
      color: "#111827",
    },
    skillItems: {
      color: "#374151",
    },
    certificationItem: {
      marginBottom: 6,
      fontSize: baseFontSize,
      textAlign: "center",
    },
    certName: {
      fontWeight: 700,
      color: "#111827",
    },
    certDetails: {
      color: "#4b5563",
    },
    projectItem: {
      marginBottom: 8 * spacing,
    },
    projectName: {
      fontWeight: 700,
      color: "#111827",
    },
    projectDescription: {
      fontSize: baseFontSize,
      color: "#374151",
      marginTop: 2,
    },
    projectTech: {
      fontSize: baseFontSize - 1,
      color: primaryColor,
      fontStyle: "italic",
      marginTop: 2,
    },
    awardItem: {
      marginBottom: 6,
      fontSize: baseFontSize,
      textAlign: "center",
    },
    awardTitle: {
      fontWeight: 700,
      color: "#111827",
    },
    awardDescription: {
      fontSize: baseFontSize - 1,
      color: "#6b7280",
      marginTop: 2,
    },
    languagesRow: {
      flexDirection: "row",
      justifyContent: "center",
      flexWrap: "wrap",
      gap: 20,
      fontSize: baseFontSize,
    },
    languageItem: {
      color: "#374151",
    },
    languageProficiency: {
      color: "#6b7280",
      fontStyle: "italic",
    },
  });

  const DEFAULT_SECTION_ORDER = [
    "summary", "experience", "education", "skills", "softSkills", 
    "customSkills", "projects", "certifications", "awards", "languages"
  ];

  const sectionOrder = content.sectionOrder?.length > 0 
    ? content.sectionOrder.filter(s => s !== "contact")
    : DEFAULT_SECTION_ORDER;

  const renderSection = (sectionKey: string) => {
    switch (sectionKey) {
      case "summary":
        if (!content.professionalSummary) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            <Text style={styles.sectionTitle}>About Me</Text>
            <Text style={styles.summaryText}>{stripHtml(content.professionalSummary)}</Text>
          </View>
        );

      case "experience":
        if (content.workExperience.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            <Text style={styles.sectionTitle}>Experience</Text>
            {content.workExperience.map((exp, idx) => (
              <View key={idx} style={styles.experienceItem}>
                <View style={styles.experienceHeader}>
                  <View style={styles.jobTitleRow}>
                    <Text style={styles.jobTitle}>{exp.title}</Text>
                    <Text style={styles.dateLocation}>
                      {formatDateRange(exp.startDate, exp.endDate, exp.isCurrent)}
                    </Text>
                  </View>
                  <Text style={styles.company}>{exp.company}{exp.location && ` • ${exp.location}`}</Text>
                </View>
                {exp.achievements.length > 0 && (
                  <View style={styles.bulletList}>
                    {exp.achievements.map((ach, i) => (
                      <View key={i} style={styles.bulletItem}>
                        <Text style={styles.bullet}>◆</Text>
                        <Text style={styles.bulletText}>{stripHtml(ach)}</Text>
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
          <View key={sectionKey} style={styles.section}>
            <Text style={styles.sectionTitle}>Education</Text>
            {content.education.map((edu, idx) => (
              <View key={idx} style={styles.educationItem}>
                <View style={styles.jobTitleRow}>
                  <View>
                    <Text style={styles.jobTitle}>{edu.degree}</Text>
                    {edu.fieldOfStudy && <Text style={styles.company}>{edu.fieldOfStudy}</Text>}
                    <Text style={styles.company}>{edu.institution}</Text>
                  </View>
                  <Text style={styles.dateLocation}>
                    {edu.graduationDate}
                    {edu.gpa && ` • GPA: ${edu.gpa}`}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        );

      case "skills":
        if (!content.skills.technical?.length) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            <Text style={styles.sectionTitle}>Skills</Text>
            {content.skills.technical.map((group, idx) => (
              <View key={idx} style={styles.skillsRow}>
                <Text>
                  <Text style={styles.skillHeader}>{group.header}: </Text>
                  <Text style={styles.skillItems}>{group.items.join(", ")}</Text>
                </Text>
              </View>
            ))}
          </View>
        );

      case "softSkills":
        if (!content.skills.soft?.length) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            <Text style={styles.sectionTitle}>Soft Skills</Text>
            <Text style={{ ...styles.skillItems, textAlign: "center" }}>{content.skills.soft.join("  •  ")}</Text>
          </View>
        );

      case "customSkills":
        if (!content.skills.custom?.length) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            <Text style={styles.sectionTitle}>{content.skills.customSkillsHeader || "Custom Skills"}</Text>
            {content.skills.custom.map((group, idx) => (
              <View key={idx} style={styles.skillsRow}>
                <Text>
                  <Text style={styles.skillHeader}>{group.header}: </Text>
                  <Text style={styles.skillItems}>{group.items.join(", ")}</Text>
                </Text>
              </View>
            ))}
          </View>
        );

      case "projects":
        if (content.projects.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            <Text style={styles.sectionTitle}>Projects</Text>
            {content.projects.map((proj, idx) => (
              <View key={idx} style={styles.projectItem}>
                <Text>
                  <Text style={styles.projectName}>{proj.name}</Text>
                  {proj.url && <Link src={proj.url} style={styles.link}> [View]</Link>}
                </Text>
                {proj.description && (
                  <Text style={styles.projectDescription}>{stripHtml(proj.description)}</Text>
                )}
                {proj.technologies.length > 0 && (
                  <Text style={styles.projectTech}>{proj.technologies.join(" • ")}</Text>
                )}
              </View>
            ))}
          </View>
        );

      case "certifications":
        if (content.certifications.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            <Text style={styles.sectionTitle}>Certifications</Text>
            {content.certifications.map((cert, idx) => (
              <View key={idx} style={styles.certificationItem}>
                <Text>
                  <Text style={styles.certName}>{cert.name}</Text>
                  {cert.issuer && <Text style={styles.certDetails}> — {cert.issuer}</Text>}
                  {cert.date && <Text style={styles.certDetails}> ({cert.date})</Text>}
                </Text>
              </View>
            ))}
          </View>
        );

      case "awards":
        if (content.awards.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            <Text style={styles.sectionTitle}>Awards</Text>
            {content.awards.map((award, idx) => (
              <View key={idx} style={styles.awardItem}>
                <Text>
                  <Text style={styles.awardTitle}>{award.title}</Text>
                  {award.issuer && <Text style={styles.certDetails}> — {award.issuer}</Text>}
                  {award.date && <Text style={styles.certDetails}> ({award.date})</Text>}
                </Text>
              </View>
            ))}
          </View>
        );

      case "languages":
        if (content.languages.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            <Text style={styles.sectionTitle}>Languages</Text>
            <View style={styles.languagesRow}>
              {content.languages.map((lang, idx) => (
                <Text key={idx} style={styles.languageItem}>
                  {lang.language} <Text style={styles.languageProficiency}>({capitalize(lang.proficiency)})</Text>
                </Text>
              ))}
            </View>
          </View>
        );

      default:
        return null;
    }
  };

  return (
    <Document>
      <Page size={pageSize} style={styles.page}>
        {/* Header Accent */}
        <View style={styles.headerAccent} />
        
        {/* Header */}
        <View style={styles.header}>
          {content.profilePictureUrl && (
            <Image src={content.profilePictureUrl} style={styles.profileImage} />
          )}
          <Text style={styles.name}>{content.fullName || "John Doe"}</Text>
          <View style={styles.contactRow}>
            {content.email && <Text>{content.email}</Text>}
            {content.phone && <Text>  •  {content.phone}</Text>}
            {content.location && <Text>  •  {content.location}</Text>}
          </View>
          <View style={styles.linksRow}>
            {content.linkedinUrl && <Link src={content.linkedinUrl} style={styles.link}>LinkedIn</Link>}
            {content.portfolioUrl && <Link src={content.portfolioUrl} style={styles.link}>Portfolio</Link>}
            {content.githubUrl && <Link src={content.githubUrl} style={styles.link}>GitHub</Link>}
            {content.customLinks?.map((link, idx) => (
              link.url && <Link key={idx} src={link.url} style={styles.link}>{link.label || "Link"}</Link>
            ))}
          </View>
        </View>

        <View style={styles.divider} />

        {/* Sections */}
        {sectionOrder.map(renderSection)}
      </Page>
    </Document>
  );
}
