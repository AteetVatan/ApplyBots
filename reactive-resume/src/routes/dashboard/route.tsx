import { createFileRoute, Outlet, redirect, useRouter } from "@tanstack/react-router";
import { SidebarProvider } from "@/components/ui/sidebar";
import { getDashboardSidebarServerFn, setDashboardSidebarServerFn } from "./-components/functions";
import { DashboardSidebar } from "./-components/sidebar";
import { getTokenFromStorage, validateToken } from "@/utils/jwt";

export const Route = createFileRoute("/dashboard")({
	component: RouteComponent,
	beforeLoad: async () => {
		const token = getTokenFromStorage();

		if (!token || !validateToken(token)) {
			// Notify parent iframe
			if (typeof window !== "undefined" && window.parent !== window) {
				window.parent.postMessage({ type: "auth-required" }, "*");
			}
			// Redirect to home page (not /auth/login - route doesn't exist)
			throw redirect({ to: "/", replace: true });
		}

		return {};
	},
	loader: async () => {
		const sidebarState = await getDashboardSidebarServerFn();
		return { sidebarState };
	},
});

function RouteComponent() {
	const router = useRouter();
	const { sidebarState } = Route.useLoaderData();

	const handleSidebarOpenChange = (open: boolean) => {
		setDashboardSidebarServerFn({ data: open }).then(() => {
			router.invalidate();
		});
	};

	return (
		<SidebarProvider open={sidebarState} onOpenChange={handleSidebarOpenChange}>
			<DashboardSidebar />

			<main className="@container flex-1 p-4 md:ps-2">
				<Outlet />
			</main>
		</SidebarProvider>
	);
}
