import { Trans } from "@lingui/react/macro";
import { FileJsIcon, FilePdfIcon, SpinnerGapIcon } from "@phosphor-icons/react";
import { useCallback, useState } from "react";
import { toast } from "sonner";
import { useResumeStore } from "@/components/resume/store/resume";
import { Button } from "@/components/ui/button";
import { downloadWithAnchor, generateFilename } from "@/utils/file";
import { getTokenFromStorage } from "@/utils/jwt";
import { SectionBase } from "../shared/section-base";

export function ExportSectionBuilder() {
	const resume = useResumeStore((state) => state.resume);
	const [isPDFGenerating, setIsPDFGenerating] = useState(false);

	const onDownloadJSON = useCallback(() => {
		const filename = generateFilename(resume.data.basics.name, "json");
		const jsonString = JSON.stringify(resume.data, null, 2);
		const blob = new Blob([jsonString], { type: "application/json" });

		downloadWithAnchor(blob, filename);
	}, [resume]);

	const onDownloadPDF = useCallback(async () => {
		if (!resume.id) {
			toast.error("Please save your resume before exporting");
			return;
		}

		setIsPDFGenerating(true);

		try {
			const token = getTokenFromStorage();
			// Get API URL from the same origin or use environment variable
			const apiUrl = import.meta.env.VITE_API_URL || `${window.location.origin.replace(":3002", ":8080")}`;

			const response = await fetch(`${apiUrl}/api/v1/resume-builder/drafts/${resume.id}/export-pdf`, {
				method: "POST",
				headers: {
					Authorization: `Bearer ${token}`,
				},
			});

			if (!response.ok) {
				const error = await response.json().catch(() => ({ detail: "Failed to generate PDF" }));
				throw new Error(error.detail || "Failed to generate PDF");
			}

			const { url } = await response.json();

			// Download the PDF
			const filename = generateFilename(resume.data.basics.name, "pdf");
			const link = document.createElement("a");
			link.href = url;
			link.download = filename;
			link.target = "_blank";
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);

			toast.success("PDF downloaded successfully");
		} catch (error) {
			toast.error(error instanceof Error ? error.message : "Failed to export PDF");
		} finally {
			setIsPDFGenerating(false);
		}
	}, [resume]);

	return (
		<SectionBase type="export" className="space-y-4">
			{/* JSON Export Button */}
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

			{/* PDF Export Button */}
			<Button
				variant="outline"
				onClick={onDownloadPDF}
				disabled={isPDFGenerating || !resume.id}
				className="h-auto gap-x-4 whitespace-normal p-4! text-start font-normal active:scale-98"
			>
				{isPDFGenerating ? (
					<SpinnerGapIcon className="size-6 shrink-0 animate-spin" />
				) : (
					<FilePdfIcon className="size-6 shrink-0" />
				)}
				<div className="flex flex-1 flex-col gap-y-1">
					<h6 className="font-medium">PDF</h6>
					<p className="text-muted-foreground text-xs leading-normal">
						{isPDFGenerating ? (
							<Trans>Generating PDF... This may take a few seconds.</Trans>
						) : (
							<Trans>Export your resume as a high-quality PDF with selectable text, perfect for ATS systems.</Trans>
						)}
					</p>
				</div>
			</Button>
		</SectionBase>
	);
}
