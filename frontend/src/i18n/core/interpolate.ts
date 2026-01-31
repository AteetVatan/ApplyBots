/**
 * Interpolation utilities for translation strings.
 *
 * Handles parameter substitution in translation strings with safety guarantees:
 * - Missing params: Error in dev, warning + partial string in prod
 * - Extra params: Silently ignored
 * - XSS prevention: All values are treated as plain text
 */

import {
  MissingInterpolationError,
  type InterpolationParams,
} from "./types";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/** Regex to match interpolation placeholders: {paramName} */
const INTERPOLATION_REGEX = /\{(\w+)\}/g;

/** Check if running in development mode */
const IS_DEV = process.env.NODE_ENV === "development";

// ---------------------------------------------------------------------------
// Core Interpolation
// ---------------------------------------------------------------------------

/**
 * Extracts all parameter names from a translation string.
 *
 * @param template - The translation string with {param} placeholders
 * @returns Array of parameter names found in the template
 *
 * @example
 * extractParamNames("Hello, {name}!"); // ["name"]
 * extractParamNames("Hi {first} {last}"); // ["first", "last"]
 */
export function extractParamNames(template: string): string[] {
  const params: string[] = [];
  let match: RegExpExecArray | null;

  // Reset regex state
  INTERPOLATION_REGEX.lastIndex = 0;

  while ((match = INTERPOLATION_REGEX.exec(template)) !== null) {
    const paramName = match[1];
    if (!params.includes(paramName)) {
      params.push(paramName);
    }
  }

  return params;
}

/**
 * Escapes a value for safe interpolation (prevents XSS).
 *
 * @param value - The value to escape
 * @returns The escaped string value
 */
function escapeValue(value: string | number): string {
  const str = String(value);
  // Basic HTML entity escaping for safety
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/**
 * Interpolates parameters into a translation string.
 *
 * @param template - The translation string with {param} placeholders
 * @param params - Object containing parameter values
 * @param key - The translation key (for error messages)
 * @returns The interpolated string
 *
 * @throws {MissingInterpolationError} In development when a required param is missing
 *
 * @example
 * interpolate("Hello, {name}!", { name: "World" }, "greeting");
 * // Returns: "Hello, World!"
 *
 * interpolate("Hi {first} {last}", { first: "John" }, "fullName");
 * // Dev: throws MissingInterpolationError
 * // Prod: logs warning, returns "Hi John {last}"
 */
export function interpolate(
  template: string,
  params: InterpolationParams | undefined,
  key: string
): string {
  // No params provided - check if template expects any
  if (!params) {
    const expectedParams = extractParamNames(template);
    if (expectedParams.length > 0) {
      handleMissingParam(expectedParams[0], key);
      // In prod, return template as-is with placeholders intact
      return template;
    }
    return template;
  }

  // Track which params were used for validation
  const usedParams = new Set<string>();

  // Replace all placeholders
  const result = template.replace(INTERPOLATION_REGEX, (match, paramName: string) => {
    if (paramName in params) {
      usedParams.add(paramName);
      return escapeValue(params[paramName]);
    }

    // Parameter not provided
    handleMissingParam(paramName, key);
    // In prod, keep the placeholder intact
    return match;
  });

  return result;
}

/**
 * Handles a missing interpolation parameter.
 *
 * @param param - The missing parameter name
 * @param key - The translation key
 * @throws {MissingInterpolationError} In development mode
 */
function handleMissingParam(param: string, key: string): void {
  const error = new MissingInterpolationError(param, key);

  if (IS_DEV) {
    throw error;
  }

  // In production, log a warning but don't crash
  console.warn("[i18n]", error.message, {
    code: error.code,
    param,
    key,
  });
}

/**
 * Validates that all required parameters are provided.
 * Useful for pre-validation before interpolation.
 *
 * @param template - The translation string with {param} placeholders
 * @param params - Object containing parameter values
 * @returns Object with validation result and missing params
 */
export function validateParams(
  template: string,
  params: InterpolationParams | undefined
): { valid: boolean; missing: string[] } {
  const required = extractParamNames(template);
  const provided = params ? Object.keys(params) : [];
  const missing = required.filter((p) => !provided.includes(p));

  return {
    valid: missing.length === 0,
    missing,
  };
}
