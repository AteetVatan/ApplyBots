"use client";

/**
 * ResumeSelector component for CareerKit.
 * Displays available uploaded resumes and builder drafts for selection.
 */

import { useCareerKitResumes, ResumeSource, ResumeOption } from "@/hooks/useCareerKit";
import { FileText, Star, Clock, Loader2, CheckCircle } from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";

interface ResumeSelectorProps {
  onSelect: (source: ResumeSource) => void;
  selectedId?: string;
  isLoading?: boolean;
}

export function ResumeSelector({ onSelect, selectedId, isLoading }: ResumeSelectorProps) {
  const { data, isLoading: isLoadingResumes } = useCareerKitResumes();

  if (isLoadingResumes) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  const hasUploaded = data?.uploaded_resumes && data.uploaded_resumes.length > 0;
  const hasDrafts = data?.builder_drafts && data.builder_drafts.length > 0;

  if (!hasUploaded && !hasDrafts) {
    return (
      <div className="text-center py-12">
        <FileText className="w-12 h-12 mx-auto text-neutral-500 mb-4" />
        <h3 className="text-lg font-semibold mb-2">No Resumes Found</h3>
        <p className="text-neutral-400">
          Please upload a resume or create one in the Resume Builder first.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Uploaded Resumes */}
      {hasUploaded && (
        <section>
          <h3 className="text-sm font-semibold text-neutral-400 uppercase tracking-wide mb-3">
            Uploaded Resumes
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.uploaded_resumes.map((resume) => (
              <ResumeCard
                key={resume.id}
                resume={resume}
                isSelected={selectedId === resume.id}
                isLoading={isLoading && selectedId === resume.id}
                onSelect={() => onSelect({ source_type: "uploaded", resume_id: resume.id })}
              />
            ))}
          </div>
        </section>
      )}

      {/* Builder Drafts */}
      {hasDrafts && (
        <section>
          <h3 className="text-sm font-semibold text-neutral-400 uppercase tracking-wide mb-3">
            Resume Builder Drafts
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {data.builder_drafts.map((draft) => (
              <ResumeCard
                key={draft.id}
                resume={draft}
                isSelected={selectedId === draft.id}
                isLoading={isLoading && selectedId === draft.id}
                onSelect={() => onSelect({ source_type: "draft", resume_id: draft.id })}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

interface ResumeCardProps {
  resume: ResumeOption;
  isSelected: boolean;
  isLoading: boolean;
  onSelect: () => void;
}

function ResumeCard({ resume, isSelected, isLoading, onSelect }: ResumeCardProps) {
  return (
    <button
      onClick={onSelect}
      disabled={isLoading}
      className={`
        w-full p-4 rounded-xl border-2 text-left transition-all
        ${isSelected
          ? "border-primary-500 bg-primary-500/10"
          : "border-neutral-700 hover:border-neutral-600 bg-neutral-800/50 hover:bg-neutral-800"
        }
        ${isLoading ? "opacity-50 cursor-wait" : ""}
      `}
    >
      <div className="flex items-start gap-3">
        <div className={`
          p-2 rounded-lg
          ${isSelected ? "bg-primary-500/20 text-primary-400" : "bg-neutral-700 text-neutral-400"}
        `}>
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : isSelected ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <FileText className="w-5 h-5" />
          )}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium truncate">{resume.name}</span>
            {resume.is_primary && (
              <span className="flex items-center gap-1 text-xs text-yellow-500">
                <Star className="w-3 h-3 fill-current" />
                Primary
              </span>
            )}
          </div>

          {resume.preview && (
            <p className="text-sm text-neutral-400 truncate mb-2">
              {resume.preview}
            </p>
          )}

          <div className="flex items-center gap-2 text-xs text-neutral-500">
            <span className={`
              px-2 py-0.5 rounded-full
              ${resume.source_type === "uploaded" ? "bg-blue-500/20 text-blue-400" : "bg-purple-500/20 text-purple-400"}
            `}>
              {resume.source_type === "uploaded" ? "Uploaded" : "Builder"}
            </span>
            {resume.updated_at && (
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatRelativeTime(resume.updated_at)}
              </span>
            )}
          </div>
        </div>
      </div>
    </button>
  );
}
