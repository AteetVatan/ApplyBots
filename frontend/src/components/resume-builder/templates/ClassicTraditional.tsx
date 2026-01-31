/**
 * Classic Traditional resume template.
 *
 * Timeless serif design suitable for conservative industries.
 * ATS Score: 98
 */

import type { ResumeTemplateProps } from "./types";

export function ClassicTraditional({
  content,
  scale = 1,
  highlightSection,
}: ResumeTemplateProps) {
  const highlight = (section: string) =>
    highlightSection === section ? "bg-amber-50 ring-2 ring-amber-200 ring-inset" : "";

  return (
    <div
      className="bg-white text-black shadow-lg"
      style={{
        width: "8.5in",
        minHeight: "11in",
        padding: "0.75in",
        transform: `scale(${scale})`,
        transformOrigin: "top left",
        fontFamily: "'Times New Roman', Times, serif",
        fontSize: "11pt",
        lineHeight: 1.3,
      }}
    >
      {/* Header */}
      <header className={`text-center mb-3.5 ${highlight("contact")}`}>
        <h1 className="text-lg font-bold uppercase tracking-widest">
          {content.fullName || "YOUR NAME"}
        </h1>
        <div className="text-[10pt] mt-1">
          {content.email}
          {content.phone && ` • ${content.phone}`}
          {content.location && ` • ${content.location}`}
        </div>
      </header>

      {/* Objective/Summary */}
      {content.professionalSummary && (
        <section className={`mb-3 ${highlight("summary")}`}>
          <h2 className="text-sm font-bold uppercase border-b border-black mb-1.5 pb-0.5">
            Objective
          </h2>
          <p className="text-[10pt]">{content.professionalSummary}</p>
        </section>
      )}

      {/* Experience */}
      {content.workExperience.length > 0 && (
        <section className={`mb-3 ${highlight("experience")}`}>
          <h2 className="text-sm font-bold uppercase border-b border-black mb-2 pb-0.5">
            Experience
          </h2>
          {content.workExperience.map((exp) => (
            <div key={exp.id} className="mb-2.5">
              <div className="flex justify-between">
                <span className="font-bold">
                  {exp.title}, {exp.company}
                </span>
                <span className="italic text-[10pt]">
                  {exp.startDate} - {exp.endDate || (exp.isCurrent ? "Present" : "")}
                </span>
              </div>
              {exp.achievements.length > 0 && (
                <ul className="mt-1 pl-5 list-disc text-[10pt]">
                  {exp.achievements.map((ach, i) => (
                    <li key={i} className="mb-0.5">
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
          <h2 className="text-sm font-bold uppercase border-b border-black mb-2 pb-0.5">
            Education
          </h2>
          {content.education.map((edu) => (
            <div key={edu.id} className="mb-2">
              <div className="flex justify-between">
                <span className="font-bold">
                  {edu.degree}
                  {edu.fieldOfStudy && ` in ${edu.fieldOfStudy}`}
                </span>
                <span className="italic text-[10pt]">{edu.graduationDate}</span>
              </div>
              <div>{edu.institution}</div>
              {edu.gpa && <div className="text-[10pt]">GPA: {edu.gpa}</div>}
            </div>
          ))}
        </section>
      )}

      {/* Skills */}
      {(content.skills.technical.length > 0 ||
        content.skills.soft.length > 0 ||
        content.skills.tools.length > 0) && (
        <section className={`mb-3 ${highlight("skills")}`}>
          <h2 className="text-sm font-bold uppercase border-b border-black mb-2 pb-0.5">
            Skills
          </h2>
          <p className="text-[10pt]">
            {[
              ...content.skills.technical,
              ...content.skills.soft,
              ...content.skills.tools,
            ].join(", ")}
          </p>
        </section>
      )}

      {/* Certifications */}
      {content.certifications.length > 0 && (
        <section className={`mb-3 ${highlight("certifications")}`}>
          <h2 className="text-sm font-bold uppercase border-b border-black mb-2 pb-0.5">
            Certifications
          </h2>
          {content.certifications.map((cert) => (
            <div key={cert.id} className="text-[10pt] mb-1">
              <span className="font-bold">{cert.name}</span>
              {cert.issuer && `, ${cert.issuer}`}
              {cert.date && ` (${cert.date})`}
            </div>
          ))}
        </section>
      )}

      {/* Awards */}
      {content.awards.length > 0 && (
        <section className={`mb-3 ${highlight("awards")}`}>
          <h2 className="text-sm font-bold uppercase border-b border-black mb-2 pb-0.5">
            Honors & Awards
          </h2>
          {content.awards.map((award) => (
            <div key={award.id} className="text-[10pt] mb-1">
              <span className="font-bold">{award.title}</span>
              {award.issuer && `, ${award.issuer}`}
              {award.date && ` (${award.date})`}
            </div>
          ))}
        </section>
      )}

      {/* Languages */}
      {content.languages.length > 0 && (
        <section className={`mb-3 ${highlight("languages")}`}>
          <h2 className="text-sm font-bold uppercase border-b border-black mb-2 pb-0.5">
            Languages
          </h2>
          <p className="text-[10pt]">
            {content.languages
              .map(
                (lang) =>
                  `${lang.language} (${lang.proficiency.charAt(0).toUpperCase() + lang.proficiency.slice(1)})`
              )
              .join(", ")}
          </p>
        </section>
      )}
    </div>
  );
}
