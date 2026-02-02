/**
 * Editor panel with section navigation and drag-and-drop reordering.
 */

"use client";

import { useMemo, useEffect } from "react";
import { useResumeBuilderStore, type SectionKey } from "@/stores/resume-builder-store";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  horizontalListSortingStrategy,
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
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
  GripVertical,
  Users,
  Tag,
} from "lucide-react";
import {
  ContactSection,
  SummarySection,
  ExperienceSection,
  EducationSection,
  SkillsSection,
  SoftSkillsSection,
  CustomSkillsSection,
  ProjectsSection,
} from "./sections";

// Section configuration
const SECTION_CONFIG: Record<
  SectionKey,
  {
    label: string;
    icon: React.ReactNode;
    component: React.ComponentType;
  }
> = {
  contact: { label: "Contact", icon: <User className="h-4 w-4" />, component: ContactSection },
  summary: { label: "Summary", icon: <FileText className="h-4 w-4" />, component: SummarySection },
  experience: { label: "Experience", icon: <Briefcase className="h-4 w-4" />, component: ExperienceSection },
  education: { label: "Education", icon: <GraduationCap className="h-4 w-4" />, component: EducationSection },
  skills: { label: "Technical Skills", icon: <Wrench className="h-4 w-4" />, component: SkillsSection },
  softSkills: { label: "Soft Skills", icon: <Users className="h-4 w-4" />, component: SoftSkillsSection },
  customSkills: { label: "Custom Skills", icon: <Tag className="h-4 w-4" />, component: CustomSkillsSection },
  projects: { label: "Projects", icon: <FolderGit2 className="h-4 w-4" />, component: ProjectsSection },
  certifications: { label: "Certifications", icon: <Award className="h-4 w-4" />, component: CertificationsPlaceholder },
  awards: { label: "Awards", icon: <Medal className="h-4 w-4" />, component: AwardsPlaceholder },
  languages: { label: "Languages", icon: <Languages className="h-4 w-4" />, component: LanguagesPlaceholder },
  custom: { label: "Custom", icon: <PlusCircle className="h-4 w-4" />, component: CustomSectionPlaceholder },
};

// Default section order
const DEFAULT_SECTION_ORDER: SectionKey[] = [
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

// Sortable tab component
interface SortableTabProps {
  id: SectionKey;
  isActive: boolean;
  onClick: () => void;
  label: string;
  icon: React.ReactNode;
}

function SortableTab({ id, isActive, onClick, label, icon }: SortableTabProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    zIndex: isDragging ? 10 : undefined,
    opacity: isDragging ? 0.8 : undefined,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-1 px-2 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap select-none ${
        isActive
          ? "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300"
          : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
      } ${isDragging ? "shadow-lg ring-2 ring-blue-400" : ""}`}
    >
      {/* Drag handle */}
      <button
        {...attributes}
        {...listeners}
        className="p-0.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 cursor-grab active:cursor-grabbing"
        title="Drag to reorder"
      >
        <GripVertical className="h-3 w-3" />
      </button>
      {/* Click area */}
      <button
        onClick={onClick}
        className="flex items-center gap-1.5"
      >
        {icon}
        {label}
      </button>
    </div>
  );
}

function CertificationsPlaceholder() {
  const certifications = useResumeBuilderStore((s) => s.content.certifications);
  const addCertification = useResumeBuilderStore((s) => s.addCertification);
  const removeCertification = useResumeBuilderStore((s) => s.removeCertification);
  const updateCertification = useResumeBuilderStore((s) => s.updateCertification);
  // #region agent log
  useEffect(() => {
    fetch('http://127.0.0.1:7242/ingest/478687fd-7ff3-4069-9a5d-c1e34f5138df',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'EditorPanel.tsx:140',message:'CertificationsPlaceholder render',data:{certificationCount:certifications.length,certificationIds:certifications.map(c=>c.id),certificationNames:certifications.map(c=>c.name)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A,C'})}).catch(()=>{});
  }, [certifications]);
  // #endregion

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
      {certifications.length === 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400 py-4 text-center">
          No certifications added yet
        </p>
      )}
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
          <input
            type="url"
            value={cert.url || ""}
            onChange={(e) => updateCertification(cert.id, { url: e.target.value || null })}
            placeholder="Certificate link (URL)"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          />
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
      {awards.length === 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400 py-4 text-center">
          No awards added yet
        </p>
      )}
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
      {languages.length === 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400 py-4 text-center">
          No languages added yet
        </p>
      )}
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

function CustomSectionPlaceholder() {
  const customSections = useResumeBuilderStore((s) => s.content.customSections);
  const addCustomSection = useResumeBuilderStore((s) => s.addCustomSection);
  const updateCustomSection = useResumeBuilderStore((s) => s.updateCustomSection);
  const removeCustomSection = useResumeBuilderStore((s) => s.removeCustomSection);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Custom Sections</h3>
        <button
          onClick={() => addCustomSection("New Section")}
          className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          <PlusCircle className="h-4 w-4" />
          Add Section
        </button>
      </div>
      {customSections.length === 0 && (
        <p className="text-sm text-gray-500 dark:text-gray-400 py-4 text-center">
          No custom sections added yet
        </p>
      )}
      {customSections.map((section) => (
        <div key={section.id} className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg space-y-3">
          <div className="flex gap-2">
            <input
              type="text"
              value={section.title}
              onChange={(e) => updateCustomSection(section.id, { title: e.target.value })}
              placeholder="Section Title"
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-medium"
            />
            <button
              onClick={() => removeCustomSection(section.id)}
              className="px-3 py-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
            >
              Remove
            </button>
          </div>
          <textarea
            value={section.items.join("\n")}
            onChange={(e) => updateCustomSection(section.id, { items: e.target.value.split("\n").filter(Boolean) })}
            placeholder="Add items (one per line)"
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm"
          />
        </div>
      ))}
    </div>
  );
}

export function EditorPanel() {
  const activeSection = useResumeBuilderStore((s) => s.activeSection);
  const setActiveSection = useResumeBuilderStore((s) => s.setActiveSection);
  const sectionOrder = useResumeBuilderStore((s) => s.content.sectionOrder);
  const updateSectionOrder = useResumeBuilderStore((s) => s.updateSectionOrder);
  const customSkillsHeader = useResumeBuilderStore((s) => s.content.skills.customSkillsHeader || "Custom Skills");

  // Ensure section order is valid
  const orderedSections = useMemo(() => {
    const order = sectionOrder && sectionOrder.length > 0 
      ? sectionOrder as SectionKey[]
      : DEFAULT_SECTION_ORDER;
    return order.filter((key) => key in SECTION_CONFIG);
  }, [sectionOrder]);

  // Get dynamic label for customSkills
  const getSectionLabel = (key: SectionKey): string => {
    if (key === "customSkills") {
      return customSkillsHeader;
    }
    return SECTION_CONFIG[key]?.label || key;
  };

  // DnD sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 5,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Handle drag end
  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = orderedSections.indexOf(active.id as SectionKey);
      const newIndex = orderedSections.indexOf(over.id as SectionKey);
      const newOrder = arrayMove(orderedSections, oldIndex, newIndex);
      updateSectionOrder(newOrder);
    }
  };

  const ActiveComponent = SECTION_CONFIG[activeSection]?.component;

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
      {/* Section Navigation with Drag & Drop */}
      <div className="flex-shrink-0 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-x-auto">
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={orderedSections}
            strategy={horizontalListSortingStrategy}
          >
            <nav className="flex min-w-max px-4 py-2 gap-1">
              {orderedSections.map((sectionKey) => {
                const config = SECTION_CONFIG[sectionKey];
                if (!config) return null;
                return (
                  <SortableTab
                    key={sectionKey}
                    id={sectionKey}
                    isActive={activeSection === sectionKey}
                    onClick={() => setActiveSection(sectionKey)}
                    label={getSectionLabel(sectionKey)}
                    icon={config.icon}
                  />
                );
              })}
            </nav>
          </SortableContext>
        </DndContext>
      </div>

      {/* Section Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {ActiveComponent && <ActiveComponent />}
      </div>
    </div>
  );
}
