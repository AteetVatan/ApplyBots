import { createFileRoute } from "@tanstack/react-router";
import { printerService } from "@/integrations/orpc/services/printer";
import { getStorageClient } from "@/lib/storage-client";

function isUnhealthy(check: unknown): boolean {
	return (
		!!check &&
		typeof check === "object" &&
		"status" in check &&
		typeof check.status === "string" &&
		check.status === "unhealthy"
	);
}

async function handler() {
	const checks = {
		version: process.env.npm_package_version,
		status: "healthy",
		timestamp: new Date().toISOString(),
		uptime: `${process.uptime().toFixed(2)}s`,
		// Database check removed - this app uses FastAPI backend for data storage
		printer: await checkPrinter(),
		storage: await checkStorage(),
	};

	if (checks.status === "unhealthy" || Object.values(checks).some(isUnhealthy)) {
		checks.status = "unhealthy";
	}

	const headers = new Headers();
	const body = JSON.stringify(checks);
	headers.set("Content-Type", "application/json; charset=UTF-8");
	headers.set("Content-Length", Buffer.byteLength(body, "utf-8").toString());

	return new Response(body, {
		headers,
		status: checks.status === "unhealthy" ? 500 : 200,
	});
}

async function checkPrinter() {
	try {
		const result = await printerService.healthcheck();

		return { status: "healthy", ...result };
	} catch (error) {
		return {
			status: "unhealthy",
			error: error instanceof Error ? error.message : "Unknown error",
		};
	}
}

async function checkStorage() {
	try {
		const storageClient = getStorageClient();
		const result = await storageClient.healthCheck();
		return {
			status: result.status === "healthy" ? "healthy" : "unhealthy",
			type: "backend",
			message: result.message,
		};
	} catch (error) {
		return {
			status: "unhealthy",
			type: "backend",
			message: "Failed to connect to backend storage service.",
			error: error instanceof Error ? error.message : "Unknown error",
		};
	}
}

export const Route = createFileRoute("/api/health")({
	server: {
		handlers: {
			GET: handler,
		},
	},
});
