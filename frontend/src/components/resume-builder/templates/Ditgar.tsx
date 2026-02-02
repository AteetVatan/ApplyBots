/**
 * Ditgar resume template.
 *
 * Two-column layout with blue sidebar - profile photo on left, experience on right.
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

export function Ditgar({
  content,
  scale = 1,
  highlightSection,
  themeSettings = DEFAULT_THEME,
}: ResumeTemplateProps) {
  const highlight = (section: string) =>
    highlightSection === section ? "bg-sky-50 ring-2 ring-sky-200 ring-inset" : "";

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
        lineHeight: 1.45,
      } as React.CSSProperties}
    >
      {/* Left Sidebar - Primary Color */}
      <aside
        className="w-[32%] text-white p-5"
        style={{ background: getPrimaryGradient(themeSettings) }}
      >
        {/* Profile */}
        <div className={`mb-6 ${highlight("contact")}`}>
          {content.profilePictureUrl && (
            <div className="mb-4 flex justify-center">
              <img
                src={content.profilePictureUrl}
                alt="Profile"
                className="w-32 h-32 rounded-lg border-4 border-white/30 object-cover shadow-xl"
              />
            </div>
          )}
          <h1 className="text-xl font-bold leading-tight mb-1 text-white">
            {content.fullName || "John Doe"}
          </h1>
          {content.workExperience[0]?.title && (
            <p className="text-sky-100 mb-4 font-medium" style={{ fontSize: "var(--font-body)" }}>
              {content.workExperience[0].title}
            </p>
          )}
          
          {/* Contact Info */}
          <div className="space-y-2" style={{ fontSize: "var(--font-small)" }}>
            {content.email && (
              <div className="flex items-start gap-2">
                <span className="text-sky-300 mt-0.5">✉</span>
                <span className="text-sky-50 break-all">{content.email}</span>
              </div>
            )}
            {content.phone && (
              <div className="flex items-start gap-2">
                <span className="text-sky-300">☎</span>
                <span className="text-sky-50">{content.phone}</span>
              </div>
            )}
            {content.location && (
              <div className="flex items-start gap-2">
                <span className="text-sky-300">◎</span>
                <span className="text-sky-50">{content.location}</span>
              </div>
            )}
          </div>

          {/* Links Section */}
          <div className="mt-4 pt-3 border-t border-sky-500/50">
            <h3 className="uppercase text-sky-200 mb-2 font-bold tracking-wide" style={{ fontSize: "var(--font-small)" }}>
              Profiles
            </h3>
            <div className="space-y-1.5" style={{ fontSize: "var(--font-small)" }}>
              {content.linkedinUrl && (
                <div className="flex items-center gap-2">
                  <span className="text-sky-300">in</span>
                  <a href={content.linkedinUrl} target="_blank" rel="noopener noreferrer" className="text-white hover:text-sky-200">
                    LinkedIn
                  </a>
                </div>
              )}
              {content.portfolioUrl && (
                <div className="flex items-center gap-2">
                  <span className="text-sky-300">⌘</span>
                  <a href={content.portfolioUrl} target="_blank" rel="noopener noreferrer" className="text-white hover:text-sky-200">
                    Portfolio
                  </a>
                </div>
              )}
              {content.githubUrl && (
                <div className="flex items-center gap-2">
                  <span className="text-sky-300">⚙</span>
                  <a href={content.githubUrl} target="_blank" rel="noopener noreferrer" className="text-white hover:text-sky-200">
                    GitHub
                  </a>
                </div>
              )}
              {content.customLinks?.map((link) => (
                link.url && (
                  <div key={link.id} className="flex items-center gap-2">
                    <span className="text-sky-300">→</span>
                    <a href={link.url} target="_blank" rel="noopener noreferrer" className="text-white hover:text-sky-200">
                      {link.label || "Link"}
                    </a>
                  </div>
                )
              ))}
            </div>
          </div>
        </div>

        {/* Skills */}
        {/* Technical Skills */}
        {(content.skills.technical?.length ?? 0) > 0 && (
          <div className={`mb-6 ${highlight("skills")}`}>
            <h2 className="font-bold uppercase tracking-wider text-white mb-3 pb-1 border-b border-sky-400/50" style={{ fontSize: "var(--font-header)" }}>
              Technical Skills
            </h2>
            {content.skills.technical.map((group) => (
              <div key={group.id} className="mb-3 last:mb-0">
                <h3 className="uppercase text-sky-200 mb-2 font-medium" style={{ fontSize: "var(--font-small)" }}>{group.header}</h3>
                <div className="space-y-1.5">
                  {group.items.slice(0, 6).map((skill, i) => (
                    <div key={i} className="flex items-center justify-between">
                      <span className="text-white" style={{ fontSize: "var(--font-small)" }}>{skill}</span>
                      <div className="flex gap-0.5">
                        {[1, 2, 3, 4, 5].map((dot) => (
                          <div
                            key={dot}
                            className={`w-1.5 h-1.5 rounded-full ${dot <= 4 ? 'bg-white' : 'bg-sky-400/50'}`}
                          />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Soft Skills */}
        {(content.skills.soft?.length ?? 0) > 0 && (
          <div className={`mb-6 ${highlight("softSkills")}`}>
            <h2 className="font-bold uppercase tracking-wider text-white mb-3 pb-1 border-b border-sky-400/50" style={{ fontSize: "var(--font-header)" }}>
              Soft Skills
            </h2>
            <p className="text-sky-50" style={{ fontSize: "var(--font-small)" }}>
              {content.skills.soft.join(" • ")}
            </p>
          </div>
        )}

        {/* Custom Skills */}
        {(content.skills.custom?.length ?? 0) > 0 && (
          <div className={`mb-6 ${highlight("customSkills")}`}>
            <h2 className="font-bold uppercase tracking-wider text-white mb-3 pb-1 border-b border-sky-400/50" style={{ fontSize: "var(--font-header)" }}>
              {content.skills.customSkillsHeader || "Custom Skills"}
            </h2>
            {content.skills.custom.map((group) => (
              <div key={group.id} className="mb-3 last:mb-0">
                <h3 className="uppercase text-sky-200 mb-1.5 font-medium" style={{ fontSize: "var(--font-small)" }}>{group.header}</h3>
                <p className="text-sky-50" style={{ fontSize: "var(--font-small)" }}>
                  {group.items.join(" • ")}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Certifications */}
        {content.certifications.length > 0 && (
          <div className={`mb-6 ${highlight("certifications")}`}>
            <h2 className="font-bold uppercase tracking-wider text-white mb-3 pb-1 border-b border-sky-400/50" style={{ fontSize: "var(--font-header)" }}>
              Certifications
            </h2>
            {content.certifications.map((cert) => (
              <div key={cert.id} className="mb-2.5" style={{ fontSize: "var(--font-small)" }}>
                <div className="font-bold text-white">
                  {cert.name}
                  {cert.url && (
                    <a href={cert.url} target="_blank" rel="noopener noreferrer" className="text-sky-200 ml-1 hover:underline" style={{ fontSize: "var(--font-xs)" }}>
                      [Link]
                    </a>
                  )}
                </div>
                {cert.issuer && <div className="text-sky-200">{cert.issuer}</div>}
                {cert.date && <div className="text-sky-300" style={{ fontSize: "var(--font-xs)" }}>{cert.date}</div>}
              </div>
            ))}
          </div>
        )}

        {/* Languages */}
        {content.languages.length > 0 && (
          <div className={`${highlight("languages")}`}>
            <h2 className="font-bold uppercase tracking-wider text-white mb-3 pb-1 border-b border-sky-400/50" style={{ fontSize: "var(--font-header)" }}>
              Languages
            </h2>
            {content.languages.map((lang) => (
              <div key={lang.id} className="flex justify-between mb-1.5" style={{ fontSize: "var(--font-small)" }}>
                <span className="text-white font-medium">{lang.language}</span>
                <span className="text-sky-200">
                  {lang.proficiency.charAt(0).toUpperCase() + lang.proficiency.slice(1)}
                </span>
              </div>
            ))}
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="w-[68%] p-6">
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
                  <h2 className="font-bold uppercase tracking-wider text-sky-700 mb-2 pb-1 border-b-2 border-sky-200" style={{ fontSize: "var(--font-header)" }}>
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
                <section key={sectionKey} className={`mb-5 ${highlight("experience")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-sky-700 mb-3 pb-1 border-b-2 border-sky-200" style={{ fontSize: "var(--font-header)" }}>
                    Experience
                  </h2>
                  {content.workExperience.map((exp, index) => (
                    <div key={exp.id} className={`mb-4 ${index > 0 ? 'pt-3 border-t border-gray-100' : ''}`}>
                      <div className="flex justify-between items-baseline mb-1">
                        <div>
                          <span className="font-bold text-gray-900">{exp.company}</span>
                          <span className="text-sky-600 ml-2" style={{ fontSize: "var(--font-body)" }}>{exp.location || ''}</span>
                        </div>
                        <span className="text-sky-600 font-medium" style={{ fontSize: "var(--font-small)" }}>
                          {exp.startDate} — {exp.endDate || (exp.isCurrent ? "Present" : "")}
                        </span>
                      </div>
                      <div className="text-gray-700 font-medium mb-1.5" style={{ fontSize: "var(--font-body)" }}>{exp.title}</div>
                      {exp.achievements.length > 0 && (
                        <ul className="text-gray-600 space-y-1" style={{ fontSize: "var(--font-body)" }}>
                          {exp.achievements.map((ach, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="text-sky-400 mt-0.5">•</span>
                              <span dangerouslySetInnerHTML={{ __html: ach || "" }} />
                            </li>
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
                <section key={sectionKey} className={`mb-5 ${highlight("education")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-sky-700 mb-3 pb-1 border-b-2 border-sky-200" style={{ fontSize: "var(--font-header)" }}>
                    Education
                  </h2>
                  {content.education.map((edu) => (
                    <div key={edu.id} className="mb-3">
                      <div className="flex justify-between items-baseline mb-0.5">
                        <span className="font-bold text-gray-900">{edu.institution}</span>
                        <span className="text-sky-600" style={{ fontSize: "var(--font-small)" }}>{edu.graduationDate}</span>
                      </div>
                      <div className="text-gray-700" style={{ fontSize: "var(--font-body)" }}>
                        {edu.degree}
                        {edu.fieldOfStudy && ` in ${edu.fieldOfStudy}`}
                      </div>
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
                <section key={sectionKey} className={`mb-5 ${highlight("skills")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-sky-700 mb-3 pb-1 border-b-2 border-sky-200" style={{ fontSize: "var(--font-header)" }}>
                    Technical Skills
                  </h2>
                  {content.skills.technical.map((group) => (
                    <div key={group.id} className="mb-2">
                      <h3 className="uppercase text-sky-600 mb-1" style={{ fontSize: "var(--font-small)" }}>{group.header}</h3>
                      <div className="flex flex-wrap gap-1">
                        {group.items.map((skill, i) => (
                          <span
                            key={i}
                            className="bg-sky-100 text-sky-700 px-2 py-1 rounded"
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
                <section key={sectionKey} className={`mb-5 ${highlight("softSkills")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-sky-700 mb-3 pb-1 border-b-2 border-sky-200" style={{ fontSize: "var(--font-header)" }}>
                    Soft Skills
                  </h2>
                  <div className="flex flex-wrap gap-1">
                    {content.skills.soft.map((skill, i) => (
                      <span
                        key={i}
                        className="bg-sky-100 text-sky-700 px-2 py-1 rounded"
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
                <section key={sectionKey} className={`mb-5 ${highlight("customSkills")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-sky-700 mb-3 pb-1 border-b-2 border-sky-200" style={{ fontSize: "var(--font-header)" }}>
                    {content.skills.customSkillsHeader || "Custom Skills"}
                  </h2>
                  {content.skills.custom.map((group) => (
                    <div key={group.id} className="mb-2">
                      <h3 className="uppercase text-sky-600 mb-1" style={{ fontSize: "var(--font-small)" }}>{group.header}</h3>
                      <div className="flex flex-wrap gap-1">
                        {group.items.map((skill, i) => (
                          <span
                            key={i}
                            className="bg-sky-100 text-sky-700 px-2 py-1 rounded"
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
                <section key={sectionKey} className={`mb-5 ${highlight("projects")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-sky-700 mb-3 pb-1 border-b-2 border-sky-200" style={{ fontSize: "var(--font-header)" }}>
                    Projects
                  </h2>
                  {content.projects.map((proj) => (
                    <div key={proj.id} className="mb-3">
                      <div className="flex items-baseline gap-2">
                        <span className="font-bold text-gray-900">{proj.name}</span>
                        {proj.url && (
                          <a href={proj.url} target="_blank" rel="noopener noreferrer" className="text-sky-600 hover:underline" style={{ fontSize: "var(--font-small)" }}>
                            ↗ {proj.url.replace(/^https?:\/\//, '').split('/')[0]}
                          </a>
                        )}
                      </div>
                      <div
                        className="text-gray-600 mt-0.5"
                        style={{ fontSize: "var(--font-body)" }}
                        dangerouslySetInnerHTML={{ __html: proj.description || "" }}
                      />
                      {proj.technologies.length > 0 && (
                        <p className="text-sky-500 mt-1" style={{ fontSize: "var(--font-small)" }}>
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
                <section key={sectionKey} className={`mb-5 ${highlight("certifications")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-sky-700 mb-3 pb-1 border-b-2 border-sky-200" style={{ fontSize: "var(--font-header)" }}>
                    Certifications
                  </h2>
                  {content.certifications.map((cert) => (
                    <div key={cert.id} className="mb-2" style={{ fontSize: "var(--font-body)" }}>
                      <div className="font-medium">
                        {cert.name}
                        {cert.url && (
                          <a href={cert.url} target="_blank" rel="noopener noreferrer" className="text-sky-600 ml-1 hover:underline" style={{ fontSize: "var(--font-xs)" }}>
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
                <section key={sectionKey} className={`mb-5 ${highlight("awards")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-sky-700 mb-3 pb-1 border-b-2 border-sky-200" style={{ fontSize: "var(--font-header)" }}>
                    Awards & Achievements
                  </h2>
                  {content.awards.map((award) => (
                    <div key={award.id} className="mb-2" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-bold text-gray-900">{award.title}</span>
                      {award.issuer && <span className="text-gray-600"> — {award.issuer}</span>}
                      {award.date && <span className="text-sky-600"> ({award.date})</span>}
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
                <section key={sectionKey} className={`mb-5 ${highlight("languages")}`}>
                  <h2 className="font-bold uppercase tracking-wider text-sky-700 mb-3 pb-1 border-b-2 border-sky-200" style={{ fontSize: "var(--font-header)" }}>
                    Languages
                  </h2>
                  {content.languages.map((lang) => (
                    <div key={lang.id} className="flex justify-between mb-1.5" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-medium">{lang.language}</span>
                      <span className="text-sky-600">
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
                    <section key={section.id} className={`mb-5 ${highlight("custom")}`}>
                      <h2 className="font-bold uppercase tracking-wider text-sky-700 mb-3 pb-1 border-b-2 border-sky-200" style={{ fontSize: "var(--font-header)" }}>
                        {section.title}
                      </h2>
                      <ul className="text-gray-600 space-y-1" style={{ fontSize: "var(--font-body)" }}>
                        {section.items.map((item, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-sky-400 mt-0.5">•</span>
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
      </main>
    </div>
  );
}
