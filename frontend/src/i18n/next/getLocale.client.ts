"use client";

/**
 * Client-side locale detection for Next.js.
 *
 * Detects the user's preferred locale from:
 * 1. Cookie (NEXT_LOCALE)
 * 2. Navigator language
 * 3. DEFAULT_LOCALE fallback
 *
 * This module is safe to import in client components.
 */

import type { Locale } from "../core/types";
import { DEFAULT_LOCALE, SUPPORTED_LOCALES, LOCALE_COOKIE_NAME } from "../config";

// ---------------------------------------------------------------------------
// Client-Side Locale Detection
// ---------------------------------------------------------------------------

/**
 * Type guard to check if a string is a valid supported locale.
 */
function isValidLocale(value: string | undefined | null): value is Locale {
  return !!value && (SUPPORTED_LOCALES as readonly string[]).includes(value);
}

/**
 * Detects the current locale from client context.
 *
 * Priority order:
 * 1. Cookie (user's explicit preference)
 * 2. Navigator language (browser preference)
 * 3. DEFAULT_LOCALE fallback
 *
 * @returns The detected locale
 *
 * @example
 * // In a client component
 * const locale = getLocaleClient();
 */
export function getLocaleClient(): Locale {
  // Try to get locale from cookie first (user's explicit choice)
  if (typeof document !== "undefined") {
    const cookieRegex = new RegExp(`(?:^|;\\s*)${LOCALE_COOKIE_NAME}=([^;]+)`);
    const match = document.cookie.match(cookieRegex);
    const value = match?.[1] ? decodeURIComponent(match[1]) : null;
    if (isValidLocale(value)) {
      return value;
    }
  }

  // Try navigator language
  if (typeof navigator !== "undefined") {
    const navLang = navigator.language;
    // Try exact match first
    if (isValidLocale(navLang)) {
      return navLang;
    }
    // Try base language (e.g., "en-US" -> "en")
    const twoChar = navLang?.slice(0, 2);
    if (isValidLocale(twoChar)) {
      return twoChar;
    }
  }

  // Final fallback
  return DEFAULT_LOCALE;
}
