/**
 * Leafish resume template.
 *
 * Single-column layout with green accent bars and modern typography.
 * ATS Score: 95
 */

import React from "react";
import type { ResumeTemplateProps } from "./types";
import type { ThemeSettings } from "@/stores/resume-builder-store";
import {
  getFontFamily,
  getSpacingMultiplier,
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

export function Leafish({
  content,
  scale = 1,
  highlightSection,
  themeSettings = DEFAULT_THEME,
}: ResumeTemplateProps) {
  const highlight = (section: string) =>
    highlightSection === section ? "bg-lime-50 ring-2 ring-lime-200 ring-inset" : "";
  
  const spacingMultiplier = getSpacingMultiplier(themeSettings);
  const basePadding = 0.5;
  const padding = `${basePadding * spacingMultiplier}in`;

  // CSS custom properties for consistent font sizing (don't compound like %)
  const cssVars = getThemeCSSVariables(themeSettings);

  return (
    <div
      className="bg-white text-gray-900 shadow-lg"
      style={{
        ...cssVars,
        width: "8.5in",
        minHeight: "11in",
        padding,
        transform: `scale(${scale})`,
        transformOrigin: "top left",
        fontFamily: getFontFamily(themeSettings),
        fontSize: "var(--font-base)",
        lineHeight: 1.5,
      } as React.CSSProperties}
    >
      {/* Header */}
      <header className={`mb-5 ${highlight("contact")}`}>
        <div className="flex items-start gap-4">
          {content.profilePictureUrl && (
            <img
              src={content.profilePictureUrl}
              alt="Profile"
              className="w-20 h-20 rounded-lg object-cover border-2 border-lime-400"
            />
          )}
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <div
                className="w-1 h-12 rounded"
                style={{ background: getPrimaryGradient(themeSettings) }}
              ></div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {content.fullName || "Your Name"}
                </h1>
                {content.workExperience[0]?.title && (
                  <p
                    className="text-lime-600 font-medium"
                    style={{ fontSize: "var(--font-body)" }}
                  >
                    {content.workExperience[0].title}
                  </p>
                )}
              </div>
            </div>
            <div
              className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-3 text-gray-600"
              style={{ fontSize: "var(--font-small)" }}
            >
              {content.email && (
                <span className="flex items-center gap-1">
                  <span className="text-lime-500">✉</span> {content.email}
                </span>
              )}
              {content.phone && (
                <span className="flex items-center gap-1">
                  <span className="text-lime-500">☎</span> {content.phone}
                </span>
              )}
              {content.location && (
                <span className="flex items-center gap-1">
                  <span className="text-lime-500">◎</span> {content.location}
                </span>
              )}
            </div>
            <div
              className="flex flex-wrap gap-3 mt-2"
              style={{ fontSize: "var(--font-small)" }}
            >
              {content.linkedinUrl && (
                <a href={content.linkedinUrl} target="_blank" rel="noopener noreferrer" className="text-lime-600 hover:underline">
                  LinkedIn
                </a>
              )}
              {content.portfolioUrl && (
                <a href={content.portfolioUrl} target="_blank" rel="noopener noreferrer" className="text-lime-600 hover:underline">
                  Portfolio
                </a>
              )}
              {content.githubUrl && (
                <a href={content.githubUrl} target="_blank" rel="noopener noreferrer" className="text-lime-600 hover:underline">
                  GitHub
                </a>
              )}
              {content.customLinks?.map((link) => (
                link.url && (
                  <a key={link.id} href={link.url} target="_blank" rel="noopener noreferrer" className="text-lime-600 hover:underline">
                    {link.label || "Link"}
                  </a>
                )
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Render sections based on sectionOrder */}
      {(content.sectionOrder && content.sectionOrder.length > 0 
        ? content.sectionOrder 
        : DEFAULT_SECTION_ORDER)
        .filter((key) => key !== "contact")
        .map((sectionKey) => {
          // Summary
          if (sectionKey === "summary" && content.professionalSummary) {
            return (
              <section key={sectionKey} className={`mb-4 ${highlight("summary")}`}>
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-8 h-1 bg-lime-500 rounded"></div>
                  <h2
                    className="font-bold uppercase tracking-wider text-gray-800"
                    style={{ fontSize: "var(--font-header)" }}
                  >
                    About
                  </h2>
                </div>
                <div
                  className="text-gray-600 leading-relaxed pl-10"
                  style={{ fontSize: "var(--font-body)" }}
                  dangerouslySetInnerHTML={{ __html: content.professionalSummary }}
                />
              </section>
            );
          }

          // Experience
          if (sectionKey === "experience" && content.workExperience.length > 0) {
            return (
              <section key={sectionKey} className={`mb-4 ${highlight("experience")}`}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-1 bg-lime-500 rounded"></div>
                  <h2
                    className="font-bold uppercase tracking-wider text-gray-800"
                    style={{ fontSize: "var(--font-header)" }}
                  >
                    Experience
                  </h2>
                </div>
                <div className="pl-10 space-y-3">
                  {content.workExperience.map((exp) => (
                    <div key={exp.id} className="relative">
                      <div className="absolute -left-6 top-1 w-2 h-2 bg-lime-400 rounded-full"></div>
                      <div className="flex justify-between items-baseline mb-0.5">
                        <div>
                          <span className="font-bold text-gray-900">{exp.title}</span>
                          <span className="text-lime-600 ml-1">• {exp.company}</span>
                        </div>
                        <span
                          className="text-gray-500"
                          style={{ fontSize: "var(--font-small)" }}
                        >
                          {exp.startDate} — {exp.endDate || (exp.isCurrent ? "Present" : "")}
                        </span>
                      </div>
                      {exp.location && (
                        <div
                          className="text-gray-500"
                          style={{ fontSize: "var(--font-small)" }}
                        >
                          {exp.location}
                        </div>
                      )}
                      {exp.achievements.length > 0 && (
                        <ul
                          className="mt-1 text-gray-600 space-y-0.5"
                          style={{ fontSize: "var(--font-body)" }}
                        >
                          {exp.achievements.map((ach, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="text-lime-400 mt-0.5">›</span>
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
              <section key={sectionKey} className={`mb-4 ${highlight("education")}`}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-1 bg-lime-500 rounded"></div>
                  <h2
                    className="font-bold uppercase tracking-wider text-gray-800"
                    style={{ fontSize: "var(--font-header)" }}
                  >
                    Education
                  </h2>
                </div>
                <div className="pl-10 space-y-2">
                  {content.education.map((edu) => (
                    <div key={edu.id} className="relative">
                      <div className="absolute -left-6 top-1 w-2 h-2 bg-lime-400 rounded-full"></div>
                      <div className="flex justify-between items-baseline">
                        <div>
                          <span className="font-bold text-gray-900">{edu.degree}</span>
                          {edu.fieldOfStudy && (
                            <span className="text-gray-600"> in {edu.fieldOfStudy}</span>
                          )}
                        </div>
                        <span
                          className="text-gray-500"
                          style={{ fontSize: "var(--font-small)" }}
                        >
                          {edu.graduationDate}
                        </span>
                      </div>
                      <div
                        className="text-lime-600"
                        style={{ fontSize: "var(--font-body)" }}
                      >
                        {edu.institution}
                      </div>
                      {edu.gpa && (
                        <div
                          className="text-gray-500"
                          style={{ fontSize: "var(--font-small)" }}
                        >
                          GPA: {edu.gpa}
                        </div>
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
              <section key={sectionKey} className={`mb-4 ${highlight("skills")}`}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-1 bg-lime-500 rounded"></div>
                  <h2
                    className="font-bold uppercase tracking-wider text-gray-800"
                    style={{ fontSize: "var(--font-header)" }}
                  >
                    Technical Skills
                  </h2>
                </div>
                <div className="pl-10 space-y-1">
                  {content.skills.technical.map((group) => (
                    <div key={group.id}>
                      <span
                        className="uppercase text-lime-600 font-medium"
                        style={{ fontSize: "var(--font-small)" }}
                      >
                        {group.header}:{" "}
                      </span>
                      <span
                        className="text-gray-700"
                        style={{ fontSize: "var(--font-body)" }}
                      >
                        {group.items.join(" • ")}
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            );
          }

          // Soft Skills
          if (sectionKey === "softSkills" && (content.skills.soft?.length ?? 0) > 0) {
            return (
              <section key={sectionKey} className={`mb-4 ${highlight("softSkills")}`}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-1 bg-lime-500 rounded"></div>
                  <h2
                    className="font-bold uppercase tracking-wider text-gray-800"
                    style={{ fontSize: "var(--font-header)" }}
                  >
                    Soft Skills
                  </h2>
                </div>
                <div className="pl-10">
                  <span
                    className="text-gray-700"
                    style={{ fontSize: "var(--font-body)" }}
                  >
                    {content.skills.soft.join(" • ")}
                  </span>
                </div>
              </section>
            );
          }

          // Custom Skills
          if (sectionKey === "customSkills" && (content.skills.custom?.length ?? 0) > 0) {
            return (
              <section key={sectionKey} className={`mb-4 ${highlight("customSkills")}`}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-1 bg-lime-500 rounded"></div>
                  <h2
                    className="font-bold uppercase tracking-wider text-gray-800"
                    style={{ fontSize: "var(--font-header)" }}
                  >
                    {content.skills.customSkillsHeader || "Custom Skills"}
                  </h2>
                </div>
                <div className="pl-10 space-y-1">
                  {content.skills.custom.map((group) => (
                    <div key={group.id}>
                      <span
                        className="uppercase text-lime-600 font-medium"
                        style={{ fontSize: "var(--font-small)" }}
                      >
                        {group.header}:{" "}
                      </span>
                      <span
                        className="text-gray-700"
                        style={{ fontSize: "var(--font-body)" }}
                      >
                        {group.items.join(" • ")}
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            );
          }

          // Projects
          if (sectionKey === "projects" && content.projects.length > 0) {
            return (
              <section key={sectionKey} className={`mb-4 ${highlight("projects")}`}>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-1 bg-lime-500 rounded"></div>
                  <h2
                    className="font-bold uppercase tracking-wider text-gray-800"
                    style={{ fontSize: "var(--font-header)" }}
                  >
                    Projects
                  </h2>
                </div>
                <div className="pl-10 space-y-2">
                  {content.projects.map((proj) => (
                    <div key={proj.id} className="relative">
                      <div className="absolute -left-6 top-1 w-2 h-2 bg-lime-400 rounded-full"></div>
                      <div className="font-bold text-gray-900">
                        {proj.name}
                        {proj.url && (
                          <a
                            href={proj.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-lime-600 ml-2 hover:underline"
                            style={{ fontSize: "var(--font-small)" }}
                          >
                            [View]
                          </a>
                        )}
                      </div>
                      <div
                        className="text-gray-600"
                        style={{ fontSize: "var(--font-body)" }}
                        dangerouslySetInnerHTML={{ __html: proj.description || "" }}
                      />
                      {proj.technologies.length > 0 && (
                        <p
                          className="text-lime-500 mt-0.5"
                          style={{ fontSize: "var(--font-xs)" }}
                        >
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
              <section key={sectionKey} className={`mb-4 ${highlight("certifications")}`}>
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-8 h-1 bg-lime-500 rounded"></div>
                  <h2
                    className="font-bold uppercase tracking-wider text-gray-800"
                    style={{ fontSize: "var(--font-header)" }}
                  >
                    Certifications
                  </h2>
                </div>
                <div className="pl-10">
                  {content.certifications.map((cert) => (
                    <div
                      key={cert.id}
                      className="mb-1"
                      style={{ fontSize: "var(--font-body)" }}
                    >
                      <span className="font-medium">{cert.name}</span>
                      {cert.issuer && <span className="text-gray-500"> - {cert.issuer}</span>}
                      {cert.url && (
                        <a
                          href={cert.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-gray-600 ml-1 hover:underline"
                          style={{ fontSize: "var(--font-xs)" }}
                        >
                          [Link]
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </section>
            );
          }

          // Awards
          if (sectionKey === "awards" && content.awards.length > 0) {
            return (
              <section key={sectionKey} className={`mb-4 ${highlight("awards")}`}>
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-8 h-1 bg-lime-500 rounded"></div>
                  <h2
                    className="font-bold uppercase tracking-wider text-gray-800"
                    style={{ fontSize: "var(--font-header)" }}
                  >
                    Awards
                  </h2>
                </div>
                <div className="pl-10">
                  {content.awards.map((award) => (
                    <div
                      key={award.id}
                      className="mb-1"
                      style={{ fontSize: "var(--font-body)" }}
                    >
                      <span className="font-medium">{award.title}</span>
                      {award.date && <span className="text-lime-500"> ({award.date})</span>}
                    </div>
                  ))}
                </div>
              </section>
            );
          }

          // Languages
          if (sectionKey === "languages" && content.languages.length > 0) {
            return (
              <section key={sectionKey} className={`mb-4 ${highlight("languages")}`}>
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-8 h-1 bg-lime-500 rounded"></div>
                  <h2
                    className="font-bold uppercase tracking-wider text-gray-800"
                    style={{ fontSize: "var(--font-header)" }}
                  >
                    Languages
                  </h2>
                </div>
                <div
                  className="pl-10 flex flex-wrap gap-2"
                  style={{ fontSize: "var(--font-body)" }}
                >
                  {content.languages.map((lang) => (
                    <span key={lang.id}>
                      <span className="font-medium">{lang.language}</span>
                      <span className="text-lime-500"> ({lang.proficiency})</span>
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
                  <section key={section.id} className={`mt-4 ${highlight("custom")}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-8 h-1 bg-lime-500 rounded"></div>
                      <h2
                        className="font-bold uppercase tracking-wider text-gray-800"
                        style={{ fontSize: "var(--font-header)" }}
                      >
                        {section.title}
                      </h2>
                    </div>
                    <ul
                      className="pl-10 text-gray-600 space-y-0.5"
                      style={{ fontSize: "var(--font-body)" }}
                    >
                      {section.items.map((item, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-lime-400 mt-0.5">›</span>
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
  );
}
