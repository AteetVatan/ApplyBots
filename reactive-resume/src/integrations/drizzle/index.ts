/**
 * Drizzle Schema Types
 * 
 * NOTE: This application uses the FastAPI backend for data storage.
 * This file provides type definitions for compatibility with existing code.
 */

import type { ResumeData } from "@/schema/resume/data";

/**
 * Resume type matching what the printer service expects
 */
export const schema = {
	resume: {} as {
		id: string;
		data: ResumeData;
		userId: string;
		updatedAt: Date;
	},
};
