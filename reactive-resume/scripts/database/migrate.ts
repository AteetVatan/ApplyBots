import { drizzle } from "drizzle-orm/node-postgres";
import { migrate } from "drizzle-orm/node-postgres/migrator";
import { Pool } from "pg";

export async function migrateDatabase() {
	console.log("⌛ Running database migrations...");

	const databaseUrl = process.env.DATABASE_URL;
	if (!databaseUrl) {
		throw new Error("DATABASE_URL environment variable is not set");
	}

	const pool = new Pool({ connectionString: databaseUrl });
	const db = drizzle({ client: pool });

	try {
		await migrate(db, { migrationsFolder: "./migrations" });
		console.log("✅ Database migrations completed");
	} catch (error) {
		console.error("🚨 Database migrations failed:", error);
	} finally {
		await pool.end();
	}
}

if (import.meta.main) {
	await migrateDatabase();
}
