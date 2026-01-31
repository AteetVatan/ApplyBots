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
 * import { getT } from "@/i18n";
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

export {
  DEFAULT_LOCALE,
  SUPPORTED_LOCALES,
  LOCALE_COOKIE_NAME,
  isValidLocale,
  validateLocale,
  parseAcceptLanguage,
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
// Next.js Integration
// ---------------------------------------------------------------------------

// Server-side
export { getLocale, getLocaleSync } from "./next/getLocale";
export { getT, getTranslation } from "./next/getT";

// Client-side
export { I18nProvider, useI18nContext, useLocale } from "./next/I18nProvider";
export { useT } from "./next/useT";

// ---------------------------------------------------------------------------
// Dictionaries (for advanced usage)
// ---------------------------------------------------------------------------

export { getDictionary, dictionaries } from "./locales";
