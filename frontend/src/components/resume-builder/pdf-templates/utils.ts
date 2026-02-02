/**
 * Utility functions for PDF template rendering.
 */

/**
 * Strip HTML tags and decode entities for plain text output.
 */
export function stripHtml(html: string | null | undefined): string {
  if (!html) return "";
  return html
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/p>/gi, "\n")
    .replace(/<\/li>/gi, "\n")
    .replace(/<[^>]*>/g, "")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\n\s*\n/g, "\n")
    .trim();
}

/**
 * Capitalize first letter of a string.
 */
export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Format date range for experience/education entries.
 */
export function formatDateRange(
  startDate: string | null,
  endDate: string | null,
  isCurrent?: boolean
): string {
  if (!startDate && !endDate) return "";
  const start = startDate || "";
  const end = isCurrent ? "Present" : endDate || "";
  if (start && end) return `${start} - ${end}`;
  return start || end;
}
