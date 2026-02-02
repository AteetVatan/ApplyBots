/**
 * Dictionary registry.
 *
 * Centralizes all locale dictionaries and provides type-safe access.
 * New locales should be added here after creating their dictionary file.
 */

import type { Locale, Dictionary } from "../core/types";
import { en } from "./en";
import { es } from "./es";
import { fr } from "./fr";
import { de } from "./de";

/**
 * Registry mapping locale codes to their dictionaries.
 * All dictionaries must match the structure of the English dictionary.
 */
export const dictionaries: Record<Locale, Dictionary> = {
  en,
  es,
  fr,
  de,
};

/**
 * Retrieves the dictionary for a given locale.
 *
 * @param locale - The locale code to retrieve
 * @returns The dictionary for the locale
 */
export function getDictionary(locale: Locale): Dictionary {
  return dictionaries[locale];
}

// Re-export dictionary types for use in other locale files
export type { EnDictionary, LocaleDictionary } from "./en";
