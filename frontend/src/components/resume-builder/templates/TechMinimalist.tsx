/**
 * Tech Minimalist resume template.
 *
 * Monospace font with grid layout, perfect for developers.
 * ATS Score: 92
 */

import type { ResumeTemplateProps } from "./types";

export function TechMinimalist({
  content,
  scale = 1,
  highlightSection,
}: ResumeTemplateProps) {
  const highlight = (section: string) =>
    highlightSection === section ? "bg-cyan-50 ring-2 ring-cyan-200 ring-inset" : "";

  return (
    <div
      className="bg-white text-gray-900 shadow-lg"
      style={{
        width: "8.5in",
        minHeight: "11in",
        padding: "0.5in",
        transform: `scale(${scale})`,
        transformOrigin: "top left",
        fontFamily: "'SF Mono', 'Consolas', 'Monaco', monospace",
        fontSize: "9pt",
        lineHeight: 1.5,
      }}
    >
      {/* Header */}
      <header className={`mb-4 ${highlight("contact")}`}>
        <h1 className="text-xl font-semibold tracking-tight text-gray-900">
          {content.fullName || "Your Name"}
        </h1>
        <div className="text-[8pt] text-gray-500 mt-1 flex flex-wrap gap-2">
          {content.email && <span>{content.email}</span>}
          {content.phone && <span>/ {content.phone}</span>}
          {content.githubUrl && (
            <span className="text-cyan-600">/ GitHub</span>
          )}
          {content.linkedinUrl && (
            <span className="text-cyan-600">/ LinkedIn</span>
          )}
          {content.portfolioUrl && (
            <span className="text-cyan-600">/ Portfolio</span>
          )}
        </div>
      </header>

      {/* Summary */}
      {content.professionalSummary && (
        <section className={`mb-4 ${highlight("summary")}`}>
          <h2 className="text-[8pt] font-semibold uppercase tracking-widest text-gray-400 mb-1.5">
            About
          </h2>
          <p className="text-gray-700">{content.professionalSummary}</p>
        </section>
      )}

      {/* Experience */}
      {content.workExperience.length > 0 && (
        <section className={`mb-4 ${highlight("experience")}`}>
          <h2 className="text-[8pt] font-semibold uppercase tracking-widest text-gray-400 mb-2">
            Experience
          </h2>
          {content.workExperience.map((exp) => (
            <div key={exp.id} className="mb-3">
              <div className="flex justify-between items-baseline">
                <div>
                  <span className="font-semibold">{exp.title}</span>
                  <span className="text-cyan-600"> @ {exp.company}</span>
                </div>
                <span className="text-[8pt] text-gray-400">
                  {exp.startDate} → {exp.endDate || (exp.isCurrent ? "Now" : "")}
                </span>
              </div>
              {exp.achievements.length > 0 && (
                <ul className="mt-1 pl-4 text-gray-600">
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

      {/* Tech Stack */}
      {(content.skills.technical.length > 0 || content.skills.tools.length > 0) && (
        <section className={`mb-4 ${highlight("skills")}`}>
          <h2 className="text-[8pt] font-semibold uppercase tracking-widest text-gray-400 mb-2">
            Tech Stack
          </h2>
          <div className="grid grid-cols-2 gap-3 text-[8pt]">
            {content.skills.technical.length > 0 && (
              <div>
                <div className="text-[7pt] text-gray-400 uppercase tracking-wider mb-0.5">
                  Languages & Frameworks
                </div>
                <div className="text-gray-700">{content.skills.technical.join(", ")}</div>
              </div>
            )}
            {content.skills.tools.length > 0 && (
              <div>
                <div className="text-[7pt] text-gray-400 uppercase tracking-wider mb-0.5">
                  Tools & Platforms
                </div>
                <div className="text-gray-700">{content.skills.tools.join(", ")}</div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Projects */}
      {content.projects.length > 0 && (
        <section className={`mb-4 ${highlight("projects")}`}>
          <h2 className="text-[8pt] font-semibold uppercase tracking-widest text-gray-400 mb-2">
            Projects
          </h2>
          {content.projects.map((proj) => (
            <div key={proj.id} className="mb-2.5">
              <div>
                <span className="font-semibold">{proj.name}</span>
                {proj.url && (
                  <span className="text-cyan-600 ml-1">[↗]</span>
                )}
              </div>
              <p className="text-[8pt] text-gray-600">{proj.description}</p>
              {proj.technologies.length > 0 && (
                <p className="text-[7pt] text-gray-400 mt-0.5">
                  {proj.technologies.join(" • ")}
                </p>
              )}
            </div>
          ))}
        </section>
      )}

      {/* Education */}
      {content.education.length > 0 && (
        <section className={`mb-4 ${highlight("education")}`}>
          <h2 className="text-[8pt] font-semibold uppercase tracking-widest text-gray-400 mb-2">
            Education
          </h2>
          {content.education.map((edu) => (
            <div key={edu.id} className="mb-1.5">
              <span>{edu.degree}</span>
              <span className="text-gray-500"> — {edu.institution}</span>
              {edu.graduationDate && (
                <span className="text-gray-400 text-[8pt]"> ({edu.graduationDate})</span>
              )}
            </div>
          ))}
        </section>
      )}

      {/* Certifications */}
      {content.certifications.length > 0 && (
        <section className={`mb-4 ${highlight("certifications")}`}>
          <h2 className="text-[8pt] font-semibold uppercase tracking-widest text-gray-400 mb-2">
            Certifications
          </h2>
          <div className="text-[8pt] space-y-0.5">
            {content.certifications.map((cert) => (
              <div key={cert.id}>
                <span className="font-medium">{cert.name}</span>
                {cert.issuer && <span className="text-gray-500"> — {cert.issuer}</span>}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
