import { createFileRoute, redirect } from "@tanstack/react-router";
import { createServerFn } from "@tanstack/react-start";
import { zodValidator } from "@tanstack/zod-adapter";
import { useEffect } from "react";
import { z } from "zod";
import { LoadingScreen } from "@/components/layout/loading-screen";
import { ResumePreview } from "@/components/resume/preview";
import { useResumeStore } from "@/components/resume/store/resume";
import { getORPCClient } from "@/integrations/orpc/client";

const searchSchema = z.object({
	token: z.string().catch(""),
	service_token: z.string().optional(),
});

// Server-only function for token verification
// This ensures env vars are only accessed on server
const verifyTokenServerFn = createServerFn({ method: "GET" })
	.inputValidator(z.object({ token: z.string(), resumeId: z.string() }))
	.handler(async ({ data }) => {
		const { env } = await import("@/utils/env");
		const { verifyPrinterToken } = await import("@/utils/printer-token");

		if (env.FLAG_DEBUG_PRINTER) return { valid: true };

		try {
			const tokenResumeId = verifyPrinterToken(data.token);
			if (tokenResumeId !== data.resumeId) {
				return { valid: false };
			}
			return { valid: true };
		} catch {
			return { valid: false };
		}
	});

// Server-only function for loading resume data
const loadResumeServerFn = createServerFn({ method: "GET" })
	.inputValidator(z.object({ resumeId: z.string(), serviceToken: z.string().optional() }))
	.handler(async ({ data }) => {
		const client = getORPCClient();
		const resume = await client.resume.getByIdForPrinter({
			id: data.resumeId,
			serviceToken: data.serviceToken,
		});
		return resume;
	});

export const Route = createFileRoute("/printer/$resumeId")({
	component: RouteComponent,
	validateSearch: zodValidator(searchSchema),
	beforeLoad: async ({ params, search }) => {
		// Guard against undefined search during client hydration
		const token = search?.token ?? "";
		const result = await verifyTokenServerFn({ data: { token, resumeId: params.resumeId } });
		if (!result.valid) {
			throw redirect({ to: "/", search: {}, throw: true });
		}
		// Pass serviceToken to loader via context
		return { serviceToken: search?.service_token };
	},
	loader: async ({ params, context }) => {
		// Get serviceToken from beforeLoad context (more reliable than search in loader)
		const serviceToken = context.serviceToken as string | undefined;
		const resume = await loadResumeServerFn({
			data: { resumeId: params.resumeId, serviceToken },
		});
		return { resume };
	},
});

function RouteComponent() {
	const { resume } = Route.useLoaderData();

	const isReady = useResumeStore((state) => state.isReady);
	const initialize = useResumeStore((state) => state.initialize);

	useEffect(() => {
		if (!resume) return;
		initialize(resume);
		return () => initialize(null);
	}, [resume, initialize]);

	if (!isReady) return <LoadingScreen />;

	return <ResumePreview pageClassName="print:w-full!" />;
}
