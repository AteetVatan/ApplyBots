/**
 * Contact information section editor.
 */

"use client";

import { useResumeBuilderStore } from "@/stores/resume-builder-store";
import { User, Mail, Phone, MapPin, Linkedin, Globe, Github, Image as ImageIcon, X, PlusCircle, Link as LinkIcon } from "lucide-react";
import { useRef, useState } from "react";

export function ContactSection() {
  const content = useResumeBuilderStore((s) => s.content);
  const updateContact = useResumeBuilderStore((s) => s.updateContact);
  const addCustomLink = useResumeBuilderStore((s) => s.addCustomLink);
  const updateCustomLink = useResumeBuilderStore((s) => s.updateCustomLink);
  const removeCustomLink = useResumeBuilderStore((s) => s.removeCustomLink);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith("image/")) {
      alert("Please select an image file");
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert("Image size must be less than 5MB");
      return;
    }

    setIsUploading(true);
    try {
      // Convert to base64 data URL for immediate preview
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result as string;
        updateContact({ profilePictureUrl: base64String });
        setIsUploading(false);
      };
      reader.onerror = () => {
        alert("Failed to read image file");
        setIsUploading(false);
      };
      reader.readAsDataURL(file);
    } catch (error) {
      alert("Failed to upload image");
      setIsUploading(false);
    }
  };

  const handleRemoveImage = () => {
    updateContact({ profilePictureUrl: null });
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
        Contact Information
      </h3>

      {/* Profile Picture */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Profile Picture
        </label>
        {content.profilePictureUrl ? (
          <div className="relative inline-block">
            <img
              src={content.profilePictureUrl}
              alt="Profile"
              className="w-32 h-32 rounded-lg border-2 border-gray-300 dark:border-gray-600 object-cover"
            />
            <button
              onClick={handleRemoveImage}
              className="absolute -top-2 -right-2 p-1 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
              title="Remove image"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <div>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              disabled={isUploading}
              className="hidden"
              id="profile-picture-upload"
            />
            <label
              htmlFor="profile-picture-upload"
              className={`flex items-center gap-2 px-4 py-2 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors ${
                isUploading ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              <ImageIcon className="h-5 w-5 text-gray-400" />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {isUploading ? "Uploading..." : "Upload Profile Picture"}
              </span>
            </label>
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Max size: 5MB. Recommended: Square image, 200x200px or larger
            </p>
          </div>
        )}
      </div>

      {/* Full Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Full Name *
        </label>
        <div className="relative">
          <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={content.fullName}
            onChange={(e) => updateContact({ fullName: e.target.value })}
            placeholder="John Doe"
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Email */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Email *
        </label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="email"
            value={content.email}
            onChange={(e) => updateContact({ email: e.target.value })}
            placeholder="john.doe@example.com"
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Phone */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Phone
        </label>
        <div className="relative">
          <Phone className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="tel"
            value={content.phone || ""}
            onChange={(e) => updateContact({ phone: e.target.value || null })}
            placeholder="+1 (555) 123-4567"
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Location */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Location
        </label>
        <div className="relative">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={content.location || ""}
            onChange={(e) => updateContact({ location: e.target.value || null })}
            placeholder="San Francisco, CA"
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Links Section */}
      <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
          Social Links
        </h4>

        {/* LinkedIn */}
        <div className="mb-3">
          <div className="relative">
            <Linkedin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="url"
              value={content.linkedinUrl || ""}
              onChange={(e) => updateContact({ linkedinUrl: e.target.value || null })}
              placeholder="https://linkedin.com/in/johndoe"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* GitHub */}
        <div className="mb-3">
          <div className="relative">
            <Github className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="url"
              value={content.githubUrl || ""}
              onChange={(e) => updateContact({ githubUrl: e.target.value || null })}
              placeholder="https://github.com/johndoe"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Portfolio */}
        <div className="mb-3">
          <div className="relative">
            <Globe className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="url"
              value={content.portfolioUrl || ""}
              onChange={(e) => updateContact({ portfolioUrl: e.target.value || null })}
              placeholder="https://johndoe.dev"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Custom Links Section */}
      <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Custom Links
          </h4>
          <button
            onClick={() => addCustomLink({ label: "", url: "" })}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <PlusCircle className="h-4 w-4" />
            Add Link
          </button>
        </div>

        {(!content.customLinks || content.customLinks.length === 0) ? (
          <p className="text-xs text-gray-500 dark:text-gray-400 italic">
            No custom links added. Click "Add Link" to add custom links like Twitter, Medium, Blog, etc.
          </p>
        ) : (
          <div className="space-y-3">
            {content.customLinks.map((link) => (
              <div key={link.id} className="flex gap-2 items-start">
                <div className="flex-1 flex gap-2">
                  <div className="flex-1">
                    <input
                      type="text"
                      value={link.label}
                      onChange={(e) => updateCustomLink(link.id, { label: e.target.value })}
                      placeholder="Label (e.g., Twitter, Blog)"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    />
                  </div>
                  <div className="flex-1 relative">
                    <LinkIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <input
                      type="url"
                      value={link.url}
                      onChange={(e) => updateCustomLink(link.id, { url: e.target.value })}
                      placeholder="https://example.com"
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    />
                  </div>
                </div>
                <button
                  onClick={() => removeCustomLink(link.id)}
                  className="px-3 py-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  title="Remove link"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
