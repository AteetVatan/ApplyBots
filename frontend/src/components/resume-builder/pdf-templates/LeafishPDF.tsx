/**
 * Leafish PDF template - Single-column, ATS-optimized.
 * Single-column layout with green accent bars and modern typography.
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
import { getPDFFontFamily, getPDFBaseFontSize, getPDFSpacingMultiplier } from "./styles";
import { stripHtml, formatDateRange, capitalize } from "./utils";

export function LeafishPDF({ content, themeSettings }: PDFTemplateProps) {
  const pageSize = themeSettings.pageSize === "a4" ? "A4" : "LETTER";
  const baseFontSize = getPDFBaseFontSize(themeSettings);
  const spacing = getPDFSpacingMultiplier(themeSettings);
  const fontFamily = getPDFFontFamily(themeSettings);
  const primaryColor = themeSettings.primaryColor;

  const styles = StyleSheet.create({
    page: {
      padding: 36 * spacing,
      fontFamily,
      fontSize: baseFontSize,
      lineHeight: 1.4,
      color: "#1f2937",
    },
    header: {
      marginBottom: 16 * spacing,
      backgroundColor: primaryColor,
      padding: 20,
      marginHorizontal: -36 * spacing,
      marginTop: -36 * spacing,
    },
    headerContent: {
      flexDirection: "row",
      alignItems: "center",
      gap: 16,
    },
    profileImage: {
      width: 70,
      height: 70,
      borderRadius: 35,
      objectFit: "cover",
      borderWidth: 3,
      borderColor: "rgba(255,255,255,0.5)",
    },
    headerText: {
      flex: 1,
    },
    name: {
      fontSize: baseFontSize * 2.4,
      fontWeight: 700,
      color: "#ffffff",
      marginBottom: 4,
    },
    contactRow: {
      fontSize: baseFontSize,
      color: "rgba(255,255,255,0.9)",
      marginBottom: 2,
    },
    linksRow: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: 12,
      marginTop: 4,
      fontSize: baseFontSize,
    },
    headerLink: {
      color: "#ffffff",
      textDecoration: "none",
    },
    section: {
      marginBottom: 12 * spacing,
    },
    sectionHeader: {
      flexDirection: "row",
      alignItems: "center",
      marginBottom: 8 * spacing,
    },
    sectionAccent: {
      width: 4,
      height: 16,
      backgroundColor: primaryColor,
      marginRight: 8,
    },
    sectionTitle: {
      fontSize: baseFontSize + 1,
      fontWeight: 700,
      textTransform: "uppercase",
      letterSpacing: 0.5,
      color: "#111827",
    },
    summaryText: {
      fontSize: baseFontSize,
      color: "#374151",
      lineHeight: 1.5,
    },
    experienceItem: {
      marginBottom: 10 * spacing,
    },
    experienceHeader: {
      flexDirection: "row",
      justifyContent: "space-between",
      alignItems: "flex-start",
      marginBottom: 2,
    },
    jobTitle: {
      fontWeight: 600,
      color: "#111827",
    },
    company: {
      color: primaryColor,
    },
    dateLocation: {
      fontSize: baseFontSize - 1,
      color: "#6b7280",
    },
    bulletList: {
      paddingLeft: 12,
      marginTop: 4,
    },
    bulletItem: {
      flexDirection: "row",
      marginBottom: 2,
      fontSize: baseFontSize,
    },
    bullet: {
      width: 10,
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
      marginBottom: 4,
      fontSize: baseFontSize,
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
      fontSize: baseFontSize,
    },
    certName: {
      fontWeight: 600,
      color: "#111827",
    },
    certDetails: {
      color: "#4b5563",
    },
    projectItem: {
      marginBottom: 8 * spacing,
    },
    projectName: {
      fontWeight: 600,
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
      marginTop: 2,
    },
    awardItem: {
      marginBottom: 4,
      fontSize: baseFontSize,
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
    languagesRow: {
      flexDirection: "row",
      flexWrap: "wrap",
      gap: 16,
      fontSize: baseFontSize,
    },
    languageItem: {
      color: "#374151",
    },
    languageProficiency: {
      color: "#6b7280",
      fontStyle: "italic",
    },
    link: {
      color: primaryColor,
      textDecoration: "none",
    },
  });

  const DEFAULT_SECTION_ORDER = [
    "summary", "experience", "education", "skills", "softSkills", 
    "customSkills", "projects", "certifications", "awards", "languages"
  ];

  const sectionOrder = content.sectionOrder?.length > 0 
    ? content.sectionOrder.filter(s => s !== "contact")
    : DEFAULT_SECTION_ORDER;

  const renderSectionHeader = (title: string) => (
    <View style={styles.sectionHeader}>
      <View style={styles.sectionAccent} />
      <Text style={styles.sectionTitle}>{title}</Text>
    </View>
  );

  const renderSection = (sectionKey: string) => {
    switch (sectionKey) {
      case "summary":
        if (!content.professionalSummary) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            {renderSectionHeader("Professional Summary")}
            <Text style={styles.summaryText}>{stripHtml(content.professionalSummary)}</Text>
          </View>
        );

      case "experience":
        if (content.workExperience.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            {renderSectionHeader("Experience")}
            {content.workExperience.map((exp, idx) => (
              <View key={idx} style={styles.experienceItem}>
                <View style={styles.experienceHeader}>
                  <View style={{ flex: 1 }}>
                    <Text>
                      <Text style={styles.jobTitle}>{exp.title}</Text>
                      <Text style={styles.company}> @ {exp.company}</Text>
                    </Text>
                  </View>
                  <Text style={styles.dateLocation}>
                    {formatDateRange(exp.startDate, exp.endDate, exp.isCurrent)}
                    {exp.location && ` | ${exp.location}`}
                  </Text>
                </View>
                {exp.achievements.length > 0 && (
                  <View style={styles.bulletList}>
                    {exp.achievements.map((ach, i) => (
                      <View key={i} style={styles.bulletItem}>
                        <Text style={styles.bullet}>▸</Text>
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
            {renderSectionHeader("Education")}
            {content.education.map((edu, idx) => (
              <View key={idx} style={styles.educationItem}>
                <View style={styles.experienceHeader}>
                  <View style={{ flex: 1 }}>
                    <Text>
                      <Text style={styles.jobTitle}>{edu.degree}</Text>
                      {edu.fieldOfStudy && <Text style={styles.company}> in {edu.fieldOfStudy}</Text>}
                    </Text>
                    <Text style={{ fontSize: baseFontSize, color: "#4b5563" }}>{edu.institution}</Text>
                  </View>
                  <Text style={styles.dateLocation}>
                    {edu.graduationDate}
                    {edu.gpa && ` | GPA: ${edu.gpa}`}
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
            {renderSectionHeader("Technical Skills")}
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
            {renderSectionHeader("Soft Skills")}
            <Text style={styles.skillItems}>{content.skills.soft.join(", ")}</Text>
          </View>
        );

      case "customSkills":
        if (!content.skills.custom?.length) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            {renderSectionHeader(content.skills.customSkillsHeader || "Custom Skills")}
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
            {renderSectionHeader("Projects")}
            {content.projects.map((proj, idx) => (
              <View key={idx} style={styles.projectItem}>
                <Text>
                  <Text style={styles.projectName}>{proj.name}</Text>
                  {proj.url && <Link src={proj.url} style={styles.link}> [Link]</Link>}
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
            {renderSectionHeader("Certifications")}
            {content.certifications.map((cert, idx) => (
              <View key={idx} style={styles.certificationItem}>
                <Text>
                  <Text style={styles.certName}>{cert.name}</Text>
                  {cert.issuer && <Text style={styles.certDetails}> - {cert.issuer}</Text>}
                  {cert.date && <Text style={styles.certDetails}> ({cert.date})</Text>}
                  {cert.url && <Link src={cert.url} style={styles.link}> [Link]</Link>}
                </Text>
              </View>
            ))}
          </View>
        );

      case "awards":
        if (content.awards.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            {renderSectionHeader("Awards & Achievements")}
            {content.awards.map((award, idx) => (
              <View key={idx} style={styles.awardItem}>
                <Text>
                  <Text style={styles.awardTitle}>{award.title}</Text>
                  {award.issuer && <Text style={styles.certDetails}> - {award.issuer}</Text>}
                  {award.date && <Text style={styles.certDetails}> ({award.date})</Text>}
                </Text>
                {award.description && (
                  <Text style={styles.awardDescription}>{award.description}</Text>
                )}
              </View>
            ))}
          </View>
        );

      case "languages":
        if (content.languages.length === 0) return null;
        return (
          <View key={sectionKey} style={styles.section}>
            {renderSectionHeader("Languages")}
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
        {/* Header with colored background */}
        <View style={styles.header}>
          <View style={styles.headerContent}>
            {content.profilePictureUrl && (
              <Image src={content.profilePictureUrl} style={styles.profileImage} />
            )}
            <View style={styles.headerText}>
              <Text style={styles.name}>{content.fullName || "John Doe"}</Text>
              <View style={styles.contactRow}>
                {content.email && <Text>{content.email}</Text>}
                {content.phone && <Text>  •  {content.phone}</Text>}
                {content.location && <Text>  •  {content.location}</Text>}
              </View>
              <View style={styles.linksRow}>
                {content.linkedinUrl && <Link src={content.linkedinUrl} style={styles.headerLink}>LinkedIn</Link>}
                {content.portfolioUrl && <Link src={content.portfolioUrl} style={styles.headerLink}>Portfolio</Link>}
                {content.githubUrl && <Link src={content.githubUrl} style={styles.headerLink}>GitHub</Link>}
                {content.customLinks?.map((link, idx) => (
                  link.url && <Link key={idx} src={link.url} style={styles.headerLink}>{link.label || "Link"}</Link>
                ))}
              </View>
            </View>
          </View>
        </View>

        {/* Sections */}
        {sectionOrder.map(renderSection)}
      </Page>
    </Document>
  );
}
