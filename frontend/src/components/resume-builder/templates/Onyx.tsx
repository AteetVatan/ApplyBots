/**
 * Onyx resume template.
 *
 * Single-column design with thin border and blue accent line.
 * ATS Score: 95
 */

import React from "react";
import type { ResumeTemplateProps } from "./types";
import type { ThemeSettings } from "@/stores/resume-builder-store";
import { getFontFamily, getSpacingMultiplier, getPrimaryColor, getThemeCSSVariables } from "./theme-utils";

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

export function Onyx({
  content,
  scale = 1,
  highlightSection,
  themeSettings = DEFAULT_THEME,
}: ResumeTemplateProps) {
  const highlight = (section: string) =>
    highlightSection === section ? "bg-blue-50 ring-2 ring-blue-200 ring-inset" : "";
  
  const spacingMultiplier = getSpacingMultiplier(themeSettings);
  const basePadding = 0.5;
  const padding = `${basePadding * spacingMultiplier}in`;
  const cssVars = getThemeCSSVariables(themeSettings);
  const primaryColor = getPrimaryColor(themeSettings);

  return (
    <div
      className="bg-white text-gray-900 shadow-lg border border-gray-300 relative"
      style={{
        ...cssVars,
        width: "8.5in",
        minHeight: "11in",
        padding,
        transform: `scale(${scale})`,
        transformOrigin: "top left",
        fontFamily: getFontFamily(themeSettings),
        fontSize: "var(--font-base)",
        lineHeight: 1.4,
      } as React.CSSProperties}
    >
      {/* Accent Line */}
      <div
        className="absolute top-0 left-0 w-1 h-full"
        style={{ backgroundColor: primaryColor }}
      ></div>

      {/* Header */}
      <header className={`mb-4 pb-3 ml-3 ${highlight("contact")}`}>
        <div className="flex items-start gap-4">
          {content.profilePictureUrl && (
            <img
              src={content.profilePictureUrl}
              alt="Profile"
              className="w-20 h-20 rounded-full object-cover flex-shrink-0"
            />
          )}
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-gray-900 mb-1">
              {content.fullName || "Your Name"}
            </h1>
            {content.workExperience[0]?.title && (
              <p className="font-medium text-gray-600 mb-2" style={{ fontSize: "var(--font-body)" }}>
                {content.workExperience[0].title}
              </p>
            )}
            <div className="text-gray-600 space-y-0.5" style={{ fontSize: "var(--font-body)" }}>
              {content.email && <div>{content.email}</div>}
              {content.phone && <div>{content.phone}</div>}
              {content.location && <div>{content.location}</div>}
              <div className="flex flex-wrap gap-3 mt-1">
                {content.linkedinUrl && (
                  <a href={content.linkedinUrl} target="_blank" rel="noopener noreferrer" className="hover:underline" style={{ color: primaryColor }}>
                    LinkedIn
                  </a>
                )}
                {content.portfolioUrl && (
                  <a href={content.portfolioUrl} target="_blank" rel="noopener noreferrer" className="hover:underline" style={{ color: primaryColor }}>
                    Website
                  </a>
                )}
                {content.githubUrl && (
                  <a href={content.githubUrl} target="_blank" rel="noopener noreferrer" className="hover:underline" style={{ color: primaryColor }}>
                    GitHub
                  </a>
                )}
                {content.customLinks && content.customLinks.map((link) => (
                  link.url && (
                    <a key={link.id} href={link.url} target="_blank" rel="noopener noreferrer" className="hover:underline" style={{ color: primaryColor }}>
                      {link.label || "Link"}
                    </a>
                  )
                ))}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Content with left margin for accent line */}
      <div className="ml-3">
        {/* Render sections based on sectionOrder */}
        {(content.sectionOrder && content.sectionOrder.length > 0 
          ? content.sectionOrder 
          : DEFAULT_SECTION_ORDER)
          .filter((key) => key !== "contact")
          .map((sectionKey) => {
            // Summary
            if (sectionKey === "summary" && content.professionalSummary) {
              return (
                <section key={sectionKey} className={`mb-3 ${highlight("summary")}`}>
                  <h2 className="font-bold uppercase tracking-wide mb-1 border-b border-gray-200 pb-1" style={{ fontSize: "var(--font-header)", color: primaryColor }}>
                    Professional Summary
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
                <section key={sectionKey} className={`mb-3 ${highlight("experience")}`}>
                  <h2 className="font-bold uppercase tracking-wide mb-2 border-b border-gray-200 pb-1" style={{ fontSize: "var(--font-header)", color: primaryColor }}>
                    Experience
                  </h2>
                  {content.workExperience.map((exp) => (
                    <div key={exp.id} className="mb-2.5">
                      <div className="flex justify-between items-baseline mb-0.5">
                        <div>
                          <span className="font-semibold text-gray-900">{exp.title}</span>
                          <span className="text-gray-700"> | {exp.company}</span>
                        </div>
                        <span className="text-gray-500" style={{ fontSize: "var(--font-small)" }}>
                          {exp.startDate}
                          {exp.endDate ? ` - ${exp.endDate}` : exp.isCurrent ? " - Present" : ""}
                        </span>
                      </div>
                      {exp.location && (
                        <div className="text-gray-500 italic" style={{ fontSize: "var(--font-small)" }}>
                          {exp.location}
                        </div>
                      )}
                      {exp.achievements.length > 0 && (
                        <ul className="mt-1 pl-4 text-gray-700 list-disc" style={{ fontSize: "var(--font-body)" }}>
                          {exp.achievements.map((ach, i) => (
                            <li
                              key={i}
                              className="mb-0.5"
                              dangerouslySetInnerHTML={{ __html: ach || "" }}
                            />
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </section>
              );
            }

            // Education
            if (sectionKey === "education" && content.education.length > 0) {
              return (
                <section key={sectionKey} className={`mb-3 ${highlight("education")}`}>
                  <h2 className="font-bold uppercase tracking-wide mb-2 border-b border-gray-200 pb-1" style={{ fontSize: "var(--font-header)", color: primaryColor }}>
                    Education
                  </h2>
                  {content.education.map((edu) => (
                    <div key={edu.id} className="mb-2">
                      <div className="flex justify-between items-baseline">
                        <div>
                          <span className="font-semibold text-gray-900">{edu.degree}</span>
                          {edu.fieldOfStudy && <span className="text-gray-700"> in {edu.fieldOfStudy}</span>}
                        </div>
                        <span className="text-gray-500" style={{ fontSize: "var(--font-small)" }}>
                          {edu.graduationDate}
                        </span>
                      </div>
                      <div className="text-gray-600" style={{ fontSize: "var(--font-body)" }}>
                        {edu.institution}
                        {edu.gpa && <span className="text-gray-500 ml-2">GPA: {edu.gpa}</span>}
                      </div>
                    </div>
                  ))}
                </section>
              );
            }

            // Technical Skills
            if (sectionKey === "skills" && (content.skills.technical?.length ?? 0) > 0) {
              return (
                <section key={sectionKey} className={`mb-3 ${highlight("skills")}`}>
                  <h2 className="font-bold uppercase tracking-wide mb-2 border-b border-gray-200 pb-1" style={{ fontSize: "var(--font-header)", color: primaryColor }}>
                    Technical Skills
                  </h2>
                  <div className="space-y-1" style={{ fontSize: "var(--font-body)" }}>
                    {content.skills.technical.map((group) => (
                      <p key={group.id}>
                        <span className="font-semibold text-gray-900">{group.header}: </span>
                        <span className="text-gray-700">{group.items.join(", ")}</span>
                      </p>
                    ))}
                  </div>
                </section>
              );
            }

            // Soft Skills
            if (sectionKey === "softSkills" && (content.skills.soft?.length ?? 0) > 0) {
              return (
                <section key={sectionKey} className={`mb-3 ${highlight("softSkills")}`}>
                  <h2 className="font-bold uppercase tracking-wide mb-2 border-b border-gray-200 pb-1" style={{ fontSize: "var(--font-header)", color: primaryColor }}>
                    Soft Skills
                  </h2>
                  <p className="text-gray-700" style={{ fontSize: "var(--font-body)" }}>
                    {content.skills.soft.join(", ")}
                  </p>
                </section>
              );
            }

            // Custom Skills
            if (sectionKey === "customSkills" && (content.skills.custom?.length ?? 0) > 0) {
              return (
                <section key={sectionKey} className={`mb-3 ${highlight("customSkills")}`}>
                  <h2 className="font-bold uppercase tracking-wide mb-2 border-b border-gray-200 pb-1" style={{ fontSize: "var(--font-header)", color: primaryColor }}>
                    {content.skills.customSkillsHeader || "Custom Skills"}
                  </h2>
                  <div className="space-y-1" style={{ fontSize: "var(--font-body)" }}>
                    {content.skills.custom.map((group) => (
                      <p key={group.id}>
                        <span className="font-semibold text-gray-900">{group.header}: </span>
                        <span className="text-gray-700">{group.items.join(", ")}</span>
                      </p>
                    ))}
                  </div>
                </section>
              );
            }

            // Projects
            if (sectionKey === "projects" && content.projects.length > 0) {
              return (
                <section key={sectionKey} className={`mb-3 ${highlight("projects")}`}>
                  <h2 className="font-bold uppercase tracking-wide mb-2 border-b border-gray-200 pb-1" style={{ fontSize: "var(--font-header)", color: primaryColor }}>
                    Projects
                  </h2>
                  {content.projects.map((proj) => (
                    <div key={proj.id} className="mb-2">
                      <div className="font-semibold text-gray-900">
                        {proj.name}
                        {proj.url && (
                          <a href={proj.url} target="_blank" rel="noopener noreferrer" className="ml-1 hover:underline" style={{ fontSize: "var(--font-small)", color: primaryColor }}>
                            [Link]
                          </a>
                        )}
                      </div>
                      <div
                        className="text-gray-700"
                        style={{ fontSize: "var(--font-body)" }}
                        dangerouslySetInnerHTML={{ __html: proj.description || "" }}
                      />
                      {proj.technologies.length > 0 && (
                        <p className="text-gray-500 italic" style={{ fontSize: "var(--font-small)" }}>
                          Technologies: {proj.technologies.join(", ")}
                        </p>
                      )}
                    </div>
                  ))}
                </section>
              );
            }

            // Certifications
            if (sectionKey === "certifications" && content.certifications.length > 0) {
              return (
                <section key={sectionKey} className={`mb-3 ${highlight("certifications")}`}>
                  <h2 className="font-bold uppercase tracking-wide mb-2 border-b border-gray-200 pb-1" style={{ fontSize: "var(--font-header)", color: primaryColor }}>
                    Certifications
                  </h2>
                  {content.certifications.map((cert) => (
                    <p key={cert.id} className="mb-1" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-semibold text-gray-900">{cert.name}</span>
                      {cert.issuer && ` - ${cert.issuer}`}
                      {cert.date && ` (${cert.date})`}
                      {cert.url && (
                        <a href={cert.url} target="_blank" rel="noopener noreferrer" className="ml-1 hover:underline" style={{ fontSize: "var(--font-xs)", color: primaryColor }}>
                          [Link]
                        </a>
                      )}
                    </p>
                  ))}
                </section>
              );
            }

            // Awards
            if (sectionKey === "awards" && content.awards.length > 0) {
              return (
                <section key={sectionKey} className={`mb-3 ${highlight("awards")}`}>
                  <h2 className="font-bold uppercase tracking-wide mb-2 border-b border-gray-200 pb-1" style={{ fontSize: "var(--font-header)", color: primaryColor }}>
                    Awards & Achievements
                  </h2>
                  {content.awards.map((award) => (
                    <div key={award.id} className="mb-1" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-semibold text-gray-900">{award.title}</span>
                      {award.issuer && ` - ${award.issuer}`}
                      {award.date && ` (${award.date})`}
                      {award.description && (
                        <p className="text-gray-500 mt-0.5" style={{ fontSize: "var(--font-small)" }}>{award.description}</p>
                      )}
                    </div>
                  ))}
                </section>
              );
            }

            // Languages
            if (sectionKey === "languages" && content.languages.length > 0) {
              return (
                <section key={sectionKey} className={`mb-3 ${highlight("languages")}`}>
                  <h2 className="font-bold uppercase tracking-wide mb-2 border-b border-gray-200 pb-1" style={{ fontSize: "var(--font-header)", color: primaryColor }}>
                    Languages
                  </h2>
                  <div className="flex flex-wrap gap-4" style={{ fontSize: "var(--font-body)" }}>
                    {content.languages.map((lang) => (
                      <span key={lang.id} className="text-gray-700">
                        {lang.language}{" "}
                        <span className="text-gray-500 italic">
                          ({lang.proficiency.charAt(0).toUpperCase() + lang.proficiency.slice(1)})
                        </span>
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
                    <section key={section.id} className={`mb-3 ${highlight("custom")}`}>
                      <h2 className="font-bold uppercase tracking-wide mb-2 border-b border-gray-200 pb-1" style={{ fontSize: "var(--font-header)", color: primaryColor }}>
                        {section.title}
                      </h2>
                      <ul className="pl-4 text-gray-700 list-disc" style={{ fontSize: "var(--font-body)" }}>
                        {section.items.map((item, i) => (
                          <li key={i} className="mb-0.5">
                            {item}
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
