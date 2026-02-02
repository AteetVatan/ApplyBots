/**
 * Bronzor PDF template - Single-column, ATS-optimized.
 * Clean, minimalist design with profile picture left of name.
 */

import React from "react";
import {
  Document,
  Page,
  View,
  Text,
  Link,
  Image,
} from "@react-pdf/renderer";
import type { PDFTemplateProps } from "./types";
import { createSingleColumnStyles } from "./styles";
import { stripHtml, formatDateRange, capitalize } from "./utils";

export function BronzorPDF({ content, themeSettings }: PDFTemplateProps) {
  const styles = createSingleColumnStyles(themeSettings);
  const pageSize = themeSettings.pageSize === "a4" ? "A4" : "LETTER";

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
            <Text style={styles.sectionTitle}>Professional Summary</Text>
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
                  <View style={styles.experienceTitleRow}>
                    <Text style={styles.jobTitle}>{exp.title}</Text>
                    <Text style={styles.company}> | {exp.company}</Text>
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
                        <Text style={styles.bullet}>•</Text>
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
                <View style={styles.experienceHeader}>
                  <View style={styles.experienceTitleRow}>
                    <Text style={styles.jobTitle}>{edu.degree}</Text>
                    {edu.fieldOfStudy && <Text style={styles.company}> in {edu.fieldOfStudy}</Text>}
                    <Text style={styles.company}> | {edu.institution}</Text>
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
            <Text style={styles.sectionTitle}>Technical Skills</Text>
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
            <Text style={styles.skillItems}>{content.skills.soft.join(", ")}</Text>
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
                  {proj.url && (
                    <Link src={proj.url} style={styles.link}> [Link]</Link>
                  )}
                </Text>
                {proj.description && (
                  <Text style={styles.projectDescription}>{stripHtml(proj.description)}</Text>
                )}
                {proj.technologies.length > 0 && (
                  <Text style={styles.projectTech}>Technologies: {proj.technologies.join(", ")}</Text>
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
            <Text style={styles.sectionTitle}>Awards & Achievements</Text>
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
            <Text style={styles.sectionTitle}>Languages</Text>
            <View style={styles.languagesRow}>
              {content.languages.map((lang, idx) => (
                <Text key={idx} style={styles.languageItem}>
                  {lang.language} <Text style={styles.languageProficiency}>({capitalize(lang.proficiency)})</Text>
                  {idx < content.languages.length - 1 && "  •  "}
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
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerWithPhoto}>
            {content.profilePictureUrl && (
              <Image src={content.profilePictureUrl} style={styles.profileImage} />
            )}
            <View style={styles.headerContent}>
              <Text style={styles.name}>{content.fullName || "John Doe"}</Text>
              <View style={styles.contactRow}>
                {content.email && <Text style={styles.contactItem}>{content.email}</Text>}
                {content.phone && <Text style={styles.contactItem}> • {content.phone}</Text>}
                {content.location && <Text style={styles.contactItem}> • {content.location}</Text>}
              </View>
              <View style={styles.linksRow}>
                {content.linkedinUrl && (
                  <Link src={content.linkedinUrl} style={styles.link}>LinkedIn</Link>
                )}
                {content.portfolioUrl && (
                  <Link src={content.portfolioUrl} style={styles.link}>Portfolio</Link>
                )}
                {content.githubUrl && (
                  <Link src={content.githubUrl} style={styles.link}>GitHub</Link>
                )}
                {content.customLinks?.map((link, idx) => (
                  link.url && <Link key={idx} src={link.url} style={styles.link}>{link.label || "Link"}</Link>
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
