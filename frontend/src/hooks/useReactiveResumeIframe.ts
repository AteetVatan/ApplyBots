/**
 * Hook for managing Reactive Resume iframe communication.
 * 
 * Handles postMessage communication between parent window and Reactive Resume iframe.
 * Used for ATS scoring integration and draft loading.
 * 
 * Standards: react_nextjs.mdc
 * - Type-safe postMessage handling
 * - Origin validation for security
 * - Error handling
 */

"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth } from "@/providers/AuthProvider";
import type { ResumeContent } from "@/lib/resume-adapter";
import { resumeContentToApiSchema, jsonResumeToResumeContent } from "@/lib/resume-adapter";
import type { JSONResume } from "@/lib/resume-adapter";

// ============================================================================
// Message Types
// ============================================================================

interface PostMessage {
	type: string;
	payload?: unknown;
}

interface ResumeDataMessage extends PostMessage {
	type: "resume-data";
	payload: JSONResume;
}

interface ResumeUpdatedMessage extends PostMessage {
	type: "resume-updated";
}

interface DraftLoadedMessage extends PostMessage {
	type: "draft-loaded";
	payload: { draftId: string };
}

interface IframeReadyMessage extends PostMessage {
	type: "iframe-ready";
}

interface ErrorMessage extends PostMessage {
	type: "error";
	payload: { message: string };
}

interface SetUserInfoMessage extends PostMessage {
	type: "set-user-info";
	payload: {
		id: string;
		name: string;
		email: string;
		image?: string;
	};
}

interface RequestUserInfoMessage extends PostMessage {
	type: "request-user-info";
}

interface AuthRequiredMessage extends PostMessage {
	type: "auth-required";
}

interface LogoutMessage extends PostMessage {
	type: "logout";
}

interface AuthTokenReceivedMessage extends PostMessage {
	type: "auth-token-received";
}

interface RequestTokenRefreshMessage extends PostMessage {
	type: "request-token-refresh";
}

// ============================================================================
// Hook Interface
// ============================================================================

interface UseReactiveResumeIframeOptions {
	iframeRef: React.RefObject<HTMLIFrameElement>;
	draftId: string | null;
	onResumeUpdated?: (resumeData: JSONResume) => void;
	onDraftLoaded?: (draftId: string) => void;
	onError?: (error: string) => void;
	onAuthRequired?: () => void;
	onLogout?: () => void;
}

interface UseReactiveResumeIframeReturn {
	isReady: boolean;
	isLoading: boolean;
	error: string | null;
	getResumeData: () => Promise<ResumeContent | null>;
	loadDraft: (draftId: string) => void;
	sendAuthToken: (forceImmediate?: boolean) => Promise<void>;
}

// ============================================================================
// Hook Implementation
// ============================================================================

export function useReactiveResumeIframe({
	iframeRef,
	draftId,
	onResumeUpdated,
	onDraftLoaded,
	onError,
	onAuthRequired,
	onLogout,
}: UseReactiveResumeIframeOptions): UseReactiveResumeIframeReturn {
	const [isReady, setIsReady] = useState(false);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const { user, refreshToken } = useAuth();
	const messageHandlersRef = useRef<Map<string, (message: PostMessage) => void>>(new Map());
	const resumeDataPromiseRef = useRef<{
		resolve: (value: ResumeContent | null) => void;
		reject: (error: Error) => void;
	} | null>(null);

	// Get iframe origin from environment
	const iframeOrigin = process.env.NEXT_PUBLIC_REACTIVE_RESUME_URL || "http://localhost:3002";

	/**
	 * Validate message origin
	 */
	const validateOrigin = useCallback(
		(origin: string): boolean => {
			return origin === iframeOrigin;
		},
		[iframeOrigin],
	);

	/**
	 * Send message to iframe
	 */
	const sendMessage = useCallback(
		(message: PostMessage) => {
			const iframe = iframeRef.current;
			if (!iframe || !iframe.contentWindow) {
				console.warn("Iframe not available for sending message");
				return;
			}

			iframe.contentWindow.postMessage(message, iframeOrigin);
		},
		[iframeRef, iframeOrigin],
	);

	/**
	 * Get resume data from iframe
	 */
	const getResumeData = useCallback((): Promise<ResumeContent | null> => {
		return new Promise((resolve, reject) => {
			if (!isReady) {
				reject(new Error("Iframe is not ready"));
				return;
			}

			// Store promise resolvers
			resumeDataPromiseRef.current = { resolve, reject };

			// Set timeout
			const timeout = setTimeout(() => {
				if (resumeDataPromiseRef.current) {
					resumeDataPromiseRef.current.reject(new Error("Timeout waiting for resume data"));
					resumeDataPromiseRef.current = null;
				}
			}, 5000);

			// Register one-time handler for resume-data
			const handler = (message: PostMessage) => {
				if (message.type === "resume-data") {
					clearTimeout(timeout);
					const resumeDataMessage = message as ResumeDataMessage;
					try {
						const resumeContent = jsonResumeToResumeContent(resumeDataMessage.payload);
						if (resumeDataPromiseRef.current) {
							resumeDataPromiseRef.current.resolve(resumeContent as ResumeContent);
							resumeDataPromiseRef.current = null;
						}
					} catch (err) {
						const error = err instanceof Error ? err : new Error("Failed to convert resume data");
						if (resumeDataPromiseRef.current) {
							resumeDataPromiseRef.current.reject(error);
							resumeDataPromiseRef.current = null;
						}
					}
					messageHandlersRef.current.delete("resume-data");
				}
			};

			messageHandlersRef.current.set("resume-data", handler);

			// Request resume data
			sendMessage({ type: "get-resume" });
		});
	}, [isReady, sendMessage]);

	/**
	 * Load draft in iframe
	 */
	const loadDraft = useCallback(
		(draftIdToLoad: string) => {
			if (!isReady) {
				console.warn("Iframe is not ready, cannot load draft");
				return;
			}

			sendMessage({
				type: "load-draft",
				payload: { draftId: draftIdToLoad },
			});
		},
		[isReady, sendMessage],
	);

	/**
	 * Check if token is expired
	 */
	const isTokenExpired = useCallback((token: string): boolean => {
		try {
			const parts = token.split(".");
			if (parts.length !== 3) return true;
			const payload = JSON.parse(atob(parts[1]));
			const exp = payload.exp;
			if (!exp) return false; // No expiration means valid
			return Date.now() >= exp * 1000;
		} catch {
			return true; // If we can't decode, consider expired
		}
	}, []);

	/**
	 * Send auth token to iframe (can be called before isReady for initial setup)
	 * Checks if token is expired and refreshes it if needed
	 */
	const sendAuthToken = useCallback(async (forceImmediate = false) => {
		if (typeof window === "undefined") return;

		let token = localStorage.getItem("ApplyBots_access_token");
		
		// Check if token is expired and refresh if needed
		if (token && isTokenExpired(token)) {
			console.log("Token expired, refreshing...");
			try {
				await refreshToken();
				token = localStorage.getItem("ApplyBots_access_token");
			} catch (error) {
				console.error("Failed to refresh token:", error);
				// If refresh fails, still try to send the expired token
				// The iframe will handle the 401 response
			}
		}
		
		// Allow sending if forceImmediate is true (for iframe-ready handler) or if isReady
		if (token && (forceImmediate || isReady)) {
			sendMessage({
				type: "set-auth-token",
				payload: { token },
			});
		}
	}, [isReady, sendMessage, isTokenExpired, refreshToken]);

	/**
	 * Send user display info to iframe
	 */
	const sendUserInfo = useCallback(() => {
		if (user && isReady) {
			sendMessage({
				type: "set-user-info",
				payload: {
					id: user.id,
					name: user.fullName || "User",
					email: user.email || "",
					image: undefined, // Add if available
				},
			});
		}
	}, [user, isReady, sendMessage]);

	/**
	 * Setup message listener
	 */
	useEffect(() => {
		const handleMessage = (event: MessageEvent) => {
			// Validate origin
			if (!validateOrigin(event.origin)) {
				console.warn(`Rejected message from unauthorized origin: ${event.origin}`);
				return;
			}

			const message = event.data as PostMessage;
			if (!message || !message.type) return;

			// Handle iframe-ready
			if (message.type === "iframe-ready") {
				setIsReady(true);
				// Send auth token immediately when iframe is ready (use forceImmediate=true)
				sendAuthToken(true);
				// Send user info when iframe is ready
				sendUserInfo();
				// Note: Don't load draft here - wait for auth-token-received
				return;
			}

			// Handle auth-token-received - now it's safe to load draft
			if (message.type === "auth-token-received") {
				// Load draft if we have one
				// NOTE: We can't use loadDraft() here because it checks isReady state,
				// which may not have updated yet due to React's batched state updates.
				// Instead, send the message directly - we know iframe is ready since it just responded.
				if (draftId) {
					sendMessage({
						type: "load-draft",
						payload: { draftId },
					});
				}
				return;
			}

			// Handle request-user-info message from reactive-resume
			if (message.type === "request-user-info") {
				sendUserInfo();
				return;
			}

			// Handle request-token-refresh message from reactive-resume
			if (message.type === "request-token-refresh") {
				// Refresh token and send new one to iframe
				refreshToken()
					.then(() => {
						sendAuthToken(true);
					})
					.catch((error) => {
						console.error("Failed to refresh token:", error);
						onAuthRequired?.();
					});
				return;
			}

			// Handle auth-required message from reactive-resume
			if (message.type === "auth-required") {
				onAuthRequired?.();
				return;
			}

			// Handle logout message from reactive-resume
			if (message.type === "logout") {
				onLogout?.();
				return;
			}

			// Handle resume-updated
			if (message.type === "resume-updated") {
				onResumeUpdated?.(message.payload as JSONResume);
				return;
			}

			// Handle draft-loaded
			if (message.type === "draft-loaded") {
				const draftLoadedMessage = message as DraftLoadedMessage;
				onDraftLoaded?.(draftLoadedMessage.payload.draftId);
				return;
			}

			// Handle error
			if (message.type === "error") {
				const errorMessage = message as ErrorMessage;
				const errorText = errorMessage.payload?.message || "Unknown error";
				setError(errorText);
				onError?.(errorText);
				return;
			}

			// Handle resume-data (for getResumeData promise)
			if (message.type === "resume-data") {
				const handler = messageHandlersRef.current.get("resume-data");
				if (handler) {
					handler(message);
				}
				return;
			}
		};

		window.addEventListener("message", handleMessage);

		return () => {
			window.removeEventListener("message", handleMessage);
		};
	}, [validateOrigin, onResumeUpdated, onDraftLoaded, onError, onAuthRequired, onLogout, draftId, sendMessage, sendAuthToken, sendUserInfo, refreshToken]);

	/**
	 * Send auth token and user info when user changes or iframe becomes ready
	 */
	useEffect(() => {
		if (isReady && user) {
			sendAuthToken();
			sendUserInfo();
		}
	}, [isReady, user, sendAuthToken, sendUserInfo]);

	// NOTE: Draft loading is handled via auth-token-received message handler
	// to ensure auth token is stored before API calls are made.
	// Do NOT add a useEffect here that loads draft when isReady changes!

	return {
		isReady,
		isLoading,
		error,
		getResumeData,
		loadDraft,
		sendAuthToken,
	};
}
