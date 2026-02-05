import { createEnv } from "@t3-oss/env-core";
import { z } from "zod";

export const env = createEnv({
	clientPrefix: "VITE_",
	runtimeEnv: process.env,
	emptyStringAsUndefined: true,

	client: {},

	server: {
		// Server
		TZ: z.string().default("Etc/UTC"),
		APP_URL: z.url({ protocol: /https?/ }),
		PRINTER_APP_URL: z.url({ protocol: /https?/ }).optional(),

		// Printer
		PRINTER_ENDPOINT: z.url({ protocol: /^(wss?|https?)$/ }),

		// Storage is now handled by backend API - no S3 configuration needed

		// Feature Flags
		FLAG_DEBUG_PRINTER: z.stringbool().default(false),
	},
});
