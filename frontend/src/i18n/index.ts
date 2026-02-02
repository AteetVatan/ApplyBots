"use client";

/**
 * i18n Module - Centralized String Management
 *
 * Provides type-safe internationalization for Next.js App Router with:
 * - Compile-time key validation
 * - Parameter interpolation
 * - Server and client component support
 * - Locale detection and fallback
 *
 * ## Quick Start
 *
 * ### Server Components
 * ```tsx
 * import { getT, getLocale } from "@/i18n/server";
 *
 * export default async function Page() {
 *   const t = await getT();
 *   return <h1>{t("dashboard.welcome")}</h1>;
 * }
 * ```
 *
 * ### Client Components
 * ```tsx
 * "use client";
 * import { useT } from "@/i18n";
 *
 * export function Greeting({ name }: { name: string }) {
 *   const t = useT();
 *   return <p>{t("profile.greeting", { name })}</p>;
 * }
 * ```
 *
 * ## Adding Translations
 *
 * 1. Add keys to `src/i18n/locales/en.ts`
 * 2. Add same keys to other locale files (e.g., `de.ts`)
 * 3. TypeScript will autocomplete valid keys
 *
 * @module i18n
 */

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

// Note: parseAcceptLanguage is server-only and has been moved to getLocale.ts.
// It's not exported from the client module to break the shared dependency chain.
export {
  DEFAULT_LOCALE,
  SUPPORTED_LOCALES,
  LOCALE_COOKIE_NAME,
  isValidLocale,
  validateLocale,
} from "./config";

// ---------------------------------------------------------------------------
// Core Types
// ---------------------------------------------------------------------------

export type {
  Locale,
  TranslationKey,
  TranslationValue,
  Dictionary,
  InterpolationParams,
  TranslatorFn,
} from "./core/types";

export {
  I18nError,
  MissingKeyError,
  MissingInterpolationError,
} from "./core/types";

// ---------------------------------------------------------------------------
// Core Utilities
// ---------------------------------------------------------------------------

export {
  createTranslator,
  createLocaleTranslator,
} from "./core/createTranslator";

export {
  interpolate,
  extractParamNames,
  validateParams,
} from "./core/interpolate";

// ---------------------------------------------------------------------------
// Next.js Integration (Client-side only)
// ---------------------------------------------------------------------------
// NOTE: Server-side functions (getLocale, getT) are NOT exported here.
// Import them directly from "@/i18n/server" in server components.

export { I18nProvider, useI18nContext, useLocale } from "./client/I18nProvider";
export { useT } from "./client/useT";

// ---------------------------------------------------------------------------
// Dictionaries (for advanced usage)
// ---------------------------------------------------------------------------

export { getDictionary, dictionaries } from "./locales";
