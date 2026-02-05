import { extname } from "node:path";
import sharp from "sharp";
import { getStorageClient, type FileInfo } from "@/lib/storage-client";

interface StorageWriteInput {
	key: string;
	data: Uint8Array;
	contentType: string;
}

interface StorageReadResult {
	data: Uint8Array;
	size: number;
	etag?: string;
	lastModified?: Date;
	contentType?: string;
}

interface StorageService {
	list(prefix: string): Promise<FileInfo[]>;
	delete(key: string): Promise<boolean>;
	healthcheck(): Promise<StorageHealthResult>;
}

interface StorageHealthResult {
	status: "healthy" | "unhealthy";
	type: "backend";
	message: string;
	error?: string;
}

const CONTENT_TYPE_MAP: Record<string, string> = {
	".webp": "image/webp",
	".jpg": "image/jpeg",
	".jpeg": "image/jpeg",
	".png": "image/png",
	".gif": "image/gif",
	".svg": "image/svg+xml",
	".pdf": "application/pdf",
};

const DEFAULT_CONTENT_TYPE = "application/octet-stream";

const IMAGE_MIME_TYPES = ["image/gif", "image/png", "image/jpeg", "image/webp"];

// Key builders for different upload types
function buildPictureKey(userId: string): string {
	const timestamp = Date.now();
	return `uploads/${userId}/pictures/${timestamp}.webp`;
}

function buildScreenshotKey(userId: string, resumeId: string): string {
	const timestamp = Date.now();
	return `uploads/${userId}/screenshots/${resumeId}/${timestamp}.webp`;
}

function buildPdfKey(userId: string, resumeId: string): string {
	const timestamp = Date.now();
	return `uploads/${userId}/pdfs/${resumeId}/${timestamp}.pdf`;
}

// Key builders kept for reference but not used directly (backend generates keys)

export function inferContentType(filename: string): string {
	const extension = extname(filename).toLowerCase();
	return CONTENT_TYPE_MAP[extension] ?? DEFAULT_CONTENT_TYPE;
}

export function isImageFile(mimeType: string): boolean {
	return IMAGE_MIME_TYPES.includes(mimeType);
}

export interface ProcessedImage {
	data: Uint8Array;
	contentType: string;
}

export async function processImageForUpload(file: File): Promise<ProcessedImage> {
	const fileBuffer = await file.arrayBuffer();

	const processedBuffer = await sharp(fileBuffer)
		.resize(800, 800, { fit: "inside", withoutEnlargement: true })
		.webp({ preset: "picture" })
		.toBuffer();

	return {
		data: new Uint8Array(processedBuffer),
		contentType: "image/webp",
	};
}

class BackendStorageService implements StorageService {
	async list(prefix: string): Promise<FileInfo[]> {
		const storageClient = getStorageClient();
		return storageClient.listFiles(prefix);
	}

	async delete(key: string): Promise<boolean> {
		const storageClient = getStorageClient();
		try {
			await storageClient.deleteFile(key);
			return true;
		} catch {
			return false;
		}
	}

	async healthcheck(): Promise<StorageHealthResult> {
		const storageClient = getStorageClient();
		try {
			const result = await storageClient.healthCheck();
			return {
				type: "backend",
				status: result.status === "healthy" ? "healthy" : "unhealthy",
				message: result.message,
			};
		} catch (error: unknown) {
			return {
				type: "backend",
				status: "unhealthy",
				message: "Failed to connect to backend storage service.",
				error: error instanceof Error ? error.message : "Unknown error",
			};
		}
	}
}

function createStorageService(): StorageService {
	return new BackendStorageService();
}

let cachedService: StorageService | null = null;

export function getStorageService(): StorageService {
	if (cachedService) return cachedService;

	cachedService = createStorageService();
	return cachedService;
}

// High-level upload types
type UploadType = "picture" | "screenshot" | "pdf";

export interface UploadFileInput {
	userId: string;
	data: Uint8Array;
	contentType: string;
	type: UploadType;
	resumeId?: string;
}

export interface UploadFileResult {
	url: string;
	key: string;
}

export async function uploadFile(input: UploadFileInput): Promise<UploadFileResult> {
	const storageClient = getStorageClient();

	try {
		const result = await storageClient.uploadFileData(
			input.data,
			input.contentType,
			input.type,
			input.resumeId,
		);

		return {
			key: result.key,
			url: result.url,
		};
	} catch (error) {
		throw new Error(`Failed to upload file: ${error instanceof Error ? error.message : String(error)}`);
	}
}
