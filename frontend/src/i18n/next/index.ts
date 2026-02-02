/**
 * Barrel exports for Next.js i18n utilities.
 *
 * Re-exports server and client locale detection utilities.
 * Import from "@/i18n/next" for direct access to these utilities.
 *
 * NOTE: Server utilities (getLocale, getT) use Next.js server APIs
 * and should only be imported in Server Components or Route Handlers.
 */

// Re-export server utilities (only for server components)
export { getLocale, getLocaleSync } from "./getLocale.server";
export { getT, getTranslation } from "./getT.server";

// Re-export client utilities (for client components)
export { getLocaleClient } from "./getLocale.client";
