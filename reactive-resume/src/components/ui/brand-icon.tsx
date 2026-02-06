import { FileTextIcon } from "@phosphor-icons/react";
import { cn } from "@/utils/style";

type Props = React.ComponentProps<"div"> & {
	variant?: "logo" | "icon";
};

export function BrandIcon({ variant = "logo", className, ...props }: Props) {
	// Use Phosphor icon instead of external SVG files to avoid loading issues
	return (
		<div className={cn("flex items-center justify-center size-12", className)} {...props}>
			<FileTextIcon className="size-8 text-primary" weight="duotone" />
		</div>
	);
}
