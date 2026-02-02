"use client";

/**
 * Multi-resume management page.
 *
 * Standards: react_nextjs.mdc
 * - Functional components only
 * - TanStack Query for data fetching
 * - Error boundaries
 */

import { useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type Resume, type ResumeDraft } from "@/lib/api";
import { useDrafts, useDeleteDraft } from "@/hooks/useResumeDrafts";
import { useResumeBuilderStore } from "@/stores/resume-builder-store";
import {
  FileText,
  Upload,
  Trash2,
  Star,
  StarOff,
  AlertCircle,
  Loader2,
  Sparkles,
  PenLine,
  Clock,
} from "lucide-react";

export default function ResumesPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const reset = useResumeBuilderStore((state) => state.reset);

  // Fetch uploaded resumes
  const { data: resumeData, isLoading: isLoadingResumes } = useQuery({
    queryKey: ["resumes"],
    queryFn: () => api.getResumes(),
  });

  // Fetch builder drafts
  const { data: draftsData, isLoading: isLoadingDrafts } = useDrafts();
  const deleteDraftMutation = useDeleteDraft();

  const isLoading = isLoadingResumes || isLoadingDrafts;

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => api.uploadResume(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      setUploading(false);
      setError(null);
    },
    onError: (err: Error) => {
      setError(err.message);
      setUploading(false);
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteResume(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
  });

  // Set primary mutation
  const setPrimaryMutation = useMutation({
    mutationFn: (id: string) => api.setPrimaryResume(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
  });

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];
    if (!validTypes.includes(file.type)) {
      setError("Please upload a PDF or DOCX file");
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError("File size must be less than 10MB");
      return;
    }

    setUploading(true);
    setError(null);
    uploadMutation.mutate(file);

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const resumes = resumeData?.items || [];
  const drafts = draftsData?.items || [];

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          My Resumes
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Manage multiple resumes for different job applications
        </p>
      </div>

      {/* Create / Upload Section */}
      <div className="mb-8 grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Create with Builder - Primary action */}
        <button
          onClick={() => {
            // Reset store to start fresh
            reset();
            router.push("/dashboard/resumes/builder");
          }}
          className="group relative flex flex-col items-center justify-center p-8 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 transition-all shadow-lg hover:shadow-xl hover:scale-[1.02]"
        >
          <div className="absolute -top-2 -right-2 px-2 py-1 bg-yellow-400 text-yellow-900 text-xs font-bold rounded-full shadow">
            NEW
          </div>
          <div className="p-3 bg-white/20 rounded-full mb-3 group-hover:scale-110 transition-transform">
            <Sparkles className="h-8 w-8" />
          </div>
          <h3 className="text-lg font-semibold mb-1">Create with AI Builder</h3>
          <p className="text-sm text-white/80 text-center">
            Build your resume step-by-step with AI assistance
          </p>
        </button>

        {/* Upload existing resume */}
        <div
          className="border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl p-8 text-center cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors flex flex-col items-center justify-center"
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileSelect}
            className="hidden"
          />

          {uploading ? (
            <div className="flex flex-col items-center">
              <Loader2 className="h-10 w-10 text-blue-500 animate-spin mb-3" />
              <p className="text-gray-600 dark:text-gray-400">Uploading and parsing...</p>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <Upload className="h-10 w-10 text-gray-400 mb-3" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-1">
                Upload Existing Resume
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-500">
                PDF or DOCX, max 10MB
              </p>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-4 flex items-center gap-2 text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
          <AlertCircle className="h-4 w-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Resume List */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 text-gray-400 animate-spin" />
        </div>
      ) : drafts.length === 0 && resumes.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-1">
            No resumes yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Create a resume with our AI builder or upload an existing one
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Builder Drafts Section */}
          {drafts.length > 0 && (
            <div>
              <h2 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 flex items-center gap-2">
                <PenLine className="h-4 w-4" />
                Resume Builder Drafts
              </h2>
              <div className="space-y-3">
                {drafts.map((draft) => (
                  <DraftCard
                    key={draft.id}
                    draft={draft}
                    onEdit={() => router.push(`/dashboard/resumes/builder?draftId=${draft.id}`)}
                    onDelete={() => deleteDraftMutation.mutate(draft.id)}
                    isDeleting={deleteDraftMutation.isPending}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Uploaded Resumes Section */}
          {resumes.length > 0 && (
            <div>
              {drafts.length > 0 && (
                <h2 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 flex items-center gap-2">
                  <Upload className="h-4 w-4" />
                  Uploaded Resumes
                </h2>
              )}
              <div className="space-y-3">
                {resumes.map((resume) => (
                  <ResumeCard
                    key={resume.id}
                    resume={resume}
                    onSetPrimary={() => setPrimaryMutation.mutate(resume.id)}
                    onDelete={() => deleteMutation.mutate(resume.id)}
                    isDeleting={deleteMutation.isPending}
                    isSettingPrimary={setPrimaryMutation.isPending}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Usage Tips */}
      <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
        <h3 className="font-medium text-blue-900 dark:text-blue-300 mb-2">
          💡 Tips for better results
        </h3>
        <ul className="text-sm text-blue-800 dark:text-blue-400 space-y-1">
          <li>• Use a text-based PDF for accurate parsing</li>
          <li>• Create tailored resumes for different job types</li>
          <li>• Set the most relevant resume as primary</li>
          <li>• Keep your resumes under 2 pages for best results</li>
        </ul>
      </div>
    </div>
  );
}

interface ResumeCardProps {
  resume: Resume;
  onSetPrimary: () => void;
  onDelete: () => void;
  isDeleting: boolean;
  isSettingPrimary: boolean;
}

function ResumeCard({
  resume,
  onSetPrimary,
  onDelete,
  isDeleting,
  isSettingPrimary,
}: ResumeCardProps) {
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);

  const parsed = resume.parsed_data;
  const skills = parsed?.skills?.slice(0, 8) || [];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
            <FileText className="h-6 w-6 text-gray-600 dark:text-gray-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-medium text-gray-900 dark:text-white">
                {resume.filename}
              </h3>
              {resume.is_primary && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 text-xs font-medium rounded-full">
                  <Star className="h-3 w-3" />
                  Primary
                </span>
              )}
            </div>
            {parsed?.full_name && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                {parsed.full_name}
                {parsed.total_years_experience
                  ? ` • ${parsed.total_years_experience} years exp.`
                  : ""}
              </p>
            )}
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
              Uploaded {new Date(resume.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {!resume.is_primary && (
            <button
              onClick={onSetPrimary}
              disabled={isSettingPrimary}
              className="p-2 text-gray-500 hover:text-yellow-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
              title="Set as primary"
            >
              {isSettingPrimary ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <StarOff className="h-4 w-4" />
              )}
            </button>
          )}
          <button
            onClick={() => setShowConfirmDelete(true)}
            disabled={isDeleting}
            className="p-2 text-gray-500 hover:text-red-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
            title="Delete resume"
          >
            {isDeleting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      {/* Skills Preview */}
      {skills.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-500 mb-2">
            Extracted Skills
          </p>
          <div className="flex flex-wrap gap-1.5">
            {skills.map((skill, idx) => (
              <span
                key={idx}
                className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded-full"
              >
                {skill}
              </span>
            ))}
            {(parsed?.skills?.length || 0) > 8 && (
              <span className="px-2 py-0.5 text-gray-500 dark:text-gray-500 text-xs">
                +{(parsed?.skills?.length || 0) - 8} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Parsing Status */}
      {!parsed && (
        <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
          <div className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">
              Could not parse resume content. Try uploading a text-based PDF.
            </span>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      {showConfirmDelete && (
        <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
            <span className="text-sm text-red-800 dark:text-red-300">
              Delete this resume?
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setShowConfirmDelete(false)}
                className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onDelete();
                  setShowConfirmDelete(false);
                }}
                className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Draft Card Component
// =============================================================================

interface DraftCardProps {
  draft: ResumeDraft;
  onEdit: () => void;
  onDelete: () => void;
  isDeleting: boolean;
}

function DraftCard({ draft, onEdit, onDelete, isDeleting }: DraftCardProps) {
  const [showConfirmDelete, setShowConfirmDelete] = useState(false);

  const content = draft.content;
  const hasContent = content.full_name || content.work_experience?.length > 0;

  // Format date
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    return new Date(dateStr).toLocaleDateString();
  };

  return (
    <div
      className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm hover:border-purple-300 dark:hover:border-purple-700 transition-colors cursor-pointer group"
      onClick={onEdit}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/30 dark:to-pink-900/30 rounded-lg">
            <PenLine className="h-6 w-6 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-medium text-gray-900 dark:text-white group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                {draft.name}
              </h3>
              {draft.ats_score !== null && (
                <span
                  className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full ${
                    draft.ats_score >= 80
                      ? "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300"
                      : draft.ats_score >= 60
                      ? "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300"
                      : "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300"
                  }`}
                >
                  ATS: {draft.ats_score}%
                </span>
              )}
            </div>
            {hasContent ? (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                {content.full_name || "No name set"}
                {content.work_experience?.length > 0 &&
                  ` • ${content.work_experience.length} job${content.work_experience.length > 1 ? "s" : ""}`}
              </p>
            ) : (
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-0.5 italic">
                Empty draft - click to edit
              </p>
            )}
            <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-500 mt-1">
              <Clock className="h-3 w-3" />
              <span>
                {draft.updated_at
                  ? `Updated ${formatDate(draft.updated_at)}`
                  : `Created ${formatDate(draft.created_at)}`}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowConfirmDelete(true);
            }}
            disabled={isDeleting}
            className="p-2 text-gray-500 hover:text-red-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
            title="Delete draft"
          >
            {isDeleting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Trash2 className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      {/* Delete Confirmation */}
      {showConfirmDelete && (
        <div
          className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-between bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
            <span className="text-sm text-red-800 dark:text-red-300">
              Delete this draft?
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setShowConfirmDelete(false)}
                className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700 rounded"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onDelete();
                  setShowConfirmDelete(false);
                }}
                className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
