/**
 * Two Column resume template.
 *
 * Space-efficient two-column layout with sidebar for contact/skills.
 * ATS Score: 88
 */

import type { ResumeTemplateProps } from "./types";

export function TwoColumn({
  content,
  scale = 1,
  highlightSection,
}: ResumeTemplateProps) {
  const highlight = (section: string) =>
    highlightSection === section ? "bg-emerald-50 ring-2 ring-emerald-200 ring-inset" : "";

  return (
    <div
      className="bg-white text-gray-900 shadow-lg flex"
      style={{
        width: "8.5in",
        minHeight: "11in",
        transform: `scale(${scale})`,
        transformOrigin: "top left",
        fontFamily: "'Segoe UI', 'Roboto', sans-serif",
        fontSize: "9pt",
        lineHeight: 1.4,
      }}
    >
      {/* Left Sidebar */}
      <aside className="w-1/3 bg-slate-800 text-white p-5">
        {/* Profile */}
        <div className={`mb-6 ${highlight("contact")}`}>
          <h1 className="text-lg font-bold leading-tight mb-3">
            {content.fullName || "Your Name"}
          </h1>
          <div className="text-[8pt] text-slate-300 space-y-1">
            {content.email && (
              <div className="flex items-center gap-1.5">
                <span className="text-emerald-400">✉</span> {content.email}
              </div>
            )}
            {content.phone && (
              <div className="flex items-center gap-1.5">
                <span className="text-emerald-400">☎</span> {content.phone}
              </div>
            )}
            {content.location && (
              <div className="flex items-center gap-1.5">
                <span className="text-emerald-400">📍</span> {content.location}
              </div>
            )}
            {content.linkedinUrl && (
              <div className="flex items-center gap-1.5">
                <span className="text-emerald-400">in</span> LinkedIn
              </div>
            )}
            {content.githubUrl && (
              <div className="flex items-center gap-1.5">
                <span className="text-emerald-400">⌘</span> GitHub
              </div>
            )}
          </div>
        </div>

        {/* Skills */}
        {(content.skills.technical.length > 0 ||
          content.skills.soft.length > 0 ||
          content.skills.tools.length > 0) && (
          <div className={`mb-6 ${highlight("skills")}`}>
            <h2 className="text-[10pt] font-bold uppercase tracking-wider text-emerald-400 mb-2 pb-1 border-b border-slate-600">
              Skills
            </h2>
            {content.skills.technical.length > 0 && (
              <div className="mb-2">
                <h3 className="text-[8pt] uppercase text-slate-400 mb-1">Technical</h3>
                <div className="flex flex-wrap gap-1">
                  {content.skills.technical.map((skill, i) => (
                    <span
                      key={i}
                      className="bg-slate-700 text-[7pt] px-1.5 py-0.5 rounded"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {content.skills.tools.length > 0 && (
              <div className="mb-2">
                <h3 className="text-[8pt] uppercase text-slate-400 mb-1">Tools</h3>
                <div className="flex flex-wrap gap-1">
                  {content.skills.tools.map((skill, i) => (
                    <span
                      key={i}
                      className="bg-slate-700 text-[7pt] px-1.5 py-0.5 rounded"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {content.skills.soft.length > 0 && (
              <div>
                <h3 className="text-[8pt] uppercase text-slate-400 mb-1">Soft</h3>
                <div className="flex flex-wrap gap-1">
                  {content.skills.soft.map((skill, i) => (
                    <span
                      key={i}
                      className="bg-slate-700 text-[7pt] px-1.5 py-0.5 rounded"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Languages */}
        {content.languages.length > 0 && (
          <div className={`mb-6 ${highlight("languages")}`}>
            <h2 className="text-[10pt] font-bold uppercase tracking-wider text-emerald-400 mb-2 pb-1 border-b border-slate-600">
              Languages
            </h2>
            {content.languages.map((lang) => (
              <div key={lang.id} className="text-[8pt] mb-1">
                <span className="font-medium">{lang.language}</span>
                <span className="text-slate-400 ml-1">
                  ({lang.proficiency.charAt(0).toUpperCase() + lang.proficiency.slice(1)})
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Certifications */}
        {content.certifications.length > 0 && (
          <div className={`${highlight("certifications")}`}>
            <h2 className="text-[10pt] font-bold uppercase tracking-wider text-emerald-400 mb-2 pb-1 border-b border-slate-600">
              Certifications
            </h2>
            {content.certifications.map((cert) => (
              <div key={cert.id} className="text-[8pt] mb-1.5">
                <div className="font-medium">{cert.name}</div>
                {cert.issuer && <div className="text-slate-400">{cert.issuer}</div>}
              </div>
            ))}
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="w-2/3 p-5">
        {/* Summary */}
        {content.professionalSummary && (
          <section className={`mb-4 ${highlight("summary")}`}>
            <h2 className="text-[10pt] font-bold uppercase tracking-wider text-slate-700 mb-2 pb-1 border-b border-slate-200">
              Professional Summary
            </h2>
            <p className="text-gray-600">{content.professionalSummary}</p>
          </section>
        )}

        {/* Experience */}
        {content.workExperience.length > 0 && (
          <section className={`mb-4 ${highlight("experience")}`}>
            <h2 className="text-[10pt] font-bold uppercase tracking-wider text-slate-700 mb-2 pb-1 border-b border-slate-200">
              Work Experience
            </h2>
            {content.workExperience.map((exp) => (
              <div key={exp.id} className="mb-3">
                <div className="flex justify-between items-baseline">
                  <div>
                    <span className="font-semibold text-slate-800">{exp.title}</span>
                    <span className="text-emerald-600 ml-1">@ {exp.company}</span>
                  </div>
                  <span className="text-[8pt] text-gray-500">
                    {exp.startDate} - {exp.endDate || (exp.isCurrent ? "Present" : "")}
                  </span>
                </div>
                {exp.achievements.length > 0 && (
                  <ul className="mt-1 pl-3 text-[8pt] text-gray-600">
                    {exp.achievements.map((ach, i) => (
                      <li key={i} className="mb-0.5 list-disc">
                        {ach}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </section>
        )}

        {/* Education */}
        {content.education.length > 0 && (
          <section className={`mb-4 ${highlight("education")}`}>
            <h2 className="text-[10pt] font-bold uppercase tracking-wider text-slate-700 mb-2 pb-1 border-b border-slate-200">
              Education
            </h2>
            {content.education.map((edu) => (
              <div key={edu.id} className="mb-2">
                <div className="flex justify-between items-baseline">
                  <div>
                    <span className="font-semibold text-slate-800">{edu.degree}</span>
                    {edu.fieldOfStudy && (
                      <span className="text-gray-600"> in {edu.fieldOfStudy}</span>
                    )}
                  </div>
                  <span className="text-[8pt] text-gray-500">{edu.graduationDate}</span>
                </div>
                <div className="text-[8pt] text-gray-600">{edu.institution}</div>
              </div>
            ))}
          </section>
        )}

        {/* Projects */}
        {content.projects.length > 0 && (
          <section className={`${highlight("projects")}`}>
            <h2 className="text-[10pt] font-bold uppercase tracking-wider text-slate-700 mb-2 pb-1 border-b border-slate-200">
              Projects
            </h2>
            {content.projects.map((proj) => (
              <div key={proj.id} className="mb-2">
                <div className="font-semibold text-slate-800">{proj.name}</div>
                <p className="text-[8pt] text-gray-600">{proj.description}</p>
                {proj.technologies.length > 0 && (
                  <p className="text-[7pt] text-emerald-600 mt-0.5">
                    {proj.technologies.join(" • ")}
                  </p>
                )}
              </div>
            ))}
          </section>
        )}
      </main>
    </div>
  );
}
