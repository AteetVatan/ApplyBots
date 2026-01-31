/**
 * Core i18n type definitions.
 *
 * Provides type-safe translation keys derived from nested dictionary structure,
 * ensuring compile-time validation of all translation lookups.
 */

import type { en } from "../locales/en";

// ---------------------------------------------------------------------------
// Locale Types
// ---------------------------------------------------------------------------

/** Supported locale codes */
export type Locale = "en" | "de";

// ---------------------------------------------------------------------------
// Dictionary Types
// ---------------------------------------------------------------------------

/** Primitive translation value (string only, no nested objects) */
export type TranslationValue = string;

/** Recursive dictionary structure allowing nested namespaces */
export type Dictionary = {
  readonly [key: string]: TranslationValue | Dictionary;
};

// ---------------------------------------------------------------------------
// Key Derivation Utilities
// ---------------------------------------------------------------------------

/**
 * Recursively derives dot-notation keys from a nested object type.
 *
 * @example
 * type Dict = { nav: { home: "Home"; dashboard: "Dashboard" } };
 * type Keys = NestedKeyOf<Dict>; // "nav.home" | "nav.dashboard"
 */
export type NestedKeyOf<T, Prefix extends string = ""> = T extends string
  ? Prefix
  : T extends object
    ? {
        [K in keyof T & string]: NestedKeyOf<
          T[K],
          Prefix extends "" ? K : `${Prefix}.${K}`
        >;
      }[keyof T & string]
    : never;

/**
 * Union of all valid translation keys derived from the English dictionary.
 * This is the source of truth - all other locales must match this structure.
 */
export type TranslationKey = NestedKeyOf<typeof en>;

// ---------------------------------------------------------------------------
// Interpolation Types
// ---------------------------------------------------------------------------

/**
 * Extracts interpolation parameter names from a translation string.
 *
 * @example
 * type Params = ExtractParams<"Hello, {name}!">; // "name"
 * type Params2 = ExtractParams<"Hi {first} {last}">; // "first" | "last"
 */
export type ExtractParams<T extends string> =
  T extends `${string}{${infer Param}}${infer Rest}`
    ? Param | ExtractParams<Rest>
    : never;

/**
 * Parameters object for interpolation.
 * Values are always strings to prevent XSS (no raw HTML injection).
 */
export type InterpolationParams = Record<string, string | number>;

// ---------------------------------------------------------------------------
// Translator Function Types
// ---------------------------------------------------------------------------

/**
 * Type-safe translator function signature.
 * Accepts a translation key and optional interpolation parameters.
 */
export type TranslatorFn = (
  key: TranslationKey,
  params?: InterpolationParams
) => string;

// ---------------------------------------------------------------------------
// Error Types
// ---------------------------------------------------------------------------

/** Base error for i18n-related issues */
export class I18nError extends Error {
  constructor(
    message: string,
    public readonly code: string
  ) {
    super(message);
    this.name = "I18nError";
  }
}

/** Thrown when a translation key is not found in the dictionary */
export class MissingKeyError extends I18nError {
  constructor(
    public readonly key: string,
    public readonly locale: Locale
  ) {
    super(`Missing translation key "${key}" for locale "${locale}"`, "MISSING_KEY");
    this.name = "MissingKeyError";
  }
}

/** Thrown when a required interpolation parameter is missing */
export class MissingInterpolationError extends I18nError {
  constructor(
    public readonly param: string,
    public readonly key: string
  ) {
    super(
      `Missing interpolation parameter "{${param}}" for key "${key}"`,
      "MISSING_INTERPOLATION"
    );
    this.name = "MissingInterpolationError";
  }
}
