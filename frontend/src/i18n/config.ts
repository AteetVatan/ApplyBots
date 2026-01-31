/**
 * i18n configuration.
 *
 * Single source of truth for locale settings, supported languages,
 * and validation utilities.
 */

import type { Locale } from "./core/types";

// ---------------------------------------------------------------------------
// Locale Configuration
// ---------------------------------------------------------------------------

/** Default locale used when no locale preference is detected */
export const DEFAULT_LOCALE: Locale = "en";

/** Array of all supported locale codes */
export const SUPPORTED_LOCALES: readonly Locale[] = ["en", "de"] as const;

/** Cookie name for storing user's locale preference */
export const LOCALE_COOKIE_NAME = "NEXT_LOCALE";

/** Maximum age for locale cookie (1 year in seconds) */
export const LOCALE_COOKIE_MAX_AGE = 60 * 60 * 24 * 365;

// ---------------------------------------------------------------------------
// Validation Utilities
// ---------------------------------------------------------------------------

/**
 * Type guard to check if a string is a valid supported locale.
 */
export function isValidLocale(value: unknown): value is Locale {
  return (
    typeof value === "string" &&
    SUPPORTED_LOCALES.includes(value as Locale)
  );
}

/**
 * Validates and returns a locale, falling back to DEFAULT_LOCALE if invalid.
 *
 * @param value - The value to validate as a locale
 * @returns A valid Locale, either the input or DEFAULT_LOCALE
 */
export function validateLocale(value: unknown): Locale {
  if (isValidLocale(value)) {
    return value;
  }
  return DEFAULT_LOCALE;
}

/**
 * Parses the Accept-Language header and returns the best matching locale.
 *
 * @param acceptLanguage - The Accept-Language header value
 * @returns The best matching supported locale or undefined
 */
export function parseAcceptLanguage(
  acceptLanguage: string | null | undefined
): Locale | undefined {
  if (!acceptLanguage) {
    return undefined;
  }

  // Parse language tags with quality values
  // e.g., "en-US,en;q=0.9,de;q=0.8" -> [{ lang: "en-US", q: 1 }, ...]
  const languages = acceptLanguage
    .split(",")
    .map((part) => {
      const [lang, qPart] = part.trim().split(";");
      const q = qPart ? parseFloat(qPart.replace("q=", "")) : 1;
      return { lang: lang.trim().toLowerCase(), q };
    })
    .sort((a, b) => b.q - a.q);

  // Find first matching supported locale
  for (const { lang } of languages) {
    // Try exact match first (e.g., "en" matches "en")
    if (isValidLocale(lang)) {
      return lang;
    }
    // Try base language (e.g., "en-US" -> "en")
    const baseLang = lang.split("-")[0];
    if (isValidLocale(baseLang)) {
      return baseLang;
    }
  }

  return undefined;
}
