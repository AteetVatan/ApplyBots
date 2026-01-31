/**
 * Server-side translator for Next.js server components.
 *
 * Provides an async function to get a translator instance that
 * automatically detects the user's locale from server context.
 *
 * Usage in server components:
 * ```tsx
 * import { getT } from "@/i18n";
 *
 * export default async function Page() {
 *   const t = await getT();
 *   return <h1>{t("nav.home")}</h1>;
 * }
 * ```
 */

import type { Locale, TranslatorFn } from "../core/types";
import { createTranslator } from "../core/createTranslator";
import { getLocale } from "./getLocale";

// ---------------------------------------------------------------------------
// Server Translator
// ---------------------------------------------------------------------------

/**
 * Gets a translator function for server components.
 *
 * Automatically detects the locale from cookies/headers if not provided.
 * This is an async function because locale detection requires accessing
 * Next.js server APIs.
 *
 * @param locale - Optional locale override. If not provided, auto-detected.
 * @returns A type-safe translator function
 *
 * @example
 * // Auto-detect locale from request context
 * const t = await getT();
 * t("nav.home"); // "Home"
 *
 * // Override with specific locale
 * const tDe = await getT("de");
 * tDe("nav.home"); // "Startseite" (when de.ts is available)
 */
export async function getT(locale?: Locale): Promise<TranslatorFn> {
  const resolvedLocale = locale ?? (await getLocale());
  return createTranslator(resolvedLocale);
}

/**
 * Gets both the translator and detected locale.
 * Useful when you need to pass the locale to client components.
 *
 * @param locale - Optional locale override
 * @returns Object containing translator function and resolved locale
 *
 * @example
 * const { t, locale } = await getTranslation();
 * // Pass locale to client component
 * <ClientComponent locale={locale} />
 */
export async function getTranslation(locale?: Locale): Promise<{
  t: TranslatorFn;
  locale: Locale;
}> {
  const resolvedLocale = locale ?? (await getLocale());
  return {
    t: createTranslator(resolvedLocale),
    locale: resolvedLocale,
  };
}
