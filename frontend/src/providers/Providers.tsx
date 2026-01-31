"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactNode, useState } from "react";
import { AuthProvider } from "./AuthProvider";
import { I18nProvider, type Locale, DEFAULT_LOCALE } from "@/i18n";

interface ProvidersProps {
  children: ReactNode;
  /** Locale passed from server component (layout) */
  locale?: Locale;
}

export function Providers({ children, locale = DEFAULT_LOCALE }: ProvidersProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <I18nProvider locale={locale}>
        <AuthProvider>{children}</AuthProvider>
      </I18nProvider>
    </QueryClientProvider>
  );
}
