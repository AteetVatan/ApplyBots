/**
 * Professional Modern resume template.
 *
 * Clean, modern design with blue accents and balanced whitespace.
 * ATS Score: 95
 */

import type { ResumeTemplateProps } from "./types";

export function ProfessionalModern({
  content,
  scale = 1,
  highlightSection,
}: ResumeTemplateProps) {
  const highlight = (section: string) =>
    highlightSection === section ? "bg-blue-50 ring-2 ring-blue-200 ring-inset" : "";

  return (
    <div
      className="bg-white text-gray-900 shadow-lg"
      style={{
        width: "8.5in",
        minHeight: "11in",
        padding: "0.5in",
        transform: `scale(${scale})`,
        transformOrigin: "top left",
        fontFamily: "'Helvetica Neue', Helvetica, Arial, sans-serif",
        fontSize: "10pt",
        lineHeight: 1.4,
      }}
    >
      {/* Header */}
      <header className={`text-center mb-4 pb-3 border-b-2 border-blue-600 ${highlight("contact")}`}>
        <h1 className="text-2xl font-bold text-slate-800 mb-1">
          {content.fullName || "Your Name"}
        </h1>
        <div className="text-xs text-gray-600 space-x-2">
          {content.email && <span>{content.email}</span>}
          {content.phone && <span>• {content.phone}</span>}
          {content.location && <span>• {content.location}</span>}
        </div>
        {(content.linkedinUrl || content.portfolioUrl || content.githubUrl) && (
          <div className="text-xs text-blue-600 mt-1 space-x-3">
            {content.linkedinUrl && <span>LinkedIn</span>}
            {content.portfolioUrl && <span>Portfolio</span>}
            {content.githubUrl && <span>GitHub</span>}
          </div>
        )}
      </header>

      {/* Summary */}
      {content.professionalSummary && (
        <section className={`mb-3 ${highlight("summary")}`}>
          <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-1 pb-0.5 border-b border-gray-200">
            Professional Summary
          </h2>
          <p className="text-[9pt] text-gray-700 leading-relaxed">
            {content.professionalSummary}
          </p>
        </section>
      )}

      {/* Experience */}
      {content.workExperience.length > 0 && (
        <section className={`mb-3 ${highlight("experience")}`}>
          <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 pb-0.5 border-b border-gray-200">
            Professional Experience
          </h2>
          {content.workExperience.map((exp) => (
            <div key={exp.id} className="mb-2.5">
              <div className="flex justify-between items-baseline">
                <div>
                  <span className="font-semibold text-slate-800">{exp.title}</span>
                  <span className="text-gray-700"> | {exp.company}</span>
                </div>
                <span className="text-[8pt] text-gray-500">
                  {exp.startDate}
                  {exp.endDate ? ` - ${exp.endDate}` : exp.isCurrent ? " - Present" : ""}
                  {exp.location && ` | ${exp.location}`}
                </span>
              </div>
              {exp.achievements.length > 0 && (
                <ul className="mt-1 pl-3 text-[9pt] text-gray-700">
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
        <section className={`mb-3 ${highlight("education")}`}>
          <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 pb-0.5 border-b border-gray-200">
            Education
          </h2>
          {content.education.map((edu) => (
            <div key={edu.id} className="mb-2">
              <div className="flex justify-between items-baseline">
                <div>
                  <span className="font-semibold text-slate-800">{edu.degree}</span>
                  {edu.fieldOfStudy && <span> in {edu.fieldOfStudy}</span>}
                  <span className="text-gray-700"> | {edu.institution}</span>
                </div>
                <span className="text-[8pt] text-gray-500">
                  {edu.graduationDate}
                  {edu.gpa && ` | GPA: ${edu.gpa}`}
                </span>
              </div>
            </div>
          ))}
        </section>
      )}

      {/* Skills */}
      {(content.skills.technical.length > 0 ||
        content.skills.soft.length > 0 ||
        content.skills.tools.length > 0) && (
        <section className={`mb-3 ${highlight("skills")}`}>
          <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 pb-0.5 border-b border-gray-200">
            Skills
          </h2>
          <div className="text-[9pt] space-y-1">
            {content.skills.technical.length > 0 && (
              <p>
                <span className="font-semibold text-slate-700">Technical: </span>
                <span className="text-gray-700">{content.skills.technical.join(", ")}</span>
              </p>
            )}
            {content.skills.tools.length > 0 && (
              <p>
                <span className="font-semibold text-slate-700">Tools & Technologies: </span>
                <span className="text-gray-700">{content.skills.tools.join(", ")}</span>
              </p>
            )}
            {content.skills.soft.length > 0 && (
              <p>
                <span className="font-semibold text-slate-700">Soft Skills: </span>
                <span className="text-gray-700">{content.skills.soft.join(", ")}</span>
              </p>
            )}
          </div>
        </section>
      )}

      {/* Projects */}
      {content.projects.length > 0 && (
        <section className={`mb-3 ${highlight("projects")}`}>
          <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 pb-0.5 border-b border-gray-200">
            Projects
          </h2>
          {content.projects.map((proj) => (
            <div key={proj.id} className="mb-2">
              <div className="font-semibold text-slate-800">
                {proj.name}
                {proj.url && (
                  <span className="text-[8pt] text-blue-600 ml-1">[Link]</span>
                )}
              </div>
              <p className="text-[9pt] text-gray-700">{proj.description}</p>
              {proj.technologies.length > 0 && (
                <p className="text-[8pt] text-gray-500 italic">
                  Technologies: {proj.technologies.join(", ")}
                </p>
              )}
            </div>
          ))}
        </section>
      )}

      {/* Certifications */}
      {content.certifications.length > 0 && (
        <section className={`mb-3 ${highlight("certifications")}`}>
          <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 pb-0.5 border-b border-gray-200">
            Certifications
          </h2>
          {content.certifications.map((cert) => (
            <p key={cert.id} className="text-[9pt] mb-1">
              <span className="font-semibold">{cert.name}</span>
              {cert.issuer && ` - ${cert.issuer}`}
              {cert.date && ` (${cert.date})`}
            </p>
          ))}
        </section>
      )}

      {/* Awards */}
      {content.awards.length > 0 && (
        <section className={`mb-3 ${highlight("awards")}`}>
          <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 pb-0.5 border-b border-gray-200">
            Awards & Achievements
          </h2>
          {content.awards.map((award) => (
            <div key={award.id} className="text-[9pt] mb-1">
              <span className="font-semibold">{award.title}</span>
              {award.issuer && ` - ${award.issuer}`}
              {award.date && ` (${award.date})`}
              {award.description && (
                <p className="text-[8pt] text-gray-600">{award.description}</p>
              )}
            </div>
          ))}
        </section>
      )}

      {/* Languages */}
      {content.languages.length > 0 && (
        <section className={`mb-3 ${highlight("languages")}`}>
          <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 pb-0.5 border-b border-gray-200">
            Languages
          </h2>
          <div className="text-[9pt] flex flex-wrap gap-4">
            {content.languages.map((lang) => (
              <span key={lang.id}>
                {lang.language}{" "}
                <span className="text-gray-500 italic">
                  ({lang.proficiency.charAt(0).toUpperCase() + lang.proficiency.slice(1)})
                </span>
              </span>
            ))}
          </div>
        </section>
      )}

      {/* Custom Sections */}
      {content.customSections.map((section) => (
        <section key={section.id} className={`mb-3 ${highlight("custom")}`}>
          <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 pb-0.5 border-b border-gray-200">
            {section.title}
          </h2>
          <ul className="pl-3 text-[9pt] text-gray-700">
            {section.items.map((item, i) => (
              <li key={i} className="mb-0.5 list-disc">
                {item}
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  );
}
