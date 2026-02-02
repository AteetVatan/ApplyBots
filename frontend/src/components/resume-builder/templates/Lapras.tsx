/**
 * Lapras resume template.
 *
 * Single-column layout with pink/magenta header accent.
 * ATS Score: 95
 */

import React from "react";
import type { ResumeTemplateProps } from "./types";
import type { ThemeSettings } from "@/stores/resume-builder-store";
import {
  getFontFamily,
  getPrimaryColor,
  getPrimaryColorDark,
  getPrimaryColorWithOpacity,
  getPrimaryGradient,
  getThemeCSSVariables,
} from "./theme-utils";

const DEFAULT_THEME: ThemeSettings = {
  primaryColor: "#3b82f6",
  fontFamily: "Inter",
  fontSize: "medium",
  spacing: "normal",
  pageSize: "letter",
};

const DEFAULT_SECTION_ORDER = [
  "contact",
  "summary",
  "experience",
  "education",
  "skills",
  "softSkills",
  "customSkills",
  "projects",
  "certifications",
  "awards",
  "languages",
];

export function Lapras({
  content,
  scale = 1,
  highlightSection,
  themeSettings = DEFAULT_THEME,
}: ResumeTemplateProps) {
  const highlight = (section: string) =>
    highlightSection === section ? "bg-pink-50 ring-2 ring-pink-200 ring-inset" : "";

  const primaryColor = getPrimaryColor(themeSettings);
  const primaryDark = getPrimaryColorDark(themeSettings);
  const primaryLight = getPrimaryColorWithOpacity(themeSettings, 0.1);
  const cssVars = getThemeCSSVariables(themeSettings);

  return (
    <div
      className="bg-white text-gray-900 shadow-lg"
      style={{
        ...cssVars,
        width: "8.5in",
        minHeight: "11in",
        transform: `scale(${scale})`,
        transformOrigin: "top left",
        fontFamily: getFontFamily(themeSettings),
        fontSize: "var(--font-base)",
        lineHeight: 1.5,
      } as React.CSSProperties}
    >
      {/* Header with gradient */}
      <header
        className={`px-8 py-6 text-white ${highlight("contact")}`}
        style={{ background: getPrimaryGradient(themeSettings) }}
      >
        <div className="flex items-start gap-5">
          {content.profilePictureUrl && (
            <img
              src={content.profilePictureUrl}
              alt="Profile"
              className="w-24 h-24 rounded-full object-cover border-4 border-white/30 flex-shrink-0"
            />
          )}
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-white mb-1">
              {content.fullName || "Your Name"}
            </h1>
            {content.workExperience[0]?.title && (
              <p className="text-white/90 font-medium mb-3" style={{ fontSize: "var(--font-body)" }}>
                {content.workExperience[0].title}
              </p>
            )}
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-white/80" style={{ fontSize: "var(--font-small)" }}>
              {content.email && <span>{content.email}</span>}
              {content.phone && <span>{content.phone}</span>}
              {content.location && <span>{content.location}</span>}
            </div>
            <div className="flex flex-wrap gap-3 mt-2" style={{ fontSize: "var(--font-small)" }}>
              {content.linkedinUrl && (
                <a href={content.linkedinUrl} target="_blank" rel="noopener noreferrer" className="text-white/80 hover:text-white underline">
                  LinkedIn
                </a>
              )}
              {content.portfolioUrl && (
                <a href={content.portfolioUrl} target="_blank" rel="noopener noreferrer" className="text-white/80 hover:text-white underline">
                  Portfolio
                </a>
              )}
              {content.githubUrl && (
                <a href={content.githubUrl} target="_blank" rel="noopener noreferrer" className="text-white/80 hover:text-white underline">
                  GitHub
                </a>
              )}
              {content.customLinks?.map((link) => (
                link.url && (
                  <a key={link.id} href={link.url} target="_blank" rel="noopener noreferrer" className="text-white/80 hover:text-white underline">
                    {link.label || "Link"}
                  </a>
                )
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <div className="px-8 py-6">
        {/* Render sections based on sectionOrder */}
        {(content.sectionOrder && content.sectionOrder.length > 0 
          ? content.sectionOrder 
          : DEFAULT_SECTION_ORDER)
          .filter((key) => key !== "contact")
          .map((sectionKey) => {
            // Summary
            if (sectionKey === "summary" && content.professionalSummary) {
              return (
                <section key={sectionKey} className={`mb-5 ${highlight("summary")}`}>
                  <h2 className="font-bold uppercase tracking-wider mb-2 pb-1 border-b-2" style={{ fontSize: "var(--font-header)", borderColor: primaryColor, color: primaryDark }}>
                    About Me
                  </h2>
                  <div
                    className="text-gray-700 leading-relaxed"
                    style={{ fontSize: "var(--font-body)" }}
                    dangerouslySetInnerHTML={{ __html: content.professionalSummary }}
                  />
                </section>
              );
            }

            // Experience
            if (sectionKey === "experience" && content.workExperience.length > 0) {
              return (
                <section key={sectionKey} className={`mb-5 ${highlight("experience")}`}>
                  <h2 className="font-bold uppercase tracking-wider mb-3 pb-1 border-b-2" style={{ fontSize: "var(--font-header)", borderColor: primaryColor, color: primaryDark }}>
                    Experience
                  </h2>
                  <div className="space-y-4">
                    {content.workExperience.map((exp) => (
                      <div key={exp.id} className="relative pl-4" style={{ borderLeft: `2px solid ${primaryLight}` }}>
                        <div
                          className="absolute -left-1.5 top-1 w-3 h-3 rounded-full"
                          style={{ backgroundColor: primaryColor }}
                        ></div>
                        <div className="flex justify-between items-baseline mb-0.5">
                          <div>
                            <span className="font-semibold text-gray-900">{exp.title}</span>
                            <span style={{ color: primaryColor }}> • {exp.company}</span>
                          </div>
                          <span className="text-gray-500" style={{ fontSize: "var(--font-small)" }}>
                            {exp.startDate} — {exp.endDate || (exp.isCurrent ? "Present" : "")}
                          </span>
                        </div>
                        {exp.location && (
                          <div className="text-gray-500" style={{ fontSize: "var(--font-small)" }}>{exp.location}</div>
                        )}
                        {exp.achievements.length > 0 && (
                          <ul className="mt-1.5 text-gray-700 space-y-1" style={{ fontSize: "var(--font-body)" }}>
                            {exp.achievements.map((ach, i) => (
                              <li key={i} className="flex items-start gap-2">
                                <span style={{ color: primaryColor }}>›</span>
                                <span dangerouslySetInnerHTML={{ __html: ach || "" }} />
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              );
            }

            // Education
            if (sectionKey === "education" && content.education.length > 0) {
              return (
                <section key={sectionKey} className={`mb-5 ${highlight("education")}`}>
                  <h2 className="font-bold uppercase tracking-wider mb-3 pb-1 border-b-2" style={{ fontSize: "var(--font-header)", borderColor: primaryColor, color: primaryDark }}>
                    Education
                  </h2>
                  <div className="space-y-3">
                    {content.education.map((edu) => (
                      <div key={edu.id} className="pl-4" style={{ borderLeft: `2px solid ${primaryLight}` }}>
                        <div className="flex justify-between items-baseline">
                          <div>
                            <span className="font-semibold text-gray-900">{edu.degree}</span>
                            {edu.fieldOfStudy && (
                              <span className="text-gray-600"> in {edu.fieldOfStudy}</span>
                            )}
                          </div>
                          <span className="text-gray-500" style={{ fontSize: "var(--font-small)" }}>{edu.graduationDate}</span>
                        </div>
                        <div style={{ color: primaryColor, fontSize: "var(--font-body)" }}>{edu.institution}</div>
                        {edu.gpa && (
                          <div className="text-gray-500" style={{ fontSize: "var(--font-small)" }}>GPA: {edu.gpa}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              );
            }

            // Technical Skills
            if (sectionKey === "skills" && (content.skills.technical?.length ?? 0) > 0) {
              return (
                <section key={sectionKey} className={`mb-5 ${highlight("skills")}`}>
                  <h2 className="font-bold uppercase tracking-wider mb-3 pb-1 border-b-2" style={{ fontSize: "var(--font-header)", borderColor: primaryColor, color: primaryDark }}>
                    Technical Skills
                  </h2>
                  <div className="space-y-2" style={{ fontSize: "var(--font-body)" }}>
                    {content.skills.technical.map((group) => (
                      <div key={group.id}>
                        <span className="font-medium" style={{ color: primaryColor }}>{group.header}: </span>
                        <span className="text-gray-700">{group.items.join(" • ")}</span>
                      </div>
                    ))}
                  </div>
                </section>
              );
            }

            // Soft Skills
            if (sectionKey === "softSkills" && (content.skills.soft?.length ?? 0) > 0) {
              return (
                <section key={sectionKey} className={`mb-5 ${highlight("softSkills")}`}>
                  <h2 className="font-bold uppercase tracking-wider mb-3 pb-1 border-b-2" style={{ fontSize: "var(--font-header)", borderColor: primaryColor, color: primaryDark }}>
                    Soft Skills
                  </h2>
                  <p className="text-gray-700" style={{ fontSize: "var(--font-body)" }}>
                    {content.skills.soft.join(" • ")}
                  </p>
                </section>
              );
            }

            // Custom Skills
            if (sectionKey === "customSkills" && (content.skills.custom?.length ?? 0) > 0) {
              return (
                <section key={sectionKey} className={`mb-5 ${highlight("customSkills")}`}>
                  <h2 className="font-bold uppercase tracking-wider mb-3 pb-1 border-b-2" style={{ fontSize: "var(--font-header)", borderColor: primaryColor, color: primaryDark }}>
                    {content.skills.customSkillsHeader || "Custom Skills"}
                  </h2>
                  <div className="space-y-2" style={{ fontSize: "var(--font-body)" }}>
                    {content.skills.custom.map((group) => (
                      <div key={group.id}>
                        <span className="font-medium" style={{ color: primaryColor }}>{group.header}: </span>
                        <span className="text-gray-700">{group.items.join(" • ")}</span>
                      </div>
                    ))}
                  </div>
                </section>
              );
            }

            // Projects
            if (sectionKey === "projects" && content.projects.length > 0) {
              return (
                <section key={sectionKey} className={`mb-5 ${highlight("projects")}`}>
                  <h2 className="font-bold uppercase tracking-wider mb-3 pb-1 border-b-2" style={{ fontSize: "var(--font-header)", borderColor: primaryColor, color: primaryDark }}>
                    Projects
                  </h2>
                  <div className="space-y-3">
                    {content.projects.map((proj) => (
                      <div key={proj.id} className="pl-4" style={{ borderLeft: `2px solid ${primaryLight}` }}>
                        <div className="font-semibold text-gray-900">
                          {proj.name}
                          {proj.url && (
                            <a href={proj.url} target="_blank" rel="noopener noreferrer" className="ml-2 hover:underline" style={{ fontSize: "var(--font-small)", color: primaryColor }}>
                              [View]
                            </a>
                          )}
                        </div>
                        <div
                          className="text-gray-700"
                          style={{ fontSize: "var(--font-body)" }}
                          dangerouslySetInnerHTML={{ __html: proj.description || "" }}
                        />
                        {proj.technologies.length > 0 && (
                          <p className="mt-0.5" style={{ fontSize: "var(--font-xs)", color: primaryColor }}>
                            {proj.technologies.join(" • ")}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                </section>
              );
            }

            // Certifications
            if (sectionKey === "certifications" && content.certifications.length > 0) {
              return (
                <section key={sectionKey} className={`mb-5 ${highlight("certifications")}`}>
                  <h2 className="font-bold uppercase tracking-wider mb-2 pb-1 border-b-2" style={{ fontSize: "var(--font-header)", borderColor: primaryColor, color: primaryDark }}>
                    Certifications
                  </h2>
                  {content.certifications.map((cert) => (
                    <div key={cert.id} className="mb-1" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-medium">{cert.name}</span>
                      {cert.issuer && <span className="text-gray-500"> - {cert.issuer}</span>}
                      {cert.url && (
                        <a href={cert.url} target="_blank" rel="noopener noreferrer" className="ml-1 hover:underline" style={{ fontSize: "var(--font-xs)", color: primaryColor }}>
                          [Link]
                        </a>
                      )}
                    </div>
                  ))}
                </section>
              );
            }

            // Awards
            if (sectionKey === "awards" && content.awards.length > 0) {
              return (
                <section key={sectionKey} className={`mb-5 ${highlight("awards")}`}>
                  <h2 className="font-bold uppercase tracking-wider mb-2 pb-1 border-b-2" style={{ fontSize: "var(--font-header)", borderColor: primaryColor, color: primaryDark }}>
                    Awards
                  </h2>
                  {content.awards.map((award) => (
                    <div key={award.id} className="mb-1" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-medium">{award.title}</span>
                      {award.date && <span style={{ color: primaryColor }}> ({award.date})</span>}
                    </div>
                  ))}
                </section>
              );
            }

            // Languages
            if (sectionKey === "languages" && content.languages.length > 0) {
              return (
                <section key={sectionKey} className={`mb-5 ${highlight("languages")}`}>
                  <h2 className="font-bold uppercase tracking-wider mb-2 pb-1 border-b-2" style={{ fontSize: "var(--font-header)", borderColor: primaryColor, color: primaryDark }}>
                    Languages
                  </h2>
                  <div className="flex flex-wrap gap-4" style={{ fontSize: "var(--font-body)" }}>
                    {content.languages.map((lang) => (
                      <span key={lang.id}>
                        <span className="font-medium">{lang.language}</span>
                        <span style={{ color: primaryColor }}> ({lang.proficiency})</span>
                      </span>
                    ))}
                  </div>
                </section>
              );
            }

            // Custom Sections
            if (sectionKey === "custom" && content.customSections.length > 0) {
              return (
                <React.Fragment key={sectionKey}>
                  {content.customSections.map((section) => (
                    <section key={section.id} className={`mb-5 ${highlight("custom")}`}>
                      <h2 className="font-bold uppercase tracking-wider mb-2 pb-1 border-b-2" style={{ fontSize: "var(--font-header)", borderColor: primaryColor, color: primaryDark }}>
                        {section.title}
                      </h2>
                      <ul className="text-gray-700 space-y-1" style={{ fontSize: "var(--font-body)" }}>
                        {section.items.map((item, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span style={{ color: primaryColor }}>›</span>
                            <span>{item}</span>
                          </li>
                        ))}
                      </ul>
                    </section>
                  ))}
                </React.Fragment>
              );
            }

            return null;
          })}
      </div>
    </div>
  );
}
