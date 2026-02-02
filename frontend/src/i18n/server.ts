import "server-only";

/**
 * Server-side i18n exports
 *
 * These functions use Next.js server APIs (cookies, headers) and must
 * only be imported in Server Components or Route Handlers.
 *
 * @example
 * ```tsx
 * // In a server component
 * import { getLocale, getT } from "@/i18n/server";
 *
 * export default async function Page() {
 *   const locale = await getLocale();
 *   const t = await getT();
 *   return <h1>{t("dashboard.welcome")}</h1>;
 * }
 * ```
 *
 * @module i18n/server
 */

export { getLocale, getLocaleSync } from "./next/getLocale.server";
export { getT, getTranslation } from "./next/getT.server";
