import { t } from "@lingui/core/macro";
import { debounce } from "es-toolkit";
import isDeepEqual from "fast-deep-equal";
import type { WritableDraft } from "immer";
import { current } from "immer";
import { toast } from "sonner";
import type { TemporalState } from "zundo";
import { temporal } from "zundo";
import { immer } from "zustand/middleware/immer";
import { create } from "zustand/react";
import { useStoreWithEqualityFn } from "zustand/traditional";
import type { ResumeData } from "@/schema/resume/data";
import { getAPIClient } from "@/lib/api-client";
import { getPostMessageClient } from "@/lib/postmessage-client";

type Resume = {
	id: string;
	name: string;
	slug: string;
	tags: string[];
	data: ResumeData;
	isLocked: boolean;
};

type ResumeStoreState = {
	resume: Resume;
	isReady: boolean;
};

type ResumeStoreActions = {
	initialize: (resume: Resume | null) => void;
	updateResumeData: (fn: (draft: WritableDraft<ResumeData>) => void) => void;
};

type ResumeStore = ResumeStoreState & ResumeStoreActions;

const controller = new AbortController();
const signal = controller.signal;

const _syncResume = async (resume: Resume) => {
	try {
		const apiClient = getAPIClient();
		
		// If resume has no ID, create it first
		if (!resume.id || resume.id === "") {
			const newId = await apiClient.create(resume.data);
			// Update the store with the new ID
			useResumeStore.getState().initialize({
				...resume,
				id: newId,
			});
		} else {
			// Update existing resume
			await apiClient.update(resume.id, resume.data);
		}

		// Notify parent window that resume was updated
		const postMessageClient = getPostMessageClient();
		postMessageClient.notifyResumeUpdated();
	} catch (error) {
		console.error("Error syncing resume:", error);
		const errorMessage = error instanceof Error ? error.message : "Failed to save resume";
		toast.error(errorMessage);
		throw error;
	}
};

const syncResume = debounce(_syncResume, 500, { signal });

let errorToastId: string | number | undefined;

type PartializedState = { resume: Resume | null };

export const useResumeStore = create<ResumeStore>()(
	temporal(
		immer((set) => ({
			resume: null as unknown as Resume,
			isReady: false,

			initialize: (resume) => {
				set((state) => {
					state.resume = resume as Resume;
					state.isReady = resume !== null;
					useResumeStore.temporal.getState().clear();
				});
			},

			updateResumeData: (fn) => {
				set((state) => {
					if (!state.resume) return state;

					if (state.resume.isLocked) {
						errorToastId = toast.error(t`This resume is locked and cannot be updated.`, { id: errorToastId });
						return state;
					}

					fn(state.resume.data);
					syncResume(current(state.resume));
				});
			},
		})),
		{
			partialize: (state) => ({ resume: state.resume }),
			equality: (pastState, currentState) => isDeepEqual(pastState, currentState),
			limit: 100,
		},
	),
);

// Note: Resume updates are already notified via _syncResume, so we don't need a separate subscription

export function useTemporalStore<T>(selector: (state: TemporalState<PartializedState>) => T): T {
	return useStoreWithEqualityFn(useResumeStore.temporal, selector);
}
