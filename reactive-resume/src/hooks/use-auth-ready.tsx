/**
 * Hook to track when authentication is ready for API calls.
 * 
 * In embedded iframe mode, we need to wait for the parent to send
 * the auth token via postMessage before making authenticated API calls.
 */

import { useState, useEffect } from "react";
import { getPostMessageClient } from "@/lib/postmessage-client";

// Global event name for auth ready signal
const AUTH_READY_EVENT = "applybots:auth-ready";

/**
 * Signal that auth is ready (token received)
 */
export function signalAuthReady(): void {
	if (typeof window !== "undefined") {
		window.dispatchEvent(new CustomEvent(AUTH_READY_EVENT));
	}
}

/**
 * Check if we're running in an iframe
 */
function isInIframe(): boolean {
	if (typeof window === "undefined") return false;
	try {
		return window.self !== window.top;
	} catch {
		// If we can't access window.top, we're in a cross-origin iframe
		return true;
	}
}

/**
 * Check if auth token exists in localStorage
 */
function hasAuthToken(): boolean {
	if (typeof window === "undefined") return false;
	return !!localStorage.getItem("ApplyBots_access_token");
}

/**
 * Hook that returns true when authentication is ready for API calls.
 * 
 * - If not in iframe: returns true immediately
 * - If in iframe with token: returns true immediately  
 * - If in iframe without token: waits for token via postMessage
 */
export function useAuthReady(): boolean {
	const [isReady, setIsReady] = useState(() => {
		// Initial state: ready if not in iframe OR if token already exists
		if (typeof window === "undefined") return false;
		return !isInIframe() || hasAuthToken();
	});

	useEffect(() => {
		// If already ready, no need to listen
		if (isReady) return;

		// Not in iframe and no token - still ready (will get 401 naturally)
		if (!isInIframe()) {
			setIsReady(true);
			return;
		}

		// In iframe without token - wait for auth-ready event or token
		const handleAuthReady = () => {
			setIsReady(true);
		};

		// Listen for auth-ready custom event
		window.addEventListener(AUTH_READY_EVENT, handleAuthReady);

		// Also check periodically if token appeared (fallback)
		const checkInterval = setInterval(() => {
			if (hasAuthToken()) {
				setIsReady(true);
				clearInterval(checkInterval);
			}
		}, 100);

		// Timeout after 5 seconds - proceed anyway (will get 401)
		const timeout = setTimeout(() => {
			console.warn("Auth token not received within timeout, proceeding anyway");
			setIsReady(true);
		}, 5000);

		return () => {
			window.removeEventListener(AUTH_READY_EVENT, handleAuthReady);
			clearInterval(checkInterval);
			clearTimeout(timeout);
		};
	}, [isReady]);

	return isReady;
}
