/**
 * Editor panel with section navigation and forms.
 */

"use client";

import { useResumeBuilderStore, type SectionKey } from "@/stores/resume-builder-store";
import {
  User,
  FileText,
  Briefcase,
  GraduationCap,
  Wrench,
  FolderGit2,
  Award,
  Medal,
  Languages,
  PlusCircle,
} from "lucide-react";
import {
  ContactSection,
  SummarySection,
  ExperienceSection,
  EducationSection,
  SkillsSection,
  ProjectsSection,
} from "./sections";

const SECTIONS: {
  key: SectionKey;
  label: string;
  icon: React.ReactNode;
  component: React.ComponentType;
}[] = [
  { key: "contact", label: "Contact", icon: <User className="h-4 w-4" />, component: ContactSection },
  { key: "summary", label: "Summary", icon: <FileText className="h-4 w-4" />, component: SummarySection },
  { key: "experience", label: "Experience", icon: <Briefcase className="h-4 w-4" />, component: ExperienceSection },
  { key: "education", label: "Education", icon: <GraduationCap className="h-4 w-4" />, component: EducationSection },
  { key: "skills", label: "Skills", icon: <Wrench className="h-4 w-4" />, component: SkillsSection },
  { key: "projects", label: "Projects", icon: <FolderGit2 className="h-4 w-4" />, component: ProjectsSection },
  // Placeholder sections - will show simple forms
  { key: "certifications", label: "Certifications", icon: <Award className="h-4 w-4" />, component: CertificationsPlaceholder },
  { key: "awards", label: "Awards", icon: <Medal className="h-4 w-4" />, component: AwardsPlaceholder },
  { key: "languages", label: "Languages", icon: <Languages className="h-4 w-4" />, component: LanguagesPlaceholder },
];

function CertificationsPlaceholder() {
  const certifications = useResumeBuilderStore((s) => s.content.certifications);
  const addCertification = useResumeBuilderStore((s) => s.addCertification);
  const removeCertification = useResumeBuilderStore((s) => s.removeCertification);
  const updateCertification = useResumeBuilderStore((s) => s.updateCertification);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Certifications</h3>
        <button
          onClick={() => addCertification({ name: "", issuer: "", date: null, expiryDate: null, credentialId: null, url: null })}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          <PlusCircle className="h-4 w-4" />
          Add
        </button>
      </div>
      {certifications.map((cert) => (
        <div key={cert.id} className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg space-y-2">
          <input
            type="text"
            value={cert.name}
            onChange={(e) => updateCertification(cert.id, { name: e.target.value })}
            placeholder="Certification name"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
          <div className="flex gap-2">
            <input
              type="text"
              value={cert.issuer}
              onChange={(e) => updateCertification(cert.id, { issuer: e.target.value })}
              placeholder="Issuer"
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <input
              type="text"
              value={cert.date || ""}
              onChange={(e) => updateCertification(cert.id, { date: e.target.value || null })}
              placeholder="Date"
              className="w-24 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <button
              onClick={() => removeCertification(cert.id)}
              className="px-3 py-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
            >
              Remove
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

function AwardsPlaceholder() {
  const awards = useResumeBuilderStore((s) => s.content.awards);
  const addAward = useResumeBuilderStore((s) => s.addAward);
  const removeAward = useResumeBuilderStore((s) => s.removeAward);
  const updateAward = useResumeBuilderStore((s) => s.updateAward);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Awards</h3>
        <button
          onClick={() => addAward({ title: "", issuer: "", date: null, description: null })}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          <PlusCircle className="h-4 w-4" />
          Add
        </button>
      </div>
      {awards.map((award) => (
        <div key={award.id} className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg space-y-2">
          <input
            type="text"
            value={award.title}
            onChange={(e) => updateAward(award.id, { title: e.target.value })}
            placeholder="Award title"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
          <div className="flex gap-2">
            <input
              type="text"
              value={award.issuer}
              onChange={(e) => updateAward(award.id, { issuer: e.target.value })}
              placeholder="Issuer"
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <input
              type="text"
              value={award.date || ""}
              onChange={(e) => updateAward(award.id, { date: e.target.value || null })}
              placeholder="Date"
              className="w-24 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            />
            <button
              onClick={() => removeAward(award.id)}
              className="px-3 py-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
            >
              Remove
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

function LanguagesPlaceholder() {
  const languages = useResumeBuilderStore((s) => s.content.languages);
  const addLanguage = useResumeBuilderStore((s) => s.addLanguage);
  const removeLanguage = useResumeBuilderStore((s) => s.removeLanguage);
  const updateLanguage = useResumeBuilderStore((s) => s.updateLanguage);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Languages</h3>
        <button
          onClick={() => addLanguage({ language: "", proficiency: "conversational" })}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          <PlusCircle className="h-4 w-4" />
          Add
        </button>
      </div>
      {languages.map((lang) => (
        <div key={lang.id} className="flex gap-2 items-center">
          <input
            type="text"
            value={lang.language}
            onChange={(e) => updateLanguage(lang.id, { language: e.target.value })}
            placeholder="Language"
            className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
          <select
            value={lang.proficiency}
            onChange={(e) => updateLanguage(lang.id, { proficiency: e.target.value as "native" | "fluent" | "conversational" | "basic" })}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          >
            <option value="native">Native</option>
            <option value="fluent">Fluent</option>
            <option value="conversational">Conversational</option>
            <option value="basic">Basic</option>
          </select>
          <button
            onClick={() => removeLanguage(lang.id)}
            className="px-3 py-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
          >
            Remove
          </button>
        </div>
      ))}
    </div>
  );
}

export function EditorPanel() {
  const activeSection = useResumeBuilderStore((s) => s.activeSection);
  const setActiveSection = useResumeBuilderStore((s) => s.setActiveSection);

  const ActiveComponent = SECTIONS.find((s) => s.key === activeSection)?.component;

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
      {/* Section Navigation */}
      <div className="flex-shrink-0 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-x-auto">
        <nav className="flex min-w-max px-4 py-2 gap-1">
          {SECTIONS.map((section) => (
            <button
              key={section.key}
              onClick={() => setActiveSection(section.key)}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
                activeSection === section.key
                  ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
                  : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
              }`}
            >
              {section.icon}
              {section.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Section Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {ActiveComponent && <ActiveComponent />}
      </div>
    </div>
  );
}
