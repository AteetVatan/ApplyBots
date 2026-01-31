/**
 * ATS Optimized resume template.
 *
 * Ultra-simple format designed for maximum ATS compatibility.
 * ATS Score: 100
 */

import type { ResumeTemplateProps } from "./types";

export function ATSOptimized({
  content,
  scale = 1,
  highlightSection,
}: ResumeTemplateProps) {
  const highlight = (section: string) =>
    highlightSection === section ? "bg-gray-100 ring-2 ring-gray-300 ring-inset" : "";

  return (
    <div
      className="bg-white text-black shadow-lg"
      style={{
        width: "8.5in",
        minHeight: "11in",
        padding: "0.5in 0.75in",
        transform: `scale(${scale})`,
        transformOrigin: "top left",
        fontFamily: "Arial, sans-serif",
        fontSize: "10pt",
        lineHeight: 1.4,
      }}
    >
      {/* Header - Plain text, no formatting tricks */}
      <header className={`text-center mb-4 ${highlight("contact")}`}>
        <h1 className="text-base font-bold uppercase">
          {content.fullName || "YOUR NAME"}
        </h1>
        <div className="text-[9pt] mt-1">
          {[content.email, content.phone, content.location]
            .filter(Boolean)
            .join(" | ")}
        </div>
        {(content.linkedinUrl || content.portfolioUrl || content.githubUrl) && (
          <div className="text-[9pt]">
            {[content.linkedinUrl, content.portfolioUrl, content.githubUrl]
              .filter(Boolean)
              .join(" | ")}
          </div>
        )}
      </header>

      {/* Summary */}
      {content.professionalSummary && (
        <section className={`mb-4 ${highlight("summary")}`}>
          <h2 className="text-[10pt] font-bold uppercase mb-1">
            PROFESSIONAL SUMMARY
          </h2>
          <hr className="border-black mb-2" />
          <p>{content.professionalSummary}</p>
        </section>
      )}

      {/* Experience */}
      {content.workExperience.length > 0 && (
        <section className={`mb-4 ${highlight("experience")}`}>
          <h2 className="text-[10pt] font-bold uppercase mb-1">
            WORK EXPERIENCE
          </h2>
          <hr className="border-black mb-2" />
          {content.workExperience.map((exp) => (
            <div key={exp.id} className="mb-3">
              <div className="font-bold">{exp.title}</div>
              <div>
                {exp.company}
                {exp.location && `, ${exp.location}`}
              </div>
              <div className="text-[9pt] italic">
                {exp.startDate} - {exp.endDate || (exp.isCurrent ? "Present" : "")}
              </div>
              {exp.achievements.length > 0 && (
                <ul className="mt-1 pl-4 list-disc">
                  {exp.achievements.map((ach, i) => (
                    <li key={i}>{ach}</li>
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
          <h2 className="text-[10pt] font-bold uppercase mb-1">
            EDUCATION
          </h2>
          <hr className="border-black mb-2" />
          {content.education.map((edu) => (
            <div key={edu.id} className="mb-2">
              <div className="font-bold">
                {edu.degree}
                {edu.fieldOfStudy && ` in ${edu.fieldOfStudy}`}
              </div>
              <div>{edu.institution}</div>
              <div className="text-[9pt] italic">
                {edu.graduationDate}
                {edu.gpa && ` | GPA: ${edu.gpa}`}
              </div>
            </div>
          ))}
        </section>
      )}

      {/* Skills - Plain comma-separated list */}
      {(content.skills.technical.length > 0 ||
        content.skills.soft.length > 0 ||
        content.skills.tools.length > 0) && (
        <section className={`mb-4 ${highlight("skills")}`}>
          <h2 className="text-[10pt] font-bold uppercase mb-1">
            SKILLS
          </h2>
          <hr className="border-black mb-2" />
          <p>
            {[
              ...content.skills.technical,
              ...content.skills.tools,
              ...content.skills.soft,
            ].join(", ")}
          </p>
        </section>
      )}

      {/* Projects */}
      {content.projects.length > 0 && (
        <section className={`mb-4 ${highlight("projects")}`}>
          <h2 className="text-[10pt] font-bold uppercase mb-1">
            PROJECTS
          </h2>
          <hr className="border-black mb-2" />
          {content.projects.map((proj) => (
            <div key={proj.id} className="mb-2">
              <div className="font-bold">{proj.name}</div>
              <p>{proj.description}</p>
              {proj.technologies.length > 0 && (
                <div className="text-[9pt]">Technologies: {proj.technologies.join(", ")}</div>
              )}
            </div>
          ))}
        </section>
      )}

      {/* Certifications */}
      {content.certifications.length > 0 && (
        <section className={`mb-4 ${highlight("certifications")}`}>
          <h2 className="text-[10pt] font-bold uppercase mb-1">
            CERTIFICATIONS
          </h2>
          <hr className="border-black mb-2" />
          {content.certifications.map((cert) => (
            <div key={cert.id} className="mb-1">
              {cert.name}
              {cert.issuer && ` - ${cert.issuer}`}
              {cert.date && ` (${cert.date})`}
            </div>
          ))}
        </section>
      )}

      {/* Awards */}
      {content.awards.length > 0 && (
        <section className={`mb-4 ${highlight("awards")}`}>
          <h2 className="text-[10pt] font-bold uppercase mb-1">
            AWARDS
          </h2>
          <hr className="border-black mb-2" />
          {content.awards.map((award) => (
            <div key={award.id} className="mb-1">
              {award.title}
              {award.issuer && ` - ${award.issuer}`}
              {award.date && ` (${award.date})`}
            </div>
          ))}
        </section>
      )}

      {/* Languages */}
      {content.languages.length > 0 && (
        <section className={`${highlight("languages")}`}>
          <h2 className="text-[10pt] font-bold uppercase mb-1">
            LANGUAGES
          </h2>
          <hr className="border-black mb-2" />
          <p>
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
