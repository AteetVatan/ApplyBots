/**
 * Glalie resume template.
 *
 * Two-column layout with dark green sidebar.
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

export function Glalie({
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
        className="w-[30%] text-white p-4"
        style={{ background: getPrimaryGradient(themeSettings) }}
      >
        {/* Profile */}
        <div className={`mb-5 ${highlight("contact")}`}>
          {content.profilePictureUrl && (
            <div className="mb-3 flex justify-center">
              <img
                src={content.profilePictureUrl}
                alt="Profile"
                className="w-24 h-24 rounded-full border-3 border-emerald-400 object-cover"
              />
            </div>
          )}
          <h1 className="text-lg font-bold leading-tight mb-1 text-center text-emerald-50">
            {content.fullName || "Your Name"}
          </h1>
          {content.workExperience[0]?.title && (
            <p className="text-emerald-300 text-center mb-3" style={{ fontSize: "var(--font-small)" }}>
              {content.workExperience[0].title}
            </p>
          )}
          <div className="text-emerald-100 space-y-1.5" style={{ fontSize: "var(--font-small)" }}>
            {content.email && <div className="truncate">{content.email}</div>}
            {content.phone && <div>{content.phone}</div>}
            {content.location && <div>{content.location}</div>}
            <div className="flex flex-wrap gap-x-2 gap-y-1 mt-2">
              {content.linkedinUrl && (
                <a href={content.linkedinUrl} target="_blank" rel="noopener noreferrer" className="text-emerald-300 hover:text-white" style={{ fontSize: "var(--font-xs)" }}>
                  LinkedIn
                </a>
              )}
              {content.portfolioUrl && (
                <a href={content.portfolioUrl} target="_blank" rel="noopener noreferrer" className="text-emerald-300 hover:text-white" style={{ fontSize: "var(--font-xs)" }}>
                  Portfolio
                </a>
              )}
              {content.githubUrl && (
                <a href={content.githubUrl} target="_blank" rel="noopener noreferrer" className="text-emerald-300 hover:text-white" style={{ fontSize: "var(--font-xs)" }}>
                  GitHub
                </a>
              )}
              {content.customLinks?.map((link) => (
                link.url && (
                  <a key={link.id} href={link.url} target="_blank" rel="noopener noreferrer" className="text-emerald-300 hover:text-white" style={{ fontSize: "var(--font-xs)" }}>
                    {link.label || "Link"}
                  </a>
                )
              ))}
            </div>
          </div>
        </div>

        {/* Skills - Compact */}
        {/* Technical Skills */}
        {(content.skills.technical?.length ?? 0) > 0 && (
          <div className={`mb-5 ${highlight("skills")}`}>
            <h2 className="font-bold uppercase tracking-wider text-emerald-300 mb-2 pb-1 border-b border-emerald-600" style={{ fontSize: "var(--font-body)" }}>
              Technical Skills
            </h2>
            <div className="space-y-1">
              {content.skills.technical.map((group) => (
                <div key={group.id}>
                  <h3 className="uppercase text-emerald-400 mb-1" style={{ fontSize: "var(--font-xs)" }}>{group.header}</h3>
                  <p className="text-emerald-100" style={{ fontSize: "var(--font-small)" }}>
                    {group.items.join(" · ")}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Soft Skills */}
        {(content.skills.soft?.length ?? 0) > 0 && (
          <div className={`mb-5 ${highlight("softSkills")}`}>
            <h2 className="font-bold uppercase tracking-wider text-emerald-300 mb-2 pb-1 border-b border-emerald-600" style={{ fontSize: "var(--font-body)" }}>
              Soft Skills
            </h2>
            <p className="text-emerald-100" style={{ fontSize: "var(--font-small)" }}>
              {content.skills.soft.join(" · ")}
            </p>
          </div>
        )}

        {/* Custom Skills */}
        {(content.skills.custom?.length ?? 0) > 0 && (
          <div className={`mb-5 ${highlight("customSkills")}`}>
            <h2 className="font-bold uppercase tracking-wider text-emerald-300 mb-2 pb-1 border-b border-emerald-600" style={{ fontSize: "var(--font-body)" }}>
              {content.skills.customSkillsHeader || "Custom Skills"}
            </h2>
            <div className="space-y-1">
              {content.skills.custom.map((group) => (
                <div key={group.id}>
                  <h3 className="uppercase text-emerald-400 mb-1" style={{ fontSize: "var(--font-xs)" }}>{group.header}</h3>
                  <p className="text-emerald-100" style={{ fontSize: "var(--font-small)" }}>
                    {group.items.join(" · ")}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Education - Compact in Sidebar */}
        {content.education.length > 0 && (
          <div className={`mb-5 ${highlight("education")}`}>
            <h2 className="font-bold uppercase tracking-wider text-emerald-300 mb-2 pb-1 border-b border-emerald-600" style={{ fontSize: "var(--font-body)" }}>
              Education
            </h2>
            {content.education.map((edu) => (
              <div key={edu.id} className="mb-2.5" style={{ fontSize: "var(--font-small)" }}>
                <div className="font-bold text-white">{edu.degree}</div>
                {edu.fieldOfStudy && <div className="text-emerald-200">{edu.fieldOfStudy}</div>}
                <div className="text-emerald-300">{edu.institution}</div>
                <div className="text-emerald-400" style={{ fontSize: "var(--font-xs)" }}>{edu.graduationDate}</div>
              </div>
            ))}
          </div>
        )}

        {/* Languages */}
        {content.languages.length > 0 && (
          <div className={`mb-5 ${highlight("languages")}`}>
            <h2 className="font-bold uppercase tracking-wider text-emerald-300 mb-2 pb-1 border-b border-emerald-600" style={{ fontSize: "var(--font-body)" }}>
              Languages
            </h2>
            <div className="space-y-1">
              {content.languages.map((lang) => (
                <div key={lang.id} className="flex justify-between" style={{ fontSize: "var(--font-small)" }}>
                  <span className="text-white">{lang.language}</span>
                  <span className="text-emerald-300" style={{ fontSize: "var(--font-xs)" }}>
                    {lang.proficiency}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Certifications */}
        {content.certifications.length > 0 && (
          <div className={`${highlight("certifications")}`}>
            <h2 className="font-bold uppercase tracking-wider text-emerald-300 mb-2 pb-1 border-b border-emerald-600" style={{ fontSize: "var(--font-body)" }}>
              Certifications
            </h2>
            {content.certifications.map((cert) => (
              <div key={cert.id} className="mb-2" style={{ fontSize: "var(--font-small)" }}>
                <div className="font-medium text-white">
                  {cert.name}
                  {cert.url && (
                    <a href={cert.url} target="_blank" rel="noopener noreferrer" className="text-emerald-200 ml-1 hover:underline" style={{ fontSize: "var(--font-xs)" }}>
                      [Link]
                    </a>
                  )}
                </div>
                {cert.issuer && <div className="text-emerald-300" style={{ fontSize: "var(--font-xs)" }}>{cert.issuer}</div>}
              </div>
            ))}
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="w-[70%] p-5">
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
                  <h2 className="font-bold uppercase tracking-wider text-emerald-800 mb-2 pb-1 border-b-2 border-emerald-600" style={{ fontSize: "var(--font-header)" }}>
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
                  <h2 className="font-bold uppercase tracking-wider text-emerald-800 mb-2 pb-1 border-b-2 border-emerald-600" style={{ fontSize: "var(--font-header)" }}>
                    Work Experience
                  </h2>
                  {content.workExperience.map((exp) => (
                    <div key={exp.id} className="mb-3">
                      <div className="flex justify-between items-baseline">
                        <div>
                          <span className="font-bold text-gray-900" style={{ fontSize: "var(--font-body)" }}>{exp.title}</span>
                          <span className="text-emerald-700" style={{ fontSize: "var(--font-body)" }}> — {exp.company}</span>
                        </div>
                        <span className="text-gray-500 whitespace-nowrap" style={{ fontSize: "var(--font-small)" }}>
                          {exp.startDate} - {exp.endDate || (exp.isCurrent ? "Present" : "")}
                        </span>
                      </div>
                      {exp.location && (
                        <div className="text-gray-500" style={{ fontSize: "var(--font-small)" }}>{exp.location}</div>
                      )}
                      {exp.achievements.length > 0 && (
                        <ul className="mt-1 pl-3 text-gray-600 list-disc" style={{ fontSize: "var(--font-body)" }}>
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
                  <h2 className="font-bold uppercase tracking-wider text-emerald-800 mb-2 pb-1 border-b-2 border-emerald-600" style={{ fontSize: "var(--font-header)" }}>
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
                  <h2 className="font-bold uppercase tracking-wider text-emerald-800 mb-2 pb-1 border-b-2 border-emerald-600" style={{ fontSize: "var(--font-header)" }}>
                    Technical Skills
                  </h2>
                  {content.skills.technical.map((group) => (
                    <div key={group.id} className="mb-2">
                      <h3 className="uppercase text-emerald-600 mb-1" style={{ fontSize: "var(--font-small)" }}>{group.header}</h3>
                      <div className="flex flex-wrap gap-1">
                        {group.items.map((skill, i) => (
                          <span
                            key={i}
                            className="bg-emerald-100 text-emerald-700 px-2 py-1 rounded"
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
                  <h2 className="font-bold uppercase tracking-wider text-emerald-800 mb-2 pb-1 border-b-2 border-emerald-600" style={{ fontSize: "var(--font-header)" }}>
                    Soft Skills
                  </h2>
                  <div className="flex flex-wrap gap-1">
                    {content.skills.soft.map((skill, i) => (
                      <span
                        key={i}
                        className="bg-emerald-100 text-emerald-700 px-2 py-1 rounded"
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
                  <h2 className="font-bold uppercase tracking-wider text-emerald-800 mb-2 pb-1 border-b-2 border-emerald-600" style={{ fontSize: "var(--font-header)" }}>
                    {content.skills.customSkillsHeader || "Custom Skills"}
                  </h2>
                  {content.skills.custom.map((group) => (
                    <div key={group.id} className="mb-2">
                      <h3 className="uppercase text-emerald-600 mb-1" style={{ fontSize: "var(--font-small)" }}>{group.header}</h3>
                      <div className="flex flex-wrap gap-1">
                        {group.items.map((skill, i) => (
                          <span
                            key={i}
                            className="bg-emerald-100 text-emerald-700 px-2 py-1 rounded"
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
                  <h2 className="font-bold uppercase tracking-wider text-emerald-800 mb-2 pb-1 border-b-2 border-emerald-600" style={{ fontSize: "var(--font-header)" }}>
                    Projects
                  </h2>
                  {content.projects.map((proj) => (
                    <div key={proj.id} className="mb-2.5">
                      <div className="flex items-baseline gap-2">
                        <span className="font-bold text-gray-900" style={{ fontSize: "var(--font-body)" }}>{proj.name}</span>
                        {proj.url && (
                          <a href={proj.url} target="_blank" rel="noopener noreferrer" className="text-emerald-600 hover:underline" style={{ fontSize: "var(--font-xs)" }}>
                            [link]
                          </a>
                        )}
                      </div>
                      <div
                        className="text-gray-600"
                        style={{ fontSize: "var(--font-body)" }}
                        dangerouslySetInnerHTML={{ __html: proj.description || "" }}
                      />
                      {proj.technologies.length > 0 && (
                        <p className="text-emerald-600 mt-0.5" style={{ fontSize: "var(--font-xs)" }}>
                          Tech: {proj.technologies.join(", ")}
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
                  <h2 className="font-bold uppercase tracking-wider text-emerald-800 mb-2 pb-1 border-b-2 border-emerald-600" style={{ fontSize: "var(--font-header)" }}>
                    Certifications
                  </h2>
                  {content.certifications.map((cert) => (
                    <div key={cert.id} className="mb-2" style={{ fontSize: "var(--font-body)" }}>
                      <div className="font-medium">
                        {cert.name}
                        {cert.url && (
                          <a href={cert.url} target="_blank" rel="noopener noreferrer" className="text-emerald-600 ml-1 hover:underline" style={{ fontSize: "var(--font-xs)" }}>
                            [Link]
                          </a>
                        )}
                      </div>
                      {cert.issuer && <div className="text-gray-600">{cert.issuer}</div>}
                      {cert.date && <div className="text-gray-500" style={{ fontSize: "var(--font-xs)" }}>{cert.date}</div>}
                    </div>
                  ))}
                </section>
              );
            }

            // Awards
            if (sectionKey === "awards" && content.awards.length > 0) {
              return (
                <section key={sectionKey} className={`mb-4 ${highlight("awards")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-emerald-800 mb-2 pb-1 border-b-2 border-emerald-600" style={{ fontSize: "var(--font-header)" }}>
                    Awards
                  </h2>
                  {content.awards.map((award) => (
                    <div key={award.id} className="mb-1.5" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-bold text-gray-900">{award.title}</span>
                      {award.issuer && <span className="text-gray-600"> — {award.issuer}</span>}
                      {award.date && <span className="text-emerald-600"> ({award.date})</span>}
                    </div>
                  ))}
                </section>
              );
            }

            // Languages
            if (sectionKey === "languages" && content.languages.length > 0) {
              return (
                <section key={sectionKey} className={`mb-4 ${highlight("languages")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-emerald-800 mb-2 pb-1 border-b-2 border-emerald-600" style={{ fontSize: "var(--font-header)" }}>
                    Languages
                  </h2>
                  {content.languages.map((lang) => (
                    <div key={lang.id} className="flex justify-between mb-1.5" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-medium">{lang.language}</span>
                      <span className="text-emerald-600">
                        {lang.proficiency.charAt(0).toUpperCase() + lang.proficiency.slice(1)}
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
                      <h2 className="font-bold uppercase tracking-wider text-emerald-800 mb-2 pb-1 border-b-2 border-emerald-600" style={{ fontSize: "var(--font-header)" }}>
                        {section.title}
                      </h2>
                      <ul className="pl-3 text-gray-600 list-disc" style={{ fontSize: "var(--font-body)" }}>
                        {section.items.map((item, i) => (
                          <li key={i} className="mb-0.5">{item}</li>
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
