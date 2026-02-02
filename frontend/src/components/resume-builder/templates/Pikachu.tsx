/**
 * Pikachu resume template.
 *
 * Two-column layout with vibrant yellow/gold sidebar.
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

export function Pikachu({
  content,
  scale = 1,
  highlightSection,
  themeSettings = DEFAULT_THEME,
}: ResumeTemplateProps) {
  const highlight = (section: string) =>
    highlightSection === section ? "bg-yellow-50 ring-2 ring-yellow-200 ring-inset" : "";

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
        className="w-1/3 text-gray-900 p-5"
        style={{ background: getPrimaryGradient(themeSettings) }}
      >
        {/* Profile */}
        <div className={`mb-6 ${highlight("contact")}`}>
          {content.profilePictureUrl && (
            <div className="mb-4 flex justify-center">
              <img
                src={content.profilePictureUrl}
                alt="Profile"
                className="w-28 h-28 rounded-full border-4 border-white object-cover shadow-lg"
              />
            </div>
          )}
          <h1 className="text-xl font-black leading-tight mb-1 text-center text-gray-900">
            {content.fullName || "Your Name"}
          </h1>
          {content.workExperience[0]?.title && (
            <p className="text-gray-800 text-center mb-4 font-medium" style={{ fontSize: "var(--font-body)" }}>
              {content.workExperience[0].title}
            </p>
          )}
          <div className="bg-white/30 rounded-lg p-3 text-gray-800 space-y-1.5" style={{ fontSize: "var(--font-small)" }}>
            {content.email && (
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 bg-gray-900 text-white rounded flex items-center justify-center" style={{ fontSize: "var(--font-xs)" }}>@</span>
                <span className="truncate">{content.email}</span>
              </div>
            )}
            {content.phone && (
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 bg-gray-900 text-white rounded flex items-center justify-center" style={{ fontSize: "var(--font-xs)" }}>☎</span>
                <span>{content.phone}</span>
              </div>
            )}
            {content.location && (
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 bg-gray-900 text-white rounded flex items-center justify-center" style={{ fontSize: "var(--font-xs)" }}>◎</span>
                <span>{content.location}</span>
              </div>
            )}
          </div>
          <div className="flex flex-wrap justify-center gap-2 mt-3">
            {content.linkedinUrl && (
              <a href={content.linkedinUrl} target="_blank" rel="noopener noreferrer" className="bg-gray-900 text-white px-2 py-1 rounded hover:bg-gray-700" style={{ fontSize: "var(--font-xs)" }}>
                LinkedIn
              </a>
            )}
            {content.portfolioUrl && (
              <a href={content.portfolioUrl} target="_blank" rel="noopener noreferrer" className="bg-gray-900 text-white px-2 py-1 rounded hover:bg-gray-700" style={{ fontSize: "var(--font-xs)" }}>
                Portfolio
              </a>
            )}
            {content.githubUrl && (
              <a href={content.githubUrl} target="_blank" rel="noopener noreferrer" className="bg-gray-900 text-white px-2 py-1 rounded hover:bg-gray-700" style={{ fontSize: "var(--font-xs)" }}>
                GitHub
              </a>
            )}
            {content.customLinks?.map((link) => (
              link.url && (
                <a key={link.id} href={link.url} target="_blank" rel="noopener noreferrer" className="bg-gray-900 text-white px-2 py-1 rounded hover:bg-gray-700" style={{ fontSize: "var(--font-xs)" }}>
                  {link.label || "Link"}
                </a>
              )
            ))}
          </div>
        </div>

        {/* Skills */}
        {/* Technical Skills */}
        {(content.skills.technical?.length ?? 0) > 0 && (
          <div className={`mb-6 ${highlight("skills")}`}>
            <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 pb-1 border-b-2 border-gray-900" style={{ fontSize: "var(--font-header)" }}>
              Technical Skills
            </h2>
            {content.skills.technical.map((group) => (
              <div key={group.id} className="mb-3 last:mb-0">
                <h3 className="uppercase text-gray-700 mb-1.5 font-bold" style={{ fontSize: "var(--font-small)" }}>{group.header}</h3>
                <div className="flex flex-wrap gap-1">
                  {group.items.map((skill, i) => (
                    <span key={i} className="bg-white/50 px-2 py-1 rounded-full text-gray-900 font-medium" style={{ fontSize: "var(--font-xs)" }}>
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Soft Skills */}
        {(content.skills.soft?.length ?? 0) > 0 && (
          <div className={`mb-6 ${highlight("softSkills")}`}>
            <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 pb-1 border-b-2 border-gray-900" style={{ fontSize: "var(--font-header)" }}>
              Soft Skills
            </h2>
            <div className="flex flex-wrap gap-1">
              {content.skills.soft.map((skill, i) => (
                <span key={i} className="bg-white/50 px-2 py-1 rounded-full text-gray-900 font-medium" style={{ fontSize: "var(--font-xs)" }}>
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Custom Skills */}
        {(content.skills.custom?.length ?? 0) > 0 && (
          <div className={`mb-6 ${highlight("customSkills")}`}>
            <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 pb-1 border-b-2 border-gray-900" style={{ fontSize: "var(--font-header)" }}>
              {content.skills.customSkillsHeader || "Custom Skills"}
            </h2>
            {content.skills.custom.map((group) => (
              <div key={group.id} className="mb-3 last:mb-0">
                <h3 className="uppercase text-gray-700 mb-1.5 font-bold" style={{ fontSize: "var(--font-small)" }}>{group.header}</h3>
                <div className="flex flex-wrap gap-1">
                  {group.items.map((skill, i) => (
                    <span key={i} className="bg-white/50 px-2 py-1 rounded-full text-gray-900 font-medium" style={{ fontSize: "var(--font-xs)" }}>
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Languages */}
        {content.languages.length > 0 && (
          <div className={`mb-6 ${highlight("languages")}`}>
            <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 pb-1 border-b-2 border-gray-900" style={{ fontSize: "var(--font-header)" }}>
              Languages
            </h2>
            {content.languages.map((lang) => (
              <div key={lang.id} className="flex justify-between mb-1.5" style={{ fontSize: "var(--font-small)" }}>
                <span className="font-bold">{lang.language}</span>
                <span className="text-gray-700">
                  {lang.proficiency.charAt(0).toUpperCase() + lang.proficiency.slice(1)}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Certifications */}
        {content.certifications.length > 0 && (
          <div className={`${highlight("certifications")}`}>
            <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 pb-1 border-b-2 border-gray-900" style={{ fontSize: "var(--font-header)" }}>
              Certifications
            </h2>
            {content.certifications.map((cert) => (
              <div key={cert.id} className="mb-2" style={{ fontSize: "var(--font-small)" }}>
                <div className="font-bold">
                  {cert.name}
                  {cert.url && (
                    <a href={cert.url} target="_blank" rel="noopener noreferrer" className="text-gray-600 ml-1 hover:underline" style={{ fontSize: "var(--font-xs)" }}>
                      [Link]
                    </a>
                  )}
                </div>
                {cert.issuer && <div className="text-gray-700">{cert.issuer}</div>}
                {cert.date && <div className="text-gray-600" style={{ fontSize: "var(--font-xs)" }}>{cert.date}</div>}
              </div>
            ))}
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="w-2/3 p-6 bg-gray-50">
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
                  <h2 className="font-black uppercase tracking-wider text-gray-900 mb-2 flex items-center gap-2" style={{ fontSize: "var(--font-header)" }}>
                    <span className="w-3 h-3 bg-yellow-400 rounded-full"></span>
                    Profile
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
                  <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 flex items-center gap-2" style={{ fontSize: "var(--font-header)" }}>
                    <span className="w-3 h-3 bg-yellow-400 rounded-full"></span>
                    Experience
                  </h2>
                  {content.workExperience.map((exp) => (
                    <div key={exp.id} className="mb-4 pl-4 border-l-3 border-yellow-400">
                      <div className="flex justify-between items-baseline mb-1">
                        <div>
                          <span className="font-bold text-gray-900">{exp.title}</span>
                          <span className="text-yellow-600 font-medium ml-1">@ {exp.company}</span>
                        </div>
                        <span className="text-gray-500 bg-yellow-100 px-2 py-0.5 rounded" style={{ fontSize: "var(--font-small)" }}>
                          {exp.startDate} - {exp.endDate || (exp.isCurrent ? "Present" : "")}
                        </span>
                      </div>
                      {exp.location && (
                        <div className="text-gray-500 mb-1" style={{ fontSize: "var(--font-small)" }}>{exp.location}</div>
                      )}
                      {exp.achievements.length > 0 && (
                        <ul className="mt-1.5 text-gray-600 space-y-1" style={{ fontSize: "var(--font-body)" }}>
                          {exp.achievements.map((ach, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="text-yellow-500 font-bold">▸</span>
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
                  <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 flex items-center gap-2" style={{ fontSize: "var(--font-header)" }}>
                    <span className="w-3 h-3 bg-yellow-400 rounded-full"></span>
                    Education
                  </h2>
                  {content.education.map((edu) => (
                    <div key={edu.id} className="mb-3 pl-4 border-l-3 border-yellow-400">
                      <div className="flex justify-between items-baseline mb-0.5">
                        <span className="font-bold text-gray-900">{edu.degree}</span>
                        <span className="text-gray-500" style={{ fontSize: "var(--font-small)" }}>{edu.graduationDate}</span>
                      </div>
                      {edu.fieldOfStudy && (
                        <div className="text-gray-600" style={{ fontSize: "var(--font-small)" }}>in {edu.fieldOfStudy}</div>
                      )}
                      <div className="text-yellow-600 font-medium" style={{ fontSize: "var(--font-body)" }}>{edu.institution}</div>
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
                  <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 flex items-center gap-2" style={{ fontSize: "var(--font-header)" }}>
                    <span className="w-3 h-3 bg-yellow-400 rounded-full"></span>
                    Technical Skills
                  </h2>
                  {content.skills.technical.map((group) => (
                    <div key={group.id} className="mb-2 pl-4 border-l-3 border-yellow-400">
                      <h3 className="uppercase text-yellow-600 mb-1" style={{ fontSize: "var(--font-small)" }}>{group.header}</h3>
                      <div className="flex flex-wrap gap-1">
                        {group.items.map((skill, i) => (
                          <span key={i} className="px-1.5 py-0.5 bg-yellow-100 text-yellow-700 rounded font-medium" style={{ fontSize: "var(--font-xs)" }}>
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
                  <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 flex items-center gap-2" style={{ fontSize: "var(--font-header)" }}>
                    <span className="w-3 h-3 bg-yellow-400 rounded-full"></span>
                    Soft Skills
                  </h2>
                  <div className="pl-4 border-l-3 border-yellow-400">
                    <div className="flex flex-wrap gap-1">
                      {content.skills.soft.map((skill, i) => (
                        <span key={i} className="px-1.5 py-0.5 bg-yellow-100 text-yellow-700 rounded font-medium" style={{ fontSize: "var(--font-xs)" }}>
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </section>
              );
            }

            // Custom Skills
            if (sectionKey === "customSkills" && (content.skills.custom?.length ?? 0) > 0) {
              return (
                <section key={sectionKey} className={`mb-5 ${highlight("customSkills")}`}>
                  <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 flex items-center gap-2" style={{ fontSize: "var(--font-header)" }}>
                    <span className="w-3 h-3 bg-yellow-400 rounded-full"></span>
                    {content.skills.customSkillsHeader || "Custom Skills"}
                  </h2>
                  {content.skills.custom.map((group) => (
                    <div key={group.id} className="mb-2 pl-4 border-l-3 border-yellow-400">
                      <h3 className="uppercase text-yellow-600 mb-1" style={{ fontSize: "var(--font-small)" }}>{group.header}</h3>
                      <div className="flex flex-wrap gap-1">
                        {group.items.map((skill, i) => (
                          <span key={i} className="px-1.5 py-0.5 bg-yellow-100 text-yellow-700 rounded font-medium" style={{ fontSize: "var(--font-xs)" }}>
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
                  <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 flex items-center gap-2" style={{ fontSize: "var(--font-header)" }}>
                    <span className="w-3 h-3 bg-yellow-400 rounded-full"></span>
                    Projects
                  </h2>
                  {content.projects.map((proj) => (
                    <div key={proj.id} className="mb-3 pl-4 border-l-3 border-yellow-400">
                      <div className="font-bold text-gray-900">
                        {proj.name}
                        {proj.url && (
                          <a href={proj.url} target="_blank" rel="noopener noreferrer" className="text-yellow-600 ml-2 hover:underline" style={{ fontSize: "var(--font-small)" }}>
                            ↗ View
                          </a>
                        )}
                      </div>
                      <div
                        className="text-gray-600 mt-0.5"
                        style={{ fontSize: "var(--font-body)" }}
                        dangerouslySetInnerHTML={{ __html: proj.description || "" }}
                      />
                      {proj.technologies.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {proj.technologies.map((tech, i) => (
                            <span key={i} className="px-1.5 py-0.5 bg-yellow-100 text-yellow-700 rounded font-medium" style={{ fontSize: "var(--font-xs)" }}>
                              {tech}
                            </span>
                          ))}
                        </div>
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
                  <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 flex items-center gap-2" style={{ fontSize: "var(--font-header)" }}>
                    <span className="w-3 h-3 bg-yellow-400 rounded-full"></span>
                    Certifications
                  </h2>
                  {content.certifications.map((cert) => (
                    <div key={cert.id} className="mb-2 pl-4 border-l-3 border-yellow-400" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-medium">{cert.name}</span>
                      {cert.issuer && <span className="text-gray-600" style={{ fontSize: "var(--font-small)" }}> - {cert.issuer}</span>}
                      {cert.date && <span className="text-yellow-600" style={{ fontSize: "var(--font-small)" }}> ({cert.date})</span>}
                      {cert.url && (
                        <a href={cert.url} target="_blank" rel="noopener noreferrer" className="text-yellow-600 ml-1 hover:underline" style={{ fontSize: "var(--font-xs)" }}>
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
                  <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 flex items-center gap-2" style={{ fontSize: "var(--font-header)" }}>
                    <span className="w-3 h-3 bg-yellow-400 rounded-full"></span>
                    Awards
                  </h2>
                  {content.awards.map((award) => (
                    <div key={award.id} className="mb-2 pl-4 border-l-3 border-yellow-400" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-bold text-gray-900">{award.title}</span>
                      {award.issuer && <span className="text-gray-600" style={{ fontSize: "var(--font-small)" }}> - {award.issuer}</span>}
                      {award.date && <span className="text-yellow-600" style={{ fontSize: "var(--font-small)" }}> ({award.date})</span>}
                    </div>
                  ))}
                </section>
              );
            }

            // Languages
            if (sectionKey === "languages" && content.languages.length > 0) {
              return (
                <section key={sectionKey} className={`mb-5 ${highlight("languages")}`}>
                  <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 flex items-center gap-2" style={{ fontSize: "var(--font-header)" }}>
                    <span className="w-3 h-3 bg-yellow-400 rounded-full"></span>
                    Languages
                  </h2>
                  {content.languages.map((lang) => (
                    <div key={lang.id} className="mb-1.5 pl-4 border-l-3 border-yellow-400" style={{ fontSize: "var(--font-body)" }}>
                      <span className="font-medium">{lang.language}</span>
                      <span className="text-yellow-600 ml-1" style={{ fontSize: "var(--font-small)" }}>
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
                    <section key={section.id} className={`mb-5 ${highlight("custom")}`}>
                      <h2 className="font-black uppercase tracking-wider text-gray-900 mb-3 flex items-center gap-2" style={{ fontSize: "var(--font-header)" }}>
                        <span className="w-3 h-3 bg-yellow-400 rounded-full"></span>
                        {section.title}
                      </h2>
                      <ul className="pl-4 text-gray-600 space-y-1" style={{ fontSize: "var(--font-body)" }}>
                        {section.items.map((item, i) => (
                          <li key={i} className="flex items-start gap-2">
                            <span className="text-yellow-500 font-bold">▸</span>
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
