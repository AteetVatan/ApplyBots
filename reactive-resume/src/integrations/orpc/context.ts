import { ORPCError, os } from "@orpc/server";
import { env } from "@/utils/env";
import type { Locale } from "@/utils/locale";
import type { MinimalUser } from "@/types/user";
import { decodeJWT } from "@/utils/jwt";

interface ORPCContext {
	locale: Locale;
	reqHeaders?: Headers;
}

async function getUserFromHeaders(headers: Headers): Promise<MinimalUser | null> {
	try {
		const authHeader = headers.get("Authorization");
		if (!authHeader?.startsWith("Bearer ")) return null;

		const token = authHeader.substring(7);
		const decoded = decodeJWT(token);

		if (!decoded?.user_id) return null;

		return { id: decoded.user_id };
	} catch (error) {
		console.warn("Failed to get user from headers:", error);
		return null;
	}
}

const base = os.$context<ORPCContext>();

export const publicProcedure = base.use(async ({ context, next }) => {
	const headers = context.reqHeaders ?? new Headers();

	// Try to get user from JWT token (optional for public procedures)
	const user = await getUserFromHeaders(headers);

	return next({
		context: {
			...context,
			user: user ?? null,
		},
	});
});

export const protectedProcedure = publicProcedure.use(async ({ context, next }) => {
	if (!context.user) {
		throw new ORPCError("UNAUTHORIZED", {
			message: "Authentication required",
		});
	}

	return next({
		context: {
			...context,
			user: context.user,
		},
	});
});

/**
 * Server-only procedure that can only be called from server-side code (e.g., loaders).
 * Rejects requests from the browser with a 401 UNAUTHORIZED error.
 */
export const serverOnlyProcedure = publicProcedure.use(async ({ context, next }) => {
	const headers = context.reqHeaders ?? new Headers();

	// Check for the custom header that indicates this is a server-side call
	// Server-side calls using createRouterClient have this header set
	const isServerSideCall = env.FLAG_DEBUG_PRINTER || headers.get("x-server-side-call") === "true";

	// If the header is not present, this is a client-side HTTP request - reject it
	if (!isServerSideCall) {
		throw new ORPCError("UNAUTHORIZED", {
			message: "This endpoint can only be called from server-side code",
		});
	}

	return next({ context });
});
