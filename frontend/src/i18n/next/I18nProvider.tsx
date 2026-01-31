"use client";

/**
 * React context provider for i18n in client components.
 *
 * Provides the translator function and current locale to all
 * descendant client components via React Context.
 *
 * Must be wrapped around client components that need translations.
 * Typically added to the root Providers component.
 */

import {
  createContext,
  useContext,
  useMemo,
  type ReactNode,
} from "react";
import type { Locale, TranslatorFn } from "../core/types";
import { createTranslator } from "../core/createTranslator";
import { DEFAULT_LOCALE } from "../config";

// ---------------------------------------------------------------------------
// Context Definition
// ---------------------------------------------------------------------------

interface I18nContextValue {
  /** The current locale */
  locale: Locale;
  /** The translator function */
  t: TranslatorFn;
}

const I18nContext = createContext<I18nContextValue | null>(null);

// ---------------------------------------------------------------------------
// Provider Component
// ---------------------------------------------------------------------------

interface I18nProviderProps {
  /** The locale to use for translations */
  locale: Locale;
  /** Child components that need i18n access */
  children: ReactNode;
}

/**
 * Provider component for i18n context.
 *
 * Wraps client components to provide translation functionality.
 * The locale should be passed from a server component that detects it.
 *
 * @example
 * // In a layout or provider wrapper
 * <I18nProvider locale={locale}>
 *   <App />
 * </I18nProvider>
 */
export function I18nProvider({ locale, children }: I18nProviderProps) {
  // Memoize the context value to prevent unnecessary re-renders
  const value = useMemo<I18nContextValue>(() => {
    return {
      locale,
      t: createTranslator(locale),
    };
  }, [locale]);

  return (
    <I18nContext.Provider value={value}>
      {children}
    </I18nContext.Provider>
  );
}

// ---------------------------------------------------------------------------
// Context Hook
// ---------------------------------------------------------------------------

/**
 * Hook to access the i18n context.
 *
 * Must be used within an I18nProvider.
 *
 * @returns The i18n context value
 * @throws Error if used outside of I18nProvider
 *
 * @internal Use `useT()` or `useLocale()` instead for cleaner API
 */
export function useI18nContext(): I18nContextValue {
  const context = useContext(I18nContext);

  if (!context) {
    // Provide a fallback in case provider is missing
    // This allows components to work even without provider (with default locale)
    if (process.env.NODE_ENV === "development") {
      console.warn(
        "[i18n] useI18nContext called outside of I18nProvider. " +
          "Using default locale. Wrap your app with <I18nProvider>."
      );
    }
    return {
      locale: DEFAULT_LOCALE,
      t: createTranslator(DEFAULT_LOCALE),
    };
  }

  return context;
}

/**
 * Hook to get just the current locale.
 *
 * @returns The current locale
 *
 * @example
 * const locale = useLocale();
 * console.log(locale); // "en"
 */
export function useLocale(): Locale {
  return useI18nContext().locale;
}
