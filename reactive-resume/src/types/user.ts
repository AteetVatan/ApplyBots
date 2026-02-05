/**
 * Minimal user type for ORPC context
 * Only needs id for ORPC protected procedures
 */
export interface MinimalUser {
	id: string;
}

/**
 * User display info for UI
 * Received from frontend via postMessage
 */
export interface UserDisplay {
	id: string;
	name: string;
	email: string;
	image?: string;
}
