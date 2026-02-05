import { t } from "@lingui/core/macro";
import {
	ArrowUUpLeftIcon,
	ArrowUUpRightIcon,
	CubeFocusIcon,
	FileJsIcon,
	type Icon,
	LinkSimpleIcon,
	MagnifyingGlassMinusIcon,
	MagnifyingGlassPlusIcon,
} from "@phosphor-icons/react";
import { motion } from "motion/react";
import { useCallback, useMemo } from "react";
import { useHotkeys } from "react-hotkeys-hook";
import { useControls } from "react-zoom-pan-pinch";
import { toast } from "sonner";
import { useCopyToClipboard } from "usehooks-ts";
import { useResumeStore, useTemporalStore } from "@/components/resume/store/resume";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { downloadWithAnchor, generateFilename } from "@/utils/file";
import { cn } from "@/utils/style";

export function BuilderDock() {
	const [_, copyToClipboard] = useCopyToClipboard();
	const { zoomIn, zoomOut, centerView } = useControls();

	// Use Zustand store instead of ORPC query - the resume is already loaded
	const resume = useResumeStore((state) => state.resume);

	const { undo, redo, pastStates, futureStates } = useTemporalStore((state) => ({
		undo: state.undo,
		redo: state.redo,
		pastStates: state.pastStates,
		futureStates: state.futureStates,
	}));

	const canUndo = pastStates.length > 1;
	const canRedo = futureStates.length > 0;

	useHotkeys("mod+z", () => undo(), { enabled: canUndo, preventDefault: true });
	useHotkeys(["mod+y", "mod+shift+z"], () => redo(), { enabled: canRedo, preventDefault: true });

	const publicUrl = useMemo(() => {
		if (!resume?.id) return "";
		return `${window.location.origin}/resume/${resume.id}`;
	}, [resume?.id]);

	const onCopyUrl = useCallback(async () => {
		await copyToClipboard(publicUrl);
		toast.success(t`A link to your resume has been copied to clipboard.`);
	}, [publicUrl, copyToClipboard]);

	const onDownloadJSON = useCallback(async () => {
		if (!resume?.data) return;
		const filename = generateFilename(resume.data.basics.name, "json");
		const jsonString = JSON.stringify(resume.data, null, 2);
		const blob = new Blob([jsonString], { type: "application/json" });

		downloadWithAnchor(blob, filename);
	}, [resume?.data]);

	return (
		<div className="fixed inset-x-0 bottom-4 flex items-center justify-center">
			<motion.div
				initial={{ opacity: 0, y: -50 }}
				animate={{ opacity: 0.5, y: 0 }}
				whileHover={{ opacity: 1 }}
				transition={{ duration: 0.2 }}
				className="flex items-center rounded-r-full rounded-l-full bg-popover px-2 shadow-xl"
			>
				<DockIcon
					disabled={!canUndo}
					onClick={() => undo()}
					icon={ArrowUUpLeftIcon}
					title={t({
						context: "'Ctrl' may be replaced with the locale-specific equivalent (e.g. 'Strg' for QWERTZ layouts).",
						message: "Undo (Ctrl+Z)",
					})}
				/>
				<DockIcon
					disabled={!canRedo}
					onClick={() => redo()}
					icon={ArrowUUpRightIcon}
					title={t({
						context: "'Ctrl' may be replaced with the locale-specific equivalent (e.g. 'Strg' for QWERTZ layouts).",
						message: "Redo (Ctrl+Y)",
					})}
				/>
				<div className="mx-1 h-8 w-px bg-border" />
				<DockIcon icon={MagnifyingGlassPlusIcon} title={t`Zoom in`} onClick={() => zoomIn(0.1)} />
				<DockIcon icon={MagnifyingGlassMinusIcon} title={t`Zoom out`} onClick={() => zoomOut(0.1)} />
				<DockIcon icon={CubeFocusIcon} title={t`Center view`} onClick={() => centerView()} />
				<div className="mx-1 h-8 w-px bg-border" />
				<DockIcon icon={LinkSimpleIcon} title={t`Copy URL`} onClick={() => onCopyUrl()} />
				<DockIcon icon={FileJsIcon} title={t`Download JSON`} onClick={() => onDownloadJSON()} />
			</motion.div>
		</div>
	);
}

type DockIconProps = {
	title: string;
	icon: Icon;
	disabled?: boolean;
	onClick: () => void;
	iconClassName?: string;
};

function DockIcon({ icon: Icon, title, disabled, onClick, iconClassName }: DockIconProps) {
	return (
		<Tooltip>
			<TooltipTrigger asChild>
				<Button size="icon" variant="ghost" disabled={disabled} onClick={onClick}>
					<Icon className={cn("size-4", iconClassName)} />
				</Button>
			</TooltipTrigger>
			<TooltipContent side="top" align="center" className="font-medium">
				{title}
			</TooltipContent>
		</Tooltip>
	);
}
