import "@fontsource-variable/ibm-plex-sans";
import "@phosphor-icons/web/regular/style.css";

import { i18n } from "@lingui/core";
import { I18nProvider } from "@lingui/react";
import { IconContext } from "@phosphor-icons/react";
import type { QueryClient } from "@tanstack/react-query";
import { createRootRouteWithContext, HeadContent, Scripts } from "@tanstack/react-router";
import { MotionConfig } from "motion/react";
import { CommandPalette } from "@/components/command-palette";
import { BreakpointIndicator } from "@/components/layout/breakpoint-indicator";
import { ThemeProvider } from "@/components/theme/provider";
import { Toaster } from "@/components/ui/sonner";
import { DialogManager } from "@/dialogs/manager";
import { ConfirmDialogProvider } from "@/hooks/use-confirm";
import { PromptDialogProvider } from "@/hooks/use-prompt";
import { client, type orpc } from "@/integrations/orpc/client";
import { UserProvider } from "@/contexts/user-context";
import { getPostMessageClient } from "@/lib/postmessage-client";
import { signalAuthReady } from "@/hooks/use-auth-ready";
import { useEffect } from "react";
import type { FeatureFlags } from "@/integrations/orpc/services/flags";
import { getLocale, isRTL, type Locale, loadLocale } from "@/utils/locale";
import { getTheme, type Theme } from "@/utils/theme";
import appCss from "../styles/globals.css?url";

type RouterContext = {
	theme: Theme;
	locale: Locale;
	orpc: typeof orpc;
	queryClient: QueryClient;
	flags: FeatureFlags;
};

const appName = "Reactive Resume";
const tagline = "Resume builder";
const title = `${appName} — ${tagline}`;
const description =
	"Resume builder that simplifies the process of creating, updating, and sharing your resume.";

await loadLocale(await getLocale());

export const Route = createRootRouteWithContext<RouterContext>()({
	shellComponent: RootDocument,
	head: () => {
		const appUrl = process.env.APP_URL ?? "https://rxresu.me/";

		return {
			links: [
				{ rel: "stylesheet", href: appCss },
				// Icons
				{ rel: "icon", href: "/favicon.ico", type: "image/x-icon", sizes: "128x128" },
				{ rel: "icon", href: "/favicon.svg", type: "image/svg+xml", sizes: "256x256 any" },
				{ rel: "apple-touch-icon", href: "/apple-touch-icon-180x180.png", type: "image/png", sizes: "180x180 any" },
				// Manifest
				{ rel: "manifest", href: "/manifest.webmanifest", crossOrigin: "use-credentials" },
			],
			meta: [
				{ title },
				{ charSet: "UTF-8" },
				{ name: "description", content: description },
				{ name: "viewport", content: "width=device-width, initial-scale=1" },
				// Twitter Tags
				{ property: "twitter:image", content: `${appUrl}/opengraph/banner.jpg` },
				{ property: "twitter:card", content: "summary_large_image" },
				{ property: "twitter:title", content: title },
				{ property: "twitter:description", content: description },
				// OpenGraph Tags
				{ property: "og:image", content: `${appUrl}/opengraph/banner.jpg` },
				{ property: "og:site_name", content: appName },
				{ property: "og:title", content: title },
				{ property: "og:description", content: description },
				{ property: "og:url", content: appUrl },
			],
			// Register service worker via script tag
			scripts: [
				{
					children: `
						if('serviceWorker' in navigator) {
							window.addEventListener('load', () => {
								navigator.serviceWorker.register('/sw.js', { scope: '/' })
							})
						}
					`,
				},
			],
		};
	},
	beforeLoad: async () => {
		// Initialize API client, storage client, and postMessage client
		if (typeof window !== "undefined") {
			const { initAPIClient } = await import("@/lib/api-client");
			const { initStorageClient } = await import("@/lib/storage-client");
			const { initPostMessageClient } = await import("@/lib/postmessage-client");
			
			const baseURL = import.meta.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
			const getAuthToken = () => {
				return localStorage.getItem("ApplyBots_access_token") || null;
			};
			initAPIClient(baseURL, getAuthToken);
			initStorageClient(baseURL, getAuthToken);
			
			const parentOrigin = import.meta.env.NEXT_PUBLIC_IFRAME_PARENT_ORIGIN || "http://localhost:3000";
			initPostMessageClient(parentOrigin);
		}

		const [theme, locale, flags] = await Promise.all([
			getTheme(),
			getLocale(),
			client.flags.get().catch(() => ({})), // Allow flags to fail
		]);

		return { theme, locale, flags };
	},
});

type Props = {
	children: React.ReactNode;
};

function RootDocument({ children }: Props) {
	const { theme, locale } = Route.useRouteContext();
	const dir = isRTL(locale) ? "rtl" : "ltr";

	// Setup global postMessage handlers in component (not in beforeLoad)
	useEffect(() => {
		if (typeof window === "undefined") return;

		const postMessageClient = getPostMessageClient();

		// Handle set-auth-token (moved from builder route)
		const unsubscribeSetAuthToken = postMessageClient.on("set-auth-token", (message) => {
			const setAuthTokenMessage = message as { type: "set-auth-token"; payload: { token: string } };
			if (setAuthTokenMessage.payload?.token) {
				localStorage.setItem("ApplyBots_access_token", setAuthTokenMessage.payload.token);
				// Update API client with new token getter
				import("@/lib/api-client").then(({ setAuthTokenGetter }) => {
					setAuthTokenGetter(() => setAuthTokenMessage.payload.token);
				});
				// Signal that auth is ready for API calls
				signalAuthReady();
				// Send acknowledgment to parent that token was received
				postMessageClient.send({ type: "auth-token-received" });
			}
		});

		return () => {
			unsubscribeSetAuthToken();
		};
	}, []);

	return (
		<html suppressHydrationWarning dir={dir} lang={locale} className={theme}>
			<head>
				<HeadContent />
			</head>

			<body>
				<MotionConfig reducedMotion="user">
					<I18nProvider i18n={i18n}>
						<IconContext.Provider value={{ size: 16, weight: "regular" }}>
							<ThemeProvider theme={theme}>
								<UserProvider>
									<ConfirmDialogProvider>
										<PromptDialogProvider>
											{children}

											<DialogManager />
											<CommandPalette />
											<Toaster richColors position="bottom-right" />

											{import.meta.env.DEV && <BreakpointIndicator />}
										</PromptDialogProvider>
									</ConfirmDialogProvider>
								</UserProvider>
							</ThemeProvider>
						</IconContext.Provider>
					</I18nProvider>
				</MotionConfig>

				<Scripts />
			</body>
		</html>
	);
}
