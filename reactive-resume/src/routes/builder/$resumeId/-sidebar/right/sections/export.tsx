import { Trans } from "@lingui/react/macro";
import { FileJsIcon, FilePdfIcon, InfoIcon } from "@phosphor-icons/react";
import { useCallback } from "react";
import { useResumeStore } from "@/components/resume/store/resume";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { downloadWithAnchor, generateFilename } from "@/utils/file";
import { SectionBase } from "../shared/section-base";

export function ExportSectionBuilder() {
	const resume = useResumeStore((state) => state.resume);

	const onDownloadJSON = useCallback(() => {
		const filename = generateFilename(resume.data.basics.name, "json");
		const jsonString = JSON.stringify(resume.data, null, 2);
		const blob = new Blob([jsonString], { type: "application/json" });

		downloadWithAnchor(blob, filename);
	}, [resume]);

	return (
		<SectionBase type="export" className="space-y-4">
			<Button
				variant="outline"
				onClick={onDownloadJSON}
				className="h-auto gap-x-4 whitespace-normal p-4! text-start font-normal active:scale-98"
			>
				<FileJsIcon className="size-6 shrink-0" />
				<div className="flex flex-1 flex-col gap-y-1">
					<h6 className="font-medium">JSON</h6>
					<p className="text-muted-foreground text-xs leading-normal">
						<Trans>
							Download a copy of your resume in JSON format. Use this file for backup or to import your resume into
							other applications, including AI assistants.
						</Trans>
					</p>
				</div>
			</Button>

			<div className="flex items-start gap-x-4 rounded-lg border p-4 opacity-60">
				<FilePdfIcon className="size-6 shrink-0 text-muted-foreground" />
				<div className="flex flex-1 flex-col gap-y-1">
					<h6 className="font-medium text-muted-foreground">PDF</h6>
					<p className="text-muted-foreground text-xs leading-normal">
						<Trans>
							PDF export is not available in embedded mode. Use the ApplyBots dashboard to export your resume as PDF.
						</Trans>
					</p>
				</div>
			</div>
		</SectionBase>
	);
}
