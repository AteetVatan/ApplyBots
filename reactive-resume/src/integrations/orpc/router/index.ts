import { aiRouter } from "./ai";
import { flagsRouter } from "./flags";
import { printerRouter } from "./printer";
import { resumeRouter } from "./resume";
import { statisticsRouter } from "./statistics";
import { storageRouter } from "./storage";

export default {
	ai: aiRouter,
	flags: flagsRouter,
	resume: resumeRouter,
	storage: storageRouter,
	printer: printerRouter,
	statistics: statisticsRouter,
};
