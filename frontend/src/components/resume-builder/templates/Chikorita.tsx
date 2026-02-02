/**
 * Chikorita resume template.
 *
 * Two-column layout with green sidebar for profile, skills, and certifications.
 * ATS Score: 88
 */

import React from "react";
import type { ResumeTemplateProps } from "./types";
import type { ThemeSettings } from "@/stores/resume-builder-store";
import { getFontFamily, getPrimaryGradient, getThemeCSSVariables } from "./theme-utils";

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

export function Chikorita({
  content,
  scale = 1,
  highlightSection,
  themeSettings = DEFAULT_THEME,
}: ResumeTemplateProps) {
  const highlight = (section: string) =>
    highlightSection === section ? "bg-emerald-50 ring-2 ring-emerald-200 ring-inset" : "";

  const cssVars = getThemeCSSVariables(themeSettings);

  return (
    <div
      className="bg-white text-gray-900 shadow-lg flex"
      style={{
        ...cssVars,
        width: "8.5in",
        minHeight: "11in",
        transform: `scale(${scale})`,
        transformOrigin: "top left",
        fontFamily: getFontFamily(themeSettings),
        fontSize: "var(--font-base)",
        lineHeight: 1.4,
      } as React.CSSProperties}
    >
      {/* Left Sidebar - Primary Color */}
      <aside
        className="w-1/3 text-white p-5"
        style={{ background: getPrimaryGradient(themeSettings) }}
      >
        {/* Profile */}
        <div className={`mb-6 ${highlight("contact")}`}>
          {content.profilePictureUrl && (
            <div className="mb-4 flex justify-center">
              <img
                src={content.profilePictureUrl}
                alt="Profile"
                className="w-32 h-32 rounded-full border-2 border-white object-cover"
              />
            </div>
          )}
          <h1 className="text-lg font-bold leading-tight mb-3 text-center">
            {content.fullName || "John Doe"}
          </h1>
          <div className="text-green-50 space-y-1.5" style={{ fontSize: "var(--font-small)" }}>
            {content.email && <div>{content.email}</div>}
            {content.phone && <div>{content.phone}</div>}
            {content.location && <div>{content.location}</div>}
            {content.linkedinUrl && (
              <div>
                <a href={content.linkedinUrl} target="_blank" rel="noopener noreferrer" className="text-white hover:underline">
                  LinkedIn
                </a>
              </div>
            )}
            {content.portfolioUrl && (
              <div>
                <a href={content.portfolioUrl} target="_blank" rel="noopener noreferrer" className="text-white hover:underline">
                  Website
                </a>
              </div>
            )}
            {content.githubUrl && (
              <div>
                <a href={content.githubUrl} target="_blank" rel="noopener noreferrer" className="text-white hover:underline">
                  GitHub
                </a>
              </div>
            )}
            {content.customLinks && content.customLinks.map((link) => (
              link.url && (
                <div key={link.id}>
                  <a href={link.url} target="_blank" rel="noopener noreferrer" className="text-white hover:underline">
                    {link.label || "Link"}
                  </a>
                </div>
              )
            ))}
          </div>
        </div>

      </aside>

      {/* Main Content */}
      <main className="w-2/3 p-5">
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
                  <h2 className="font-bold uppercase tracking-wider text-gray-700 mb-2 pb-1 border-b border-gray-200" style={{ fontSize: "var(--font-header)" }}>
                    Professional Summary
                  </h2>
                  <div
                    className="text-gray-600 leading-relaxed"
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
                  <h2 className="font-bold uppercase tracking-wider text-gray-700 mb-2 pb-1 border-b border-gray-200" style={{ fontSize: "var(--font-header)" }}>
                    Experience
                  </h2>
                  {content.workExperience.map((exp) => (
                    <div key={exp.id} className="mb-3">
                      <div className="flex justify-between items-baseline mb-1">
                        <div>
                          <span className="font-semibold text-gray-900">{exp.title}</span>
                          <span className="text-green-600 ml-1">@ {exp.company}</span>
                        </div>
                        <span className="text-gray-500" style={{ fontSize: "var(--font-small)" }}>
                          {exp.startDate} - {exp.endDate || (exp.isCurrent ? "Present" : "")}
                        </span>
                      </div>
                      {exp.achievements.length > 0 && (
                        <ul className="mt-1 pl-4 text-gray-600 list-disc" style={{ fontSize: "var(--font-body)" }}>
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
                <section key={sectionKey} className={`mb-4 ${highlight("education")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-gray-700 mb-2 pb-1 border-b border-gray-200" style={{ fontSize: "var(--font-header)" }}>
                    Education
                  </h2>
                  {content.education.map((edu) => (
                    <div key={edu.id} className="mb-2.5">
                      <div className="flex justify-between items-baseline mb-0.5">
                        <div>
                          <span className="font-semibold text-gray-900">{edu.degree}</span>
                          {edu.fieldOfStudy && (
                            <span className="text-gray-600"> in {edu.fieldOfStudy}</span>
                          )}
                        </div>
                        <span className="text-gray-500" style={{ fontSize: "var(--font-small)" }}>{edu.graduationDate}</span>
                      </div>
                      <div className="text-gray-600" style={{ fontSize: "var(--font-body)" }}>{edu.institution}</div>
                      {edu.gpa && (
                        <div className="text-gray-500" style={{ fontSize: "var(--font-small)" }}>GPA: {edu.gpa}</div>
                      )}
                    </div>
                  ))}
                </section>
              );
            }

            // Technical Skills
            if (sectionKey === "skills" && (content.skills.technical?.length ?? 0) > 0) {
              return (
                <section key={sectionKey} className={`mb-4 ${highlight("skills")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-gray-700 mb-2 pb-1 border-b border-gray-200" style={{ fontSize: "var(--font-header)" }}>
                    Technical Skills
                  </h2>
                  {content.skills.technical.map((group) => (
                    <div key={group.id} className="mb-2">
                      <h3 className="uppercase text-green-600 mb-1" style={{ fontSize: "var(--font-small)" }}>{group.header}</h3>
                      <div className="flex flex-wrap gap-1">
                        {group.items.map((skill, i) => (
                          <span
                            key={i}
                            className="bg-green-100 text-green-700 px-2 py-1 rounded"
                            style={{ fontSize: "var(--font-xs)" }}
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </section>
              );
            }

            // Soft Skills
            if (sectionKey === "softSkills" && (content.skills.soft?.length ?? 0) > 0) {
              return (
                <section key={sectionKey} className={`mb-4 ${highlight("softSkills")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-gray-700 mb-2 pb-1 border-b border-gray-200" style={{ fontSize: "var(--font-header)" }}>
                    Soft Skills
                  </h2>
                  <div className="flex flex-wrap gap-1">
                    {content.skills.soft.map((skill, i) => (
                      <span
                        key={i}
                        className="bg-green-100 text-green-700 px-2 py-1 rounded"
                        style={{ fontSize: "var(--font-xs)" }}
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </section>
              );
            }

            // Custom Skills
            if (sectionKey === "customSkills" && (content.skills.custom?.length ?? 0) > 0) {
              return (
                <section key={sectionKey} className={`mb-4 ${highlight("customSkills")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-gray-700 mb-2 pb-1 border-b border-gray-200" style={{ fontSize: "var(--font-header)" }}>
                    {content.skills.customSkillsHeader || "Custom Skills"}
                  </h2>
                  {content.skills.custom.map((group) => (
                    <div key={group.id} className="mb-2">
                      <h3 className="uppercase text-green-600 mb-1" style={{ fontSize: "var(--font-small)" }}>{group.header}</h3>
                      <div className="flex flex-wrap gap-1">
                        {group.items.map((skill, i) => (
                          <span
                            key={i}
                            className="bg-green-100 text-green-700 px-2 py-1 rounded"
                            style={{ fontSize: "var(--font-xs)" }}
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </section>
              );
            }

            // Projects
            if (sectionKey === "projects" && content.projects.length > 0) {
              return (
                <section key={sectionKey} className={`mb-4 ${highlight("projects")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-gray-700 mb-2 pb-1 border-b border-gray-200" style={{ fontSize: "var(--font-header)" }}>
                    Projects
                  </h2>
                  {content.projects.map((proj) => (
                    <div key={proj.id} className="mb-2.5">
                      <div className="font-semibold text-gray-900">
                        {proj.name}
                        {proj.url && (
                          <a href={proj.url} target="_blank" rel="noopener noreferrer" className="text-green-600 ml-1 hover:underline" style={{ fontSize: "var(--font-small)" }}>
                            [Link]
                          </a>
                        )}
                      </div>
                      <div
                        className="text-gray-600"
                        style={{ fontSize: "var(--font-body)" }}
                        dangerouslySetInnerHTML={{ __html: proj.description || "" }}
                      />
                      {proj.technologies.length > 0 && (
                        <p className="text-green-600 mt-0.5" style={{ fontSize: "var(--font-xs)" }}>
                          {proj.technologies.join(" • ")}
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
                <section key={sectionKey} className={`mb-4 ${highlight("certifications")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-gray-700 mb-2 pb-1 border-b border-gray-200" style={{ fontSize: "var(--font-header)" }}>
                    Certifications
                  </h2>
                  {content.certifications.map((cert) => (
                    <div key={cert.id} className="mb-2" style={{ fontSize: "var(--font-body)" }}>
                      <div className="font-medium">
                        {cert.name}
                        {cert.url && (
                          <a href={cert.url} target="_blank" rel="noopener noreferrer" className="text-green-600 ml-1 hover:underline" style={{ fontSize: "var(--font-xs)" }}>
                            [Link]
                          </a>
                        )}
                      </div>
                      {cert.issuer && <div className="text-gray-600">{cert.issuer}</div>}
                      {cert.date && <div className="text-gray-500">{cert.date}</div>}
                    </div>
                  ))}
                </section>
              );
            }

            // Awards
            if (sectionKey === "awards" && content.awards.length > 0) {
              return (
                <section key={sectionKey} className={`mb-4 ${highlight("awards")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-gray-700 mb-2 pb-1 border-b border-gray-200" style={{ fontSize: "var(--font-header)" }}>
                    Awards & Achievements
                  </h2>
                  {content.awards.map((award) => (
                    <div key={award.id} className="mb-1.5" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-semibold text-gray-900">{award.title}</span>
                      {award.issuer && ` - ${award.issuer}`}
                      {award.date && ` (${award.date})`}
                      {award.description && (
                        <p className="text-gray-600 mt-0.5" style={{ fontSize: "var(--font-xs)" }}>{award.description}</p>
                      )}
                    </div>
                  ))}
                </section>
              );
            }

            // Languages
            if (sectionKey === "languages" && content.languages.length > 0) {
              return (
                <section key={sectionKey} className={`mb-4 ${highlight("languages")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-gray-700 mb-2 pb-1 border-b border-gray-200" style={{ fontSize: "var(--font-header)" }}>
                    Languages
                  </h2>
                  {content.languages.map((lang) => (
                    <div key={lang.id} className="mb-1.5" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-medium">{lang.language}</span>
                      <span className="text-gray-600 ml-1">
                        ({lang.proficiency.charAt(0).toUpperCase() + lang.proficiency.slice(1)})
                      </span>
                    </div>
                  ))}
                </section>
              );
            }

            // Custom Sections
            if (sectionKey === "custom" && content.customSections.length > 0) {
              return (
                <React.Fragment key={sectionKey}>
                  {content.customSections.map((section) => (
                    <section key={section.id} className={`mb-4 ${highlight("custom")}`}>
                      <h2 className="font-bold uppercase tracking-wider text-gray-700 mb-2 pb-1 border-b border-gray-200" style={{ fontSize: "var(--font-header)" }}>
                        {section.title}
                      </h2>
                      <ul className="pl-4 text-gray-600 list-disc" style={{ fontSize: "var(--font-body)" }}>
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
      </main>
    </div>
  );
}
