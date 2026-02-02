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
export const SUPPORTED_LOCALES: readonly Locale[] = ["en", "es", "fr", "de"] as const;

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

// Note: parseAcceptLanguage has been moved to getLocale.ts (server-only)
// to break the shared dependency chain between client and server code.
