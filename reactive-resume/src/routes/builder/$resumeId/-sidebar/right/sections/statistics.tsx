import { Trans } from "@lingui/react/macro";
import { InfoIcon } from "@phosphor-icons/react";
import { Accordion, AccordionContent, AccordionItem } from "@/components/ui/accordion";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { SectionBase } from "../shared/section-base";

export function StatisticsSectionBuilder() {
	// Statistics are not available in embedded mode (requires ORPC backend)
	// Show informational message instead
	return (
		<SectionBase type="statistics">
			<Accordion collapsible type="single" defaultValue="info">
				<AccordionItem value="info">
					<AccordionContent className="pb-0">
						<Alert>
							<InfoIcon />
							<AlertTitle>
								<Trans>Statistics Not Available</Trans>
							</AlertTitle>
							<AlertDescription>
								<Trans>
									Resume statistics are not available in embedded mode. Use the main ApplyBots dashboard
									to track your resume's performance.
								</Trans>
							</AlertDescription>
						</Alert>
					</AccordionContent>
				</AccordionItem>
			</Accordion>
		</SectionBase>
	);
}
