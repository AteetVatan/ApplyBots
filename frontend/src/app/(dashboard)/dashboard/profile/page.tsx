"use client";

import { useState, useEffect } from "react";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { Upload, FileText, Loader2, Check, Trash2 } from "lucide-react";
import { api, type Resume } from "@/lib/api";

interface ProfileData {
  id: string;
  user_id: string;
  full_name: string | null;
  headline: string | null;
  location: string | null;
  phone: string | null;
  linkedin_url: string | null;
  portfolio_url: string | null;
}

export default function ProfilePage() {
  const queryClient = useQueryClient();
  const [fullName, setFullName] = useState("");
  const [headline, setHeadline] = useState("");
  const [location, setLocation] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Fetch existing profile data
  const { data: profile } = useQuery<ProfileData>({
    queryKey: ["profile"],
    queryFn: async () => {
      const token = localStorage.getItem("ApplyBots_access_token");
      const response = await fetch("/api/v1/profile", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error("Failed to fetch profile");
      }
      return response.json();
    },
  });

  // Fetch existing resumes
  const { data: resumeData } = useQuery({
    queryKey: ["resumes"],
    queryFn: () => api.getResumes(),
  });
  const resumes = resumeData?.items || [];

  // Populate form when profile loads
  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name || "");
      setHeadline(profile.headline || "");
      setLocation(profile.location || "");
    }
  }, [profile]);

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => api.uploadResume(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
    onError: (err: Error) => {
      // Error handling is done via mutation state
      console.error("Upload failed:", err);
    },
  });

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    uploadMutation.mutate(file);

    // Reset input
    e.target.value = "";
  };

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteResume(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
    },
    onError: (err: Error) => {
      // Error handling - could add error state if needed
      console.error("Delete failed:", err);
    },
  });

  const handleDeleteResume = async (resumeId: string) => {
    deleteMutation.mutate(resumeId);
  };

  const handleSave = async () => {
    setSaving(true);
    setSaveError(null);

    try {
      const token = localStorage.getItem("ApplyBots_access_token");
      const response = await fetch("/api/v1/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          full_name: fullName,
          headline,
          location,
        }),
      });

      if (response.ok) {
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
      } else {
        setSaveError("Failed to save. Please try again.");
      }
    } catch {
      setSaveError("Failed to save. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-display font-bold">Your Profile</h1>
        <p className="text-neutral-400">
          Complete your profile to get better job matches
        </p>
      </div>

      {/* Resume Upload */}
      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">Resume</h2>

        <div className="border-2 border-dashed border-neutral-700 rounded-xl p-8 text-center hover:border-primary-500/50 transition-colors">
          <input
            type="file"
            id="resume"
            accept=".pdf,.docx"
            onChange={handleFileUpload}
            className="hidden"
            disabled={uploadMutation.isPending}
          />

          {resumes && resumes.length > 0 ? (
            <div className="space-y-3">
              {resumes.map((resume) => (
                <div key={resume.id} className="flex items-center justify-between p-3 bg-neutral-800 rounded-lg">
                  <div className="flex items-center gap-3">
                    <FileText className="w-6 h-6 text-primary-400" />
                    <div>
                      <span className="text-neutral-300">{resume.filename}</span>
                      {resume.is_primary && (
                        <span className="ml-2 text-xs text-primary-400">(Primary)</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="w-5 h-5 text-success-500" />
                    <button
                      onClick={() => handleDeleteResume(resume.id)}
                      disabled={deleteMutation.isPending}
                      className="p-1 text-neutral-500 hover:text-red-400 transition-colors disabled:opacity-50"
                      title="Remove resume"
                    >
                      {deleteMutation.isPending ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>
              ))}
              <label htmlFor="resume" className="cursor-pointer block text-center text-sm text-primary-400 hover:text-primary-300 mt-2">
                + Upload another resume
              </label>
            </div>
          ) : uploadMutation.isPending ? (
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
              <span className="text-neutral-400">Uploading...</span>
            </div>
          ) : uploadMutation.isError ? (
            <div className="flex flex-col items-center gap-3">
              <span className="text-red-400 text-sm">Upload failed. Please try again.</span>
              <label htmlFor="resume" className="cursor-pointer text-primary-400 hover:text-primary-300 text-sm">
                Try again
              </label>
            </div>
          ) : (
            <label htmlFor="resume" className="cursor-pointer">
              <Upload className="w-12 h-12 text-neutral-600 mx-auto mb-4" />
              <p className="text-neutral-300 mb-2">
                Drop your resume here or click to browse
              </p>
              <p className="text-sm text-neutral-500">
                PDF or DOCX, max 10MB
              </p>
            </label>
          )}
        </div>
      </div>

      {/* Basic Info */}
      <div className="glass-card p-6 space-y-5">
        <h2 className="text-lg font-semibold">Basic Information</h2>

        <div>
          <label className="block text-sm font-medium mb-2">Full Name</label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full px-4 py-3 bg-neutral-800 border border-neutral-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            placeholder="John Doe"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Professional Headline</label>
          <input
            type="text"
            value={headline}
            onChange={(e) => setHeadline(e.target.value)}
            className="w-full px-4 py-3 bg-neutral-800 border border-neutral-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            placeholder="Senior Software Engineer"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Location</label>
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full px-4 py-3 bg-neutral-800 border border-neutral-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            placeholder="San Francisco, CA"
          />
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full py-3 bg-primary-600 hover:bg-primary-500 disabled:bg-primary-600/50 rounded-xl font-semibold transition-colors flex items-center justify-center gap-2"
        >
          {saving ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Saving...
            </>
          ) : saved ? (
            <>
              <Check className="w-5 h-5" />
              Saved!
            </>
          ) : (
            "Save Changes"
          )}
        </button>
      </div>
    </div>
  );
}
