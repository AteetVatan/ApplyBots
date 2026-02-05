import { ORPCError } from "@orpc/client";
import { match } from "ts-pattern";
import type { ResumeData } from "@/schema/resume/data";
import { defaultResumeData } from "@/schema/resume/data";
import { env } from "@/utils/env";
import type { Locale } from "@/utils/locale";
import { getAPIClient } from "@/lib/api-client";
import { getStorageService } from "./storage";

const tags = {
	list: async (input: { userId: string }): Promise<string[]> => {
		// Tags not supported by FastAPI backend - return empty array
		// Could be implemented in FastAPI if needed
		return [];
	},
};

const statistics = {
	getById: async (input: { id: string; userId: string }) => {
		// Statistics not supported by FastAPI backend - return default values
		// Could be implemented in FastAPI if needed
		return {
			isPublic: false,
			views: 0,
			downloads: 0,
			lastViewedAt: null,
			lastDownloadedAt: null,
		};
	},

	increment: async (input: { id: string; views?: boolean; downloads?: boolean }): Promise<void> => {
		// Statistics not supported by FastAPI backend - no-op
		// Could be implemented in FastAPI if needed
	},
};

export const resumeService = {
	tags,
	statistics,

	list: async (input: { userId: string; tags: string[]; sort: "lastUpdatedAt" | "createdAt" | "name" }) => {
		const apiClient = getAPIClient();
		const resumes = await apiClient.list();

		// Filter by tags if provided (client-side filtering since FastAPI doesn't support tags)
		let filtered = resumes;
		if (input.tags.length > 0) {
			filtered = resumes.filter((resume) =>
				input.tags.some((tag) => resume.tags.includes(tag))
			);
		}

		// Sort resumes
		const sorted = filtered.sort((a, b) => {
			return match(input.sort)
				.with("lastUpdatedAt", () => {
					const aTime = a.updatedAt?.getTime() ?? 0;
					const bTime = b.updatedAt?.getTime() ?? 0;
					return bTime - aTime; // Descending
				})
				.with("createdAt", () => {
					const aTime = a.createdAt?.getTime() ?? 0;
					const bTime = b.createdAt?.getTime() ?? 0;
					return aTime - bTime; // Ascending
				})
				.with("name", () => a.name.localeCompare(b.name))
				.exhaustive();
		});

		// Return in the format expected by ORPC router
		return sorted.map((resume) => ({
			id: resume.id,
			name: resume.name,
			slug: resume.slug,
			tags: resume.tags,
			isPublic: resume.isPublic,
			isLocked: resume.isLocked,
			createdAt: resume.createdAt ?? new Date(),
			updatedAt: resume.updatedAt ?? new Date(),
		}));
	},

	getById: async (input: { id: string; userId: string }) => {
		const apiClient = getAPIClient();
		
		try {
			const resume = await apiClient.getById(input.id);
			
			return {
				id: resume.id,
				name: resume.name,
				slug: resume.slug,
				tags: resume.tags,
				data: resume.data,
				isPublic: resume.isPublic,
				isLocked: resume.isLocked,
				hasPassword: resume.hasPassword ?? false,
			};
		} catch (error) {
			if (error instanceof Error && error.message.includes("404")) {
				throw new ORPCError("NOT_FOUND");
			}
			throw error;
		}
	},

	getByIdForPrinter: async (input: { id: string }) => {
		const apiClient = getAPIClient();
		
		try {
			const resume = await apiClient.getById(input.id);
			
			// Convert picture URL to base64 if available
			try {
				if (resume.data.picture?.url) {
					const url = resume.data.picture.url.replace(env.APP_URL, "http://localhost:3000");
					const base64 = await fetch(url)
						.then((res) => res.arrayBuffer())
						.then((buffer) => Buffer.from(buffer).toString("base64"));
					
					resume.data.picture.url = `data:image/jpeg;base64,${base64}`;
				}
			} catch {
				// Ignore errors, as the picture is not always available
			}

			return {
				id: resume.id,
				name: resume.name,
				slug: resume.slug,
				tags: resume.tags,
				data: resume.data,
				userId: "", // Not available from FastAPI, but printer doesn't need it
				isLocked: resume.isLocked,
				updatedAt: resume.updatedAt ?? new Date(),
			};
		} catch (error) {
			if (error instanceof Error && error.message.includes("404")) {
				throw new ORPCError("NOT_FOUND");
			}
			throw error;
		}
	},

	getBySlug: async (input: { username: string; slug: string; currentUserId?: string }) => {
		// FastAPI backend doesn't support slug-based lookup
		// Try to use slug as ID (since api-client uses ID as slug)
		const apiClient = getAPIClient();
		
		try {
			const resume = await apiClient.getById(input.slug);
			
			// Increment statistics
			await resumeService.statistics.increment({ id: resume.id, views: true });

			return {
				id: resume.id,
				name: resume.name,
				slug: resume.slug,
				tags: resume.tags,
				data: resume.data,
				isPublic: resume.isPublic,
				isLocked: resume.isLocked,
				hasPassword: false as const, // FastAPI doesn't support password protection
			};
		} catch (error) {
			if (error instanceof Error && error.message.includes("404")) {
				throw new ORPCError("NOT_FOUND");
			}
			throw error;
		}
	},

	create: async (input: {
		userId: string;
		name: string;
		slug: string;
		tags: string[];
		locale: Locale;
		data?: ResumeData;
	}): Promise<string> => {
		const apiClient = getAPIClient();
		
		const resumeData = input.data ?? defaultResumeData;
		resumeData.metadata.page.locale = input.locale;

		try {
			const id = await apiClient.create(resumeData);
			return id;
		} catch (error) {
			// Handle slug conflict if FastAPI returns it
			if (error instanceof Error && error.message.includes("already exists")) {
				throw new ORPCError("RESUME_SLUG_ALREADY_EXISTS", { status: 400 });
			}
			throw error;
		}
	},

	update: async (input: {
		id: string;
		userId: string;
		name?: string;
		slug?: string;
		tags?: string[];
		data?: ResumeData;
		isPublic?: boolean;
	}): Promise<void> => {
		const apiClient = getAPIClient();
		
		// Check if resume is locked
		try {
			const resume = await apiClient.getById(input.id);
			if (resume.isLocked) {
				throw new ORPCError("RESUME_LOCKED");
			}
		} catch (error) {
			if (error instanceof ORPCError && error.message === "RESUME_LOCKED") {
				throw error;
			}
			// Continue if resume not found - let FastAPI handle it
		}

		// Update data if provided
		if (input.data) {
			try {
				await apiClient.update(input.id, input.data);
			} catch (error) {
				if (error instanceof Error && error.message.includes("already exists")) {
					throw new ORPCError("RESUME_SLUG_ALREADY_EXISTS", { status: 400 });
				}
				throw error;
			}
		}
		
		// Note: FastAPI doesn't support updating name, slug, tags, isPublic separately
		// These would need to be added to the FastAPI backend if needed
	},

	setLocked: async (input: { id: string; userId: string; isLocked: boolean }): Promise<void> => {
		// FastAPI doesn't support locking - no-op
		// Could be implemented in FastAPI if needed
	},

	delete: async (input: { id: string; userId: string }): Promise<void> => {
		const apiClient = getAPIClient();
		const storageService = getStorageService();

		// Check if resume is locked before deleting
		try {
			const resume = await apiClient.getById(input.id);
			if (resume.isLocked) {
				throw new ORPCError("RESUME_LOCKED");
			}
		} catch (error) {
			if (error instanceof ORPCError && error.message === "RESUME_LOCKED") {
				throw error;
			}
			// Continue if resume not found - let FastAPI handle it
		}

		// Delete screenshots and PDFs
		const deleteScreenshotsPromise = storageService.delete(`uploads/${input.userId}/screenshots/${input.id}`);
		const deletePdfsPromise = storageService.delete(`uploads/${input.userId}/pdfs/${input.id}`);

		// Delete resume from FastAPI
		const deleteResumePromise = apiClient.delete(input.id);

		await Promise.allSettled([deleteResumePromise, deleteScreenshotsPromise, deletePdfsPromise]);
	},
};
