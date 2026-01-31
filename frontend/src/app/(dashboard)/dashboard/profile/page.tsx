"use client";

import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Upload, FileText, Loader2, Check } from "lucide-react";

// #region agent log
const debugLog = (location: string, message: string, data: Record<string, unknown>) => {
  fetch('http://127.0.0.1:7242/ingest/478687fd-7ff3-4069-9a5d-c1e34f5138df',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location,message,data,timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H4'})}).catch(()=>{});
};
// #endregion

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
  const [fullName, setFullName] = useState("");
  const [headline, setHeadline] = useState("");
  const [location, setLocation] = useState("");
  const [uploading, setUploading] = useState(false);
  const [resumeFile, setResumeFile] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  // Fetch existing profile data
  const { data: profile, isLoading: profileLoading, error: profileError } = useQuery<ProfileData>({
    queryKey: ["profile"],
    queryFn: async () => {
      const token = localStorage.getItem("ApplyBots_access_token");
      // #region agent log
      debugLog('profile/page.tsx:fetch', 'Fetching profile', { hasToken: !!token });
      // #endregion
      const response = await fetch("/api/v1/profile", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        // #region agent log
        debugLog('profile/page.tsx:fetchError', 'Profile fetch failed', { status: response.status });
        // #endregion
        throw new Error("Failed to fetch profile");
      }
      return response.json();
    },
  });

  // Populate form when profile loads
  useEffect(() => {
    // #region agent log
    debugLog('profile/page.tsx:effect', 'Profile data effect', { 
      profileLoaded: !!profile, 
      fullName: profile?.full_name,
      headline: profile?.headline,
      location: profile?.location 
    });
    // #endregion
    if (profile) {
      setFullName(profile.full_name || "");
      setHeadline(profile.headline || "");
      setLocation(profile.location || "");
    }
  }, [profile]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);

    try {
      const token = localStorage.getItem("ApplyBots_access_token");
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/api/v1/profile/resumes", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      if (response.ok) {
        setResumeFile(file.name);
      }
    } catch (error) {
      console.error("Upload failed:", error);
    } finally {
      setUploading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);

    try {
      const token = localStorage.getItem("ApplyBots_access_token");
      await fetch("/api/v1/profile", {
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

      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (error) {
      console.error("Save failed:", error);
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
            disabled={uploading}
          />

          {resumeFile ? (
            <div className="flex items-center justify-center gap-3">
              <FileText className="w-8 h-8 text-primary-400" />
              <span className="text-neutral-300">{resumeFile}</span>
              <Check className="w-5 h-5 text-success-500" />
            </div>
          ) : uploading ? (
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
              <span className="text-neutral-400">Uploading...</span>
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
