import { t } from "@lingui/core/macro";
import { Trans } from "@lingui/react/macro";
import { ClipboardIcon } from "@phosphor-icons/react";
import { useCallback, useMemo } from "react";
import { toast } from "sonner";
import { useCopyToClipboard } from "usehooks-ts";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useResumeStore } from "@/components/resume/store/resume";
import { SectionBase } from "../shared/section-base";

export function SharingSectionBuilder() {
	const [_, copyToClipboard] = useCopyToClipboard();
	
	// Use Zustand store instead of ORPC query - the resume is already loaded
	const resume = useResumeStore((state) => state.resume);

	const publicUrl = useMemo(() => {
		if (!resume?.id) return "";
		return `${window.location.origin}/resume/${resume.id}`;
	}, [resume?.id]);

	const onCopyUrl = useCallback(async () => {
		await copyToClipboard(publicUrl);
		toast.success(t`A link to your resume has been copied to clipboard.`);
	}, [publicUrl, copyToClipboard]);

	const onTogglePublic = useCallback(
		async (_checked: boolean) => {
			// Sharing functionality is not supported in embedded mode
			toast.info(t`Sharing is not available in embedded mode.`);
		},
		[],
	);

	// Don't render if resume not loaded yet
	if (!resume) return null;

	return (
		<SectionBase type="sharing" className="space-y-4">
			<div className="flex items-center gap-x-4">
				<Switch
					id="sharing-switch"
					checked={resume.isPublic ?? false}
					onCheckedChange={(checked) => void onTogglePublic(checked)}
					disabled // Disabled in embedded mode
				/>

				<Label htmlFor="sharing-switch" className="my-2 flex flex-col items-start gap-y-1 font-normal">
					<p className="font-medium">
						<Trans>Allow Public Access</Trans>
					</p>

					<span className="text-muted-foreground text-xs">
						<Trans>Anyone with the link can view and download the resume.</Trans>
					</span>
				</Label>
			</div>

			{resume.isPublic && (
				<div className="space-y-4 rounded-md border p-4">
					<div className="grid gap-2">
						<Label htmlFor="sharing-url">URL</Label>

						<div className="flex items-center gap-x-2">
							<Input readOnly id="sharing-url" value={publicUrl} />

							<Button size="icon" variant="ghost" onClick={onCopyUrl}>
								<ClipboardIcon />
							</Button>
						</div>
					</div>

					<p className="text-muted-foreground text-xs">
						<Trans>Share this link with anyone you want to view your resume.</Trans>
					</p>
				</div>
			)}
		</SectionBase>
	);
}
