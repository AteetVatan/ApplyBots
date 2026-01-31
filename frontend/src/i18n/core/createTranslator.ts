/**
 * Translator factory function.
 *
 * Creates a type-safe translator function for a given locale that:
 * - Provides compile-time key validation via TypeScript
 * - Supports parameter interpolation
 * - Handles missing keys gracefully with appropriate dev/prod behavior
 */

import {
  type Locale,
  type TranslationKey,
  type InterpolationParams,
  type TranslatorFn,
  type Dictionary,
  MissingKeyError,
} from "./types";
import { interpolate } from "./interpolate";
import { getDictionary } from "../locales";
import { DEFAULT_LOCALE } from "../config";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Check if running in development mode */
const IS_DEV = process.env.NODE_ENV === "development";

// ---------------------------------------------------------------------------
// Key Resolution
// ---------------------------------------------------------------------------

/**
 * Resolves a dot-notation key to its value in the dictionary.
 *
 * @param dictionary - The translation dictionary to search
 * @param key - The dot-notation key (e.g., "nav.home")
 * @returns The translation string or undefined if not found
 *
 * @example
 * const dict = { nav: { home: "Home" } };
 * resolveKey(dict, "nav.home"); // "Home"
 * resolveKey(dict, "nav.missing"); // undefined
 */
function resolveKey(
  dictionary: Dictionary,
  key: string
): string | undefined {
  const parts = key.split(".");
  let current: Dictionary | string = dictionary;

  for (const part of parts) {
    if (typeof current !== "object" || current === null) {
      return undefined;
    }
    current = current[part] as Dictionary | string;
  }

  return typeof current === "string" ? current : undefined;
}

/**
 * Handles a missing translation key.
 *
 * @param key - The missing translation key
 * @param locale - The locale that was searched
 * @throws {MissingKeyError} In development mode
 */
function handleMissingKey(key: string, locale: Locale): void {
  const error = new MissingKeyError(key, locale);

  if (IS_DEV) {
    throw error;
  }

  // In production, log a structured error but don't crash
  console.error("[i18n]", error.message, {
    code: error.code,
    key,
    locale,
  });
}

// ---------------------------------------------------------------------------
// Translator Factory
// ---------------------------------------------------------------------------

/**
 * Creates a translator function for the specified locale.
 *
 * The returned function provides type-safe translation lookups with:
 * - Compile-time key validation (TypeScript autocomplete)
 * - Runtime interpolation of parameters
 * - Graceful fallback behavior in production
 *
 * @param locale - The locale to use for translations
 * @returns A translator function t(key, params?)
 *
 * @example
 * const t = createTranslator("en");
 *
 * t("nav.home"); // "Home"
 * t("profile.greeting", { name: "Ateet" }); // "Hello, Ateet!"
 * t("invalid.key"); // Dev: throws, Prod: logs + returns "invalid.key"
 */
export function createTranslator(locale: Locale): TranslatorFn {
  const dictionary = getDictionary(locale);
  const fallbackDictionary =
    locale !== DEFAULT_LOCALE ? getDictionary(DEFAULT_LOCALE) : null;

  return function t(
    key: TranslationKey,
    params?: InterpolationParams
  ): string {
    // Try primary locale first
    let value = resolveKey(dictionary, key);

    // Fallback to default locale if key not found
    if (value === undefined && fallbackDictionary) {
      value = resolveKey(fallbackDictionary, key);
      if (value !== undefined && IS_DEV) {
        console.warn(
          `[i18n] Key "${key}" missing for locale "${locale}", using fallback from "${DEFAULT_LOCALE}"`
        );
      }
    }

    // Handle completely missing key
    if (value === undefined) {
      handleMissingKey(key, locale);
      // In production, return the key itself as a fallback
      return key;
    }

    // Apply interpolation if template has parameters or params provided
    return interpolate(value, params, key);
  };
}

/**
 * Creates a translator with pre-bound locale for convenience.
 * Useful for creating locale-specific translator modules.
 *
 * @param locale - The locale to bind
 * @returns Object with t function and locale
 */
export function createLocaleTranslator(locale: Locale) {
  return {
    t: createTranslator(locale),
    locale,
  };
}
