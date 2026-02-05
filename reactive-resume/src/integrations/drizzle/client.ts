/**
 * Drizzle Database Client
 * 
 * NOTE: This application uses the FastAPI backend for data storage.
 * This file exists as a stub to satisfy imports. The database check
 * in health.ts will be disabled since there's no local database.
 */

// Stub database client - not actually used since we use FastAPI backend
export const db = {
	execute: async () => {
		// Stub implementation - will not be called in health check
		return Promise.resolve([]);
	},
};
