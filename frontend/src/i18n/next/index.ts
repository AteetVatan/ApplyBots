/**
 * Next.js integration exports for i18n.
 *
 * This module provides framework-specific utilities for:
 * - Server-side locale detection
 * - Server component translations
 * - Client component translations (via React Context)
 */

// Server-side locale detection
export { getLocale, getLocaleSync } from "./getLocale";

// Server component translator
export { getT, getTranslation } from "./getT";

// Client component provider and hooks
export { I18nProvider, useI18nContext, useLocale } from "./I18nProvider";
export { useT } from "./useT";
