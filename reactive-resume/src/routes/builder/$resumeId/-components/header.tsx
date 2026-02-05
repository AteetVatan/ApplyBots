import { t } from "@lingui/core/macro";
import { Trans } from "@lingui/react/macro";
import {
	CaretDownIcon,
	HouseSimpleIcon,
	LockSimpleIcon,
	SidebarSimpleIcon,
} from "@phosphor-icons/react";
import { toast } from "sonner";
import { useResumeStore } from "@/components/resume/store/resume";
import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { getPostMessageClient } from "@/lib/postmessage-client";
import { useBuilderSidebar } from "../-store/sidebar";

export function BuilderHeader() {
	const name = useResumeStore((state) => state.resume.name);
	const isLocked = useResumeStore((state) => state.resume.isLocked);
	const toggleSidebar = useBuilderSidebar((state) => state.toggleSidebar);

	return (
		<div className="absolute inset-x-0 top-0 z-10 flex h-14 items-center justify-between border-b bg-popover px-1.5">
			<Button size="icon" variant="ghost" onClick={() => toggleSidebar("left")}>
				<SidebarSimpleIcon />
			</Button>

			<div className="flex items-center gap-x-1">
				<Button size="icon" variant="ghost" onClick={() => {
					// In embedded mode, notify parent to navigate back
					const postMessageClient = getPostMessageClient();
					postMessageClient.send({ type: "navigate-back" });
				}}>
					<HouseSimpleIcon />
				</Button>
				<span className="me-2.5 text-muted-foreground">/</span>
				<h2 className="flex-1 truncate font-medium">{name}</h2>
				{isLocked && <LockSimpleIcon className="ms-2 text-muted-foreground" />}
				<BuilderHeaderDropdown />
			</div>

			<Button size="icon" variant="ghost" onClick={() => toggleSidebar("right")}>
				<SidebarSimpleIcon className="-scale-x-100" />
			</Button>
		</div>
	);
}

function BuilderHeaderDropdown() {
	const id = useResumeStore((state) => state.resume.id);
	const name = useResumeStore((state) => state.resume.name);
	const isLocked = useResumeStore((state) => state.resume.isLocked);

	const handleRename = () => {
		// Renaming is not supported in embedded mode yet
		toast.info(t`Rename is not available in embedded mode. Use the ApplyBots dashboard.`);
	};

	return (
		<DropdownMenu>
			<DropdownMenuTrigger asChild>
				<Button size="icon" variant="ghost">
					<CaretDownIcon />
				</Button>
			</DropdownMenuTrigger>

			<DropdownMenuContent>
				<DropdownMenuItem disabled={isLocked} onSelect={handleRename}>
					<Trans>Resume: {name}</Trans>
				</DropdownMenuItem>
			</DropdownMenuContent>
		</DropdownMenu>
	);
}
