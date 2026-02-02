/**
 * Template Settings panel for customizing resume appearance.
 *
 * Features:
 * - Primary color picker
 * - Font family selector
 * - Font size scale
 * - Spacing density
 * - Page size (A4/Letter)
 */

"use client";

import { useState } from "react";
import { useResumeBuilderStore, type ThemeSettings } from "@/stores/resume-builder-store";
import {
  X,
  Palette,
  Type,
  Maximize2,
  FileText,
  RotateCcw,
  Check,
} from "lucide-react";

// Color presets
const COLOR_PRESETS = [
  { name: "Blue", value: "#3b82f6" },
  { name: "Purple", value: "#8b5cf6" },
  { name: "Pink", value: "#ec4899" },
  { name: "Red", value: "#ef4444" },
  { name: "Orange", value: "#f97316" },
  { name: "Yellow", value: "#eab308" },
  { name: "Green", value: "#22c55e" },
  { name: "Teal", value: "#14b8a6" },
  { name: "Cyan", value: "#06b6d4" },
  { name: "Indigo", value: "#6366f1" },
  { name: "Gray", value: "#6b7280" },
  { name: "Slate", value: "#475569" },
];

// Font families
const FONT_FAMILIES = [
  { name: "Inter", value: "Inter", preview: "Modern & Clean" },
  { name: "Georgia", value: "Georgia", preview: "Classic Serif" },
  { name: "Merriweather", value: "Merriweather", preview: "Elegant Serif" },
  { name: "Roboto", value: "Roboto", preview: "Professional" },
  { name: "Open Sans", value: "Open Sans", preview: "Friendly" },
  { name: "Lato", value: "Lato", preview: "Contemporary" },
  { name: "Montserrat", value: "Montserrat", preview: "Bold & Modern" },
  { name: "Source Sans Pro", value: "Source Sans Pro", preview: "Technical" },
];

// Font sizes
const FONT_SIZES: { name: string; value: ThemeSettings["fontSize"]; description: string }[] = [
  { name: "Small", value: "small", description: "More content, compact" },
  { name: "Medium", value: "medium", description: "Balanced readability" },
  { name: "Large", value: "large", description: "Better readability" },
];

// Spacing options
const SPACING_OPTIONS: { name: string; value: ThemeSettings["spacing"]; description: string }[] = [
  { name: "Compact", value: "compact", description: "More content per page" },
  { name: "Normal", value: "normal", description: "Standard spacing" },
  { name: "Spacious", value: "spacious", description: "More breathing room" },
];

// Page sizes
const PAGE_SIZES: { name: string; value: ThemeSettings["pageSize"]; dimensions: string }[] = [
  { name: "Letter", value: "letter", dimensions: "8.5\" × 11\" (US)" },
  { name: "A4", value: "a4", dimensions: "210mm × 297mm (International)" },
];

interface TemplateSettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

export function TemplateSettings({ isOpen, onClose }: TemplateSettingsProps) {
  const themeSettings = useResumeBuilderStore((s) => s.themeSettings);
  const setThemeSettings = useResumeBuilderStore((s) => s.setThemeSettings);
  const resetThemeSettings = useResumeBuilderStore((s) => s.resetThemeSettings);

  const [customColor, setCustomColor] = useState(themeSettings.primaryColor);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-white dark:bg-gray-900 rounded-xl shadow-2xl max-w-lg w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <Palette className="h-5 w-5 text-blue-500" />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Template Settings
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={resetThemeSettings}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
              title="Reset to defaults"
            >
              <RotateCcw className="h-4 w-4" />
              Reset
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {/* Primary Color */}
          <section>
            <h3 className="flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white mb-3">
              <Palette className="h-4 w-4 text-gray-500" />
              Primary Color
            </h3>
            <div className="grid grid-cols-6 gap-2 mb-3">
              {COLOR_PRESETS.map((color) => (
                <button
                  key={color.value}
                  onClick={() => {
                    setThemeSettings({ primaryColor: color.value });
                    setCustomColor(color.value);
                  }}
                  className={`relative w-10 h-10 rounded-lg transition-transform hover:scale-110 ${
                    themeSettings.primaryColor === color.value
                      ? "ring-2 ring-offset-2 ring-blue-500"
                      : ""
                  }`}
                  style={{ backgroundColor: color.value }}
                  title={color.name}
                >
                  {themeSettings.primaryColor === color.value && (
                    <Check className="absolute inset-0 m-auto h-5 w-5 text-white drop-shadow" />
                  )}
                </button>
              ))}
            </div>
            <div className="flex items-center gap-2">
              <label className="text-xs text-gray-500 dark:text-gray-400">Custom:</label>
              <input
                type="color"
                value={customColor}
                onChange={(e) => {
                  setCustomColor(e.target.value);
                  setThemeSettings({ primaryColor: e.target.value });
                }}
                className="w-8 h-8 rounded cursor-pointer"
              />
              <input
                type="text"
                value={customColor}
                onChange={(e) => {
                  setCustomColor(e.target.value);
                  if (/^#[0-9A-Fa-f]{6}$/.test(e.target.value)) {
                    setThemeSettings({ primaryColor: e.target.value });
                  }
                }}
                className="flex-1 px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                placeholder="#3b82f6"
              />
            </div>
          </section>

          {/* Font Family */}
          <section>
            <h3 className="flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white mb-3">
              <Type className="h-4 w-4 text-gray-500" />
              Font Family
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {FONT_FAMILIES.map((font) => (
                <button
                  key={font.value}
                  onClick={() => setThemeSettings({ fontFamily: font.value })}
                  className={`p-3 text-left rounded-lg border transition-colors ${
                    themeSettings.fontFamily === font.value
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                  }`}
                >
                  <div
                    className="text-sm font-medium text-gray-900 dark:text-white"
                    style={{ fontFamily: font.value }}
                  >
                    {font.name}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {font.preview}
                  </div>
                </button>
              ))}
            </div>
          </section>

          {/* Font Size */}
          <section>
            <h3 className="flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white mb-3">
              <Type className="h-4 w-4 text-gray-500" />
              Font Size
            </h3>
            <div className="flex gap-2">
              {FONT_SIZES.map((size) => (
                <button
                  key={size.value}
                  onClick={() => setThemeSettings({ fontSize: size.value })}
                  className={`flex-1 p-3 text-center rounded-lg border transition-colors ${
                    themeSettings.fontSize === size.value
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                  }`}
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {size.name}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {size.description}
                  </div>
                </button>
              ))}
            </div>
          </section>

          {/* Spacing */}
          <section>
            <h3 className="flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white mb-3">
              <Maximize2 className="h-4 w-4 text-gray-500" />
              Spacing
            </h3>
            <div className="flex gap-2">
              {SPACING_OPTIONS.map((spacing) => (
                <button
                  key={spacing.value}
                  onClick={() => setThemeSettings({ spacing: spacing.value })}
                  className={`flex-1 p-3 text-center rounded-lg border transition-colors ${
                    themeSettings.spacing === spacing.value
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                  }`}
                >
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {spacing.name}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {spacing.description}
                  </div>
                </button>
              ))}
            </div>
          </section>

          {/* Page Size */}
          <section>
            <h3 className="flex items-center gap-2 text-sm font-medium text-gray-900 dark:text-white mb-3">
              <FileText className="h-4 w-4 text-gray-500" />
              Page Size
            </h3>
            <div className="flex gap-2">
              {PAGE_SIZES.map((pageSize) => (
                <button
                  key={pageSize.value}
                  onClick={() => setThemeSettings({ pageSize: pageSize.value })}
                  className={`flex-1 p-4 text-center rounded-lg border transition-colors ${
                    themeSettings.pageSize === pageSize.value
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                  }`}
                >
                  <div className="text-base font-medium text-gray-900 dark:text-white">
                    {pageSize.name}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {pageSize.dimensions}
                  </div>
                </button>
              ))}
            </div>
          </section>
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <button
            onClick={onClose}
            className="w-full py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}

// Export a button to open settings
export function TemplateSettingsButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
      >
        <Palette className="h-4 w-4 text-gray-500" />
        <span className="text-gray-700 dark:text-gray-300">Settings</span>
      </button>
      <TemplateSettings isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
}
