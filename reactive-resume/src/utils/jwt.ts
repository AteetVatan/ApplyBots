/**
 * JWT token utilities
 * Note: Client-side decoding only (no verification)
 * Full verification happens server-side in backend
 */

export interface DecodedJWT {
	user_id: string;
	exp?: number;
	[key: string]: unknown;
}

export function decodeJWT(token: string): DecodedJWT | null {
	try {
		const parts = token.split(".");
		if (parts.length !== 3) return null;

		const payload = JSON.parse(atob(parts[1]));
		return {
			user_id: payload.sub || payload.user_id || payload.userId,
			exp: payload.exp,
		};
	} catch (error) {
		console.warn("Failed to decode JWT:", error);
		return null;
	}
}

export function getTokenFromStorage(): string | null {
	if (typeof window === "undefined") return null;
	return localStorage.getItem("ApplyBots_access_token");
}

export function isTokenExpired(token: string): boolean {
	const decoded = decodeJWT(token);
	if (!decoded || !decoded.exp) return false;
	return Date.now() >= decoded.exp * 1000;
}

export function validateToken(token: string | null): boolean {
	if (!token) return false;
	if (isTokenExpired(token)) return false;
	return true;
}
