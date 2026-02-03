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

// ============================================================================
// Hook Interface
// ============================================================================

interface UseReactiveResumeIframeOptions {
	iframeRef: React.RefObject<HTMLIFrameElement>;
	draftId: string | null;
	onResumeUpdated?: (resumeData: JSONResume) => void;
	onDraftLoaded?: (draftId: string) => void;
	onError?: (error: string) => void;
}

interface UseReactiveResumeIframeReturn {
	isReady: boolean;
	isLoading: boolean;
	error: string | null;
	getResumeData: () => Promise<ResumeContent | null>;
	loadDraft: (draftId: string) => void;
	sendAuthToken: () => void;
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
}: UseReactiveResumeIframeOptions): UseReactiveResumeIframeReturn {
	const [isReady, setIsReady] = useState(false);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const { user } = useAuth();
	const messageHandlersRef = useRef<Map<string, (message: PostMessage) => void>>(new Map());
	const resumeDataPromiseRef = useRef<{
		resolve: (value: ResumeContent | null) => void;
		reject: (error: Error) => void;
	} | null>(null);

	// Get iframe origin from environment
	const iframeOrigin = process.env.NEXT_PUBLIC_REACTIVE_RESUME_URL || "http://localhost:3001";

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
	 * Send auth token to iframe
	 */
	const sendAuthToken = useCallback(() => {
		if (typeof window === "undefined") return;

		const token = localStorage.getItem("ApplyBots_access_token");
		if (token && isReady) {
			sendMessage({
				type: "set-auth-token",
				payload: { token },
			});
		}
	}, [isReady, sendMessage]);

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
				// Send auth token when iframe is ready
				sendAuthToken();
				// Load draft if we have one
				if (draftId) {
					loadDraft(draftId);
				}
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
	}, [validateOrigin, onResumeUpdated, onDraftLoaded, onError, draftId, loadDraft, sendAuthToken]);

	/**
	 * Send auth token when user changes or iframe becomes ready
	 */
	useEffect(() => {
		if (isReady && user) {
			sendAuthToken();
		}
	}, [isReady, user, sendAuthToken]);

	/**
	 * Load draft when draftId changes
	 */
	useEffect(() => {
		if (isReady && draftId) {
			loadDraft(draftId);
		}
	}, [isReady, draftId, loadDraft]);

	return {
		isReady,
		isLoading,
		error,
		getResumeData,
		loadDraft,
		sendAuthToken,
	};
}
