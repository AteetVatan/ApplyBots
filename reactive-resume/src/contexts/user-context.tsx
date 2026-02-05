/**
 * User Context for global user display info
 * Receives user info from frontend via postMessage
 */
import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { getPostMessageClient } from "@/lib/postmessage-client";
import type { UserDisplay } from "@/types/user";

interface UserContextValue {
	user: UserDisplay | null;
	isLoading: boolean;
}

const UserContext = createContext<UserContextValue>({
	user: null,
	isLoading: true,
});

export function UserProvider({ children }: { children: ReactNode }) {
	const [user, setUser] = useState<UserDisplay | null>(null);
	const [isLoading, setIsLoading] = useState(true);

	useEffect(() => {
		const postMessageClient = getPostMessageClient();

		// Listen for user info from parent
		const unsubscribe = postMessageClient.on("set-user-info", (message) => {
			const msg = message as { type: "set-user-info"; payload: UserDisplay };
			if (msg.payload) {
				setUser(msg.payload);
				setIsLoading(false);
			}
		});

		// Request user info from parent immediately
		postMessageClient.send({ type: "request-user-info" });

		// Set loading to false after timeout if no response
		const timeout = setTimeout(() => {
			setIsLoading(false);
		}, 2000);

		return () => {
			clearTimeout(timeout);
			unsubscribe();
		};
	}, []); // Empty dependency array - only run once on mount

	return <UserContext.Provider value={{ user, isLoading }}>{children}</UserContext.Provider>;
}

export function useUserDisplay() {
	return useContext(UserContext);
}
