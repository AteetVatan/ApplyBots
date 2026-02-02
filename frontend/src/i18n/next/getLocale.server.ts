import "server-only";

/**
 * Server-side locale detection for Next.js.
 *
 * Detects the user's preferred locale from:
 * 1. Explicit parameter (if passed)
 * 2. Cookie (NEXT_LOCALE)
 * 3. Accept-Language header
 * 4. DEFAULT_LOCALE fallback
 *
 * This module uses Next.js server APIs (cookies, headers) and should
 * only be imported in server components or route handlers.
 */

import { cookies, headers } from "next/headers";
import type { Locale } from "../core/types";
import {
  DEFAULT_LOCALE,
  LOCALE_COOKIE_NAME,
  validateLocale,
  isValidLocale,
} from "../config";

// ---------------------------------------------------------------------------
// Server-Side Locale Detection
// ---------------------------------------------------------------------------

/**
 * Parses the Accept-Language header and returns the best matching locale.
 * 
 * This is a server-only function moved from config.ts to break the
 * shared dependency chain between client and server code.
 *
 * @param acceptLanguage - The Accept-Language header value
 * @returns The best matching supported locale or undefined
 */
function parseAcceptLanguage(
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

/**
 * Detects the current locale from server context.
 *
 * Priority order:
 * 1. Cookie (user's explicit preference)
 * 2. Accept-Language header (browser preference)
 * 3. DEFAULT_LOCALE fallback
 *
 * @returns The detected locale
 *
 * @example
 * // In a server component or route handler
 * const locale = await getLocale();
 * const t = createTranslator(locale);
 */
export async function getLocale(): Promise<Locale> {
  // Try to get locale from cookie first (user's explicit choice)
  const cookieStore = await cookies();
  const localeCookie = cookieStore.get(LOCALE_COOKIE_NAME);

  if (localeCookie?.value) {
    const validated = validateLocale(localeCookie.value);
    if (validated === localeCookie.value) {
      return validated;
    }
    // Cookie contains invalid locale - will fall through to other methods
  }

  // Try Accept-Language header
  const headerStore = await headers();
  const acceptLanguage = headerStore.get("accept-language");
  const headerLocale = parseAcceptLanguage(acceptLanguage);

  if (headerLocale) {
    return headerLocale;
  }

  // Final fallback
  return DEFAULT_LOCALE;
}

/**
 * Gets the locale synchronously if already known.
 * Useful when locale has been passed as a prop.
 *
 * @param locale - The locale string to validate
 * @returns A valid Locale
 */
export function getLocaleSync(locale: string | undefined): Locale {
  return validateLocale(locale);
}
