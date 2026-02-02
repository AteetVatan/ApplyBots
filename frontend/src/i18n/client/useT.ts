"use client";

/**
 * React hook for translations in client components.
 *
 * Provides a simple `useT()` hook that returns the translator function.
 * Must be used within an I18nProvider.
 *
 * @example
 * "use client";
 * import { useT } from "@/i18n";
 *
 * export function Greeting({ name }: { name: string }) {
 *   const t = useT();
 *   return <p>{t("profile.greeting", { name })}</p>;
 * }
 */

import type { TranslatorFn } from "../core/types";
import { useI18nContext } from "./I18nProvider";

// ---------------------------------------------------------------------------
// Translation Hook
// ---------------------------------------------------------------------------

/**
 * Hook to get the translator function in client components.
 *
 * Returns a type-safe translator function that can be used to
 * look up translations with optional interpolation.
 *
 * @returns The translator function
 *
 * @example
 * const t = useT();
 *
 * // Simple key lookup
 * t("nav.home"); // "Home"
 *
 * // With interpolation
 * t("profile.greeting", { name: "Ateet" }); // "Hello, Ateet!"
 */
export function useT(): TranslatorFn {
  const { t } = useI18nContext();
  return t;
}
