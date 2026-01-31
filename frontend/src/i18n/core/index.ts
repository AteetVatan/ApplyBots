/**
 * Core i18n module exports.
 *
 * This module contains pure logic with no framework dependencies.
 * Safe to import anywhere in the application.
 */

// Types
export type {
  Locale,
  TranslationKey,
  TranslationValue,
  Dictionary,
  InterpolationParams,
  TranslatorFn,
} from "./types";

// Error classes
export {
  I18nError,
  MissingKeyError,
  MissingInterpolationError,
} from "./types";

// Translator factory
export { createTranslator, createLocaleTranslator } from "./createTranslator";

// Interpolation utilities
export {
  interpolate,
  extractParamNames,
  validateParams,
} from "./interpolate";
