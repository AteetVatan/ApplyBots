/**
 * Share button component for generating and managing shareable resume links.
 *
 * Features:
 * - Generate unique share URL
 * - Toggle public/private
 * - Copy link to clipboard
 * - QR code generation (optional)
 */

"use client";

import { useState } from "react";
import { useResumeBuilderStore } from "@/stores/resume-builder-store";
import {
  Share2,
  Link2,
  Copy,
  Check,
  Globe,
  Lock,
  X,
  ExternalLink,
  Loader2,
} from "lucide-react";

// Simple ID generation for share links
function generateShareId(): string {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < 12; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ShareModal({ isOpen, onClose }: ShareModalProps) {
  const shareSettings = useResumeBuilderStore((s) => s.shareSettings);
  const setShareSettings = useResumeBuilderStore((s) => s.setShareSettings);
  const draftName = useResumeBuilderStore((s) => s.draftName);

  const [copied, setCopied] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  if (!isOpen) return null;

  const shareUrl = shareSettings.shareId
    ? `${window.location.origin}/resume/${shareSettings.shareId}`
    : null;

  const handleGenerateLink = async () => {
    setIsGenerating(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));
    
    const newShareId = generateShareId();
    setShareSettings({
      isPublic: true,
      shareId: newShareId,
      shareUrl: `${window.location.origin}/resume/${newShareId}`,
    });
    setIsGenerating(false);
  };

  const handleTogglePublic = () => {
    setShareSettings({ isPublic: !shareSettings.isPublic });
  };

  const handleCopyLink = async () => {
    if (!shareUrl) return;
    
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = shareUrl;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRemoveLink = () => {
    setShareSettings({
      isPublic: false,
      shareId: null,
      shareUrl: null,
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-900 rounded-xl shadow-2xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <Share2 className="h-5 w-5 text-blue-500" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Share Resume
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Resume name */}
          <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <p className="text-sm text-gray-500 dark:text-gray-400">Sharing</p>
            <p className="font-medium text-gray-900 dark:text-white">{draftName}</p>
          </div>

          {/* No link generated yet */}
          {!shareSettings.shareId && (
            <div className="text-center py-6">
              <div className="mx-auto w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mb-3">
                <Link2 className="h-6 w-6 text-blue-500" />
              </div>
              <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                No Share Link Yet
              </h3>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                Generate a link to share your resume with anyone
              </p>
              <button
                onClick={handleGenerateLink}
                disabled={isGenerating}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 transition-colors"
              >
                {isGenerating ? (
                  <span className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Generating...
                  </span>
                ) : (
                  "Generate Share Link"
                )}
              </button>
            </div>
          )}

          {/* Link exists */}
          {shareSettings.shareId && (
            <>
              {/* Visibility toggle */}
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center gap-3">
                  {shareSettings.isPublic ? (
                    <Globe className="h-5 w-5 text-green-500" />
                  ) : (
                    <Lock className="h-5 w-5 text-gray-500" />
                  )}
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {shareSettings.isPublic ? "Public" : "Private"}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {shareSettings.isPublic
                        ? "Anyone with the link can view"
                        : "Link is disabled"}
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleTogglePublic}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    shareSettings.isPublic
                      ? "bg-blue-500"
                      : "bg-gray-300 dark:bg-gray-600"
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      shareSettings.isPublic ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
              </div>

              {/* Share link */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Share Link
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={shareUrl || ""}
                    readOnly
                    className="flex-1 px-3 py-2 text-sm bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-700 dark:text-gray-300"
                  />
                  <button
                    onClick={handleCopyLink}
                    className={`p-2 rounded-lg transition-colors ${
                      copied
                        ? "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400"
                        : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
                    }`}
                    title="Copy link"
                  >
                    {copied ? (
                      <Check className="h-5 w-5" />
                    ) : (
                      <Copy className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <a
                  href={shareUrl || "#"}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-1 flex items-center justify-center gap-2 py-2 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
                >
                  <ExternalLink className="h-4 w-4" />
                  Open Preview
                </a>
                <button
                  onClick={handleRemoveLink}
                  className="flex-1 py-2 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                >
                  Remove Link
                </button>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 rounded-b-xl">
          <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Share links use a unique URL that doesn't reveal your identity.
          </p>
        </div>
      </div>
    </div>
  );
}

// Button to open share modal
export function ShareButton() {
  const [isOpen, setIsOpen] = useState(false);
  const shareSettings = useResumeBuilderStore((s) => s.shareSettings);

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className={`flex items-center gap-2 px-3 py-1.5 text-sm rounded-lg transition-colors ${
          shareSettings.isPublic
            ? "bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400"
            : "border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
        }`}
      >
        <Share2 className="h-4 w-4" />
        {shareSettings.isPublic ? "Shared" : "Share"}
      </button>
      <ShareModal isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
}
