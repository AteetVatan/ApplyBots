import type { Nitro } from "nitro/types";
import { migrateDatabase } from "../scripts/database/migrate.js";

export default async function migratePlugin(nitro: Nitro) {
	nitro.hooks.hook("ready", async () => {
		try {
			await migrateDatabase();
		} catch (error) {
			console.error("🚨 Failed to run database migrations on server startup:", error);
			// Don't throw - allow server to continue even if migrations fail
			// This prevents the server from crashing if migrations are already applied
		}
	});
}
