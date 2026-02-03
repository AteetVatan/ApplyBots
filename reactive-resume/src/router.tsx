import { createRouter } from "@tanstack/react-router";
import { setupRouterSsrQueryIntegration } from "@tanstack/react-router-ssr-query";
import { ErrorScreen } from "./components/layout/error-screen";
import { LoadingScreen } from "./components/layout/loading-screen";
import { NotFoundScreen } from "./components/layout/not-found-screen";
import { getSession } from "./integrations/auth/functions";
import { client, orpc } from "./integrations/orpc/client";
import { getQueryClient } from "./integrations/query/client";
import { routeTree } from "./routeTree.gen";
import { getLocale, loadLocale } from "./utils/locale";
import { getTheme } from "./utils/theme";
import { initAPIClient } from "./lib/api-client";
import { initPostMessageClient } from "./lib/postmessage-client";

export const getRouter = async () => {
	const queryClient = getQueryClient();

	// Initialize API client and postMessage client
	if (typeof window !== "undefined") {
		const baseURL = import.meta.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
		const getAuthToken = () => {
			return localStorage.getItem("ApplyBots_access_token") || null;
		};
		initAPIClient(baseURL, getAuthToken);
		
		const parentOrigin = import.meta.env.NEXT_PUBLIC_IFRAME_PARENT_ORIGIN || "http://localhost:3000";
		initPostMessageClient(parentOrigin);
	}

	const [theme, locale, session, flags] = await Promise.all([
		getTheme(),
		getLocale(),
		getSession().catch(() => null), // Allow auth to fail - we use JWT
		client.flags.get().catch(() => ({})), // Allow flags to fail
	]);

	await loadLocale(locale);

	const router = createRouter({
		routeTree,
		scrollRestoration: true,
		defaultPreload: "intent",
		defaultViewTransition: true,
		defaultStructuralSharing: true,
		defaultErrorComponent: ErrorScreen,
		defaultPendingComponent: LoadingScreen,
		defaultNotFoundComponent: NotFoundScreen,
		context: { orpc, queryClient, theme, locale, session, flags },
	});

	setupRouterSsrQueryIntegration({
		router,
		queryClient,
		handleRedirects: true,
		wrapQueryClient: true,
	});

	return router;
};
