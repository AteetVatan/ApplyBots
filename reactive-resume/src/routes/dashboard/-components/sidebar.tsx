import type { MessageDescriptor } from "@lingui/core";
import { msg } from "@lingui/core/macro";
import { useLingui } from "@lingui/react";
import { Trans } from "@lingui/react/macro";
import {
	BrainIcon,
	GearSixIcon,
	ReadCvLogoIcon,
} from "@phosphor-icons/react";
import { Link } from "@tanstack/react-router";
import { AnimatePresence, motion } from "motion/react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { BrandIcon } from "@/components/ui/brand-icon";
import { Copyright } from "@/components/ui/copyright";
import {
	Sidebar,
	SidebarContent,
	SidebarFooter,
	SidebarGroup,
	SidebarGroupContent,
	SidebarGroupLabel,
	SidebarHeader,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
	SidebarRail,
	SidebarSeparator,
	useSidebarState,
} from "@/components/ui/sidebar";
import { UserDropdownMenu } from "@/components/user/dropdown-menu";
import { useUserDisplay } from "@/contexts/user-context";
import { getInitials } from "@/utils/string";

type SidebarItem = {
	icon: React.ReactNode;
	label: MessageDescriptor;
	href: React.ComponentProps<typeof Link>["to"];
};

const appSidebarItems = [
	{
		icon: <ReadCvLogoIcon />,
		label: msg`Resumes`,
		href: "/dashboard/resumes",
	},
] as const satisfies SidebarItem[];

const settingsSidebarItems = [
	{
		icon: <GearSixIcon />,
		label: msg`Preferences`,
		href: "/dashboard/settings/preferences",
	},
	{
		icon: <BrainIcon />,
		label: msg`Artificial Intelligence`,
		href: "/dashboard/settings/ai",
	},
] as const satisfies SidebarItem[];

type SidebarItemListProps = {
	items: readonly SidebarItem[];
};

function SidebarItemList({ items }: SidebarItemListProps) {
	const { i18n } = useLingui();

	return (
		<SidebarMenu>
			{items.map((item) => (
				<SidebarMenuItem key={item.href}>
					<SidebarMenuButton asChild title={i18n.t(item.label)}>
						<Link to={item.href} activeProps={{ className: "bg-sidebar-accent" }}>
							{item.icon}
							<span className="shrink-0 transition-[margin,opacity] duration-200 ease-in-out group-data-[collapsible=icon]:-ms-8 group-data-[collapsible=icon]:opacity-0">
								{i18n.t(item.label)}
							</span>
						</Link>
					</SidebarMenuButton>
				</SidebarMenuItem>
			))}
		</SidebarMenu>
	);
}

export function DashboardSidebar() {
	const { state } = useSidebarState();

	return (
		<Sidebar variant="floating" collapsible="icon">
			<SidebarHeader>
				<SidebarMenu>
					<SidebarMenuItem>
						<SidebarMenuButton asChild className="h-auto justify-center">
							<Link to="/">
								<BrandIcon variant="icon" className="size-6" />
							</Link>
						</SidebarMenuButton>
					</SidebarMenuItem>
				</SidebarMenu>
			</SidebarHeader>

			<SidebarSeparator />

			<SidebarContent>
				<SidebarGroup>
					<SidebarGroupLabel>
						<Trans>App</Trans>
					</SidebarGroupLabel>
					<SidebarGroupContent>
						<SidebarItemList items={appSidebarItems} />
					</SidebarGroupContent>
				</SidebarGroup>

				<SidebarGroup>
					<SidebarGroupLabel>
						<Trans>Settings</Trans>
					</SidebarGroupLabel>
					<SidebarGroupContent>
						<SidebarItemList items={settingsSidebarItems} />
					</SidebarGroupContent>
				</SidebarGroup>
			</SidebarContent>

			<SidebarSeparator />

			<SidebarFooter className="gap-y-0">
				<SidebarMenu>
					<SidebarMenuItem>
						<UserDropdownMenu>
							{({ user }) => (
								<SidebarMenuButton className="h-auto gap-x-3 group-data-[collapsible=icon]:p-1!">
									<Avatar className="size-8 shrink-0 transition-all group-data-[collapsible=icon]:size-6">
										<AvatarImage src={user?.image ?? undefined} />
										<AvatarFallback className="group-data-[collapsible=icon]:text-[0.5rem]">
											{user ? getInitials(user.name) : ""}
										</AvatarFallback>
									</Avatar>

									<div className="transition-[margin,opacity] duration-200 ease-in-out group-data-[collapsible=icon]:-ms-8 group-data-[collapsible=icon]:opacity-0">
										<p className="font-medium">{user?.name ?? ""}</p>
										<p className="text-muted-foreground text-xs">{user?.email ?? ""}</p>
									</div>
								</SidebarMenuButton>
							)}
						</UserDropdownMenu>
					</SidebarMenuItem>
				</SidebarMenu>

				<AnimatePresence>
					{state === "expanded" && (
						<motion.div
							key="copyright"
							initial={{ y: 50, height: 0, opacity: 0 }}
							animate={{ y: 0, height: "auto", opacity: 1 }}
							exit={{ y: 50, height: 0, opacity: 0 }}
						>
							<Copyright className="wrap-break-word shrink-0 whitespace-normal p-2" />
						</motion.div>
					)}
				</AnimatePresence>
			</SidebarFooter>

			<SidebarRail />
		</Sidebar>
	);
}
