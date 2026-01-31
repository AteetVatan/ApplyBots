"use client";

import { useEffect } from "react";
import { AlertTriangle, RefreshCw, LayoutDashboard } from "lucide-react";
import Link from "next/link";

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

/**
 * Dashboard-specific error boundary.
 * Catches errors in dashboard routes and provides contextual recovery.
 */
export default function DashboardError({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log error to monitoring service in production
    if (process.env.NODE_ENV === "development") {
      console.error("Dashboard error boundary caught:", error);
    }
  }, [error]);

  return (
    <div className="flex items-center justify-center min-h-[60vh] p-6">
      <div className="max-w-md w-full text-center">
        {/* Error Icon */}
        <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-error-500/10 flex items-center justify-center">
          <AlertTriangle className="w-8 h-8 text-error-500" />
        </div>

        {/* Error Message */}
        <h1 className="text-2xl font-display font-bold text-white mb-3">
          Something went wrong
        </h1>
        <p className="text-neutral-400 mb-8">
          We encountered an error while loading this page. Please try again.
        </p>

        {/* Error Details (development only) */}
        {process.env.NODE_ENV === "development" && error.message && (
          <div className="mb-6 p-4 bg-neutral-900 border border-neutral-800 rounded-xl text-left">
            <p className="text-xs text-neutral-500 mb-1">Error details:</p>
            <p className="text-sm text-error-400 font-mono break-all">
              {error.message}
            </p>
            {error.digest && (
              <p className="text-xs text-neutral-600 mt-2">
                Digest: {error.digest}
              </p>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={reset}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-500 rounded-xl font-medium transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Try Again
          </button>
          <Link
            href="/dashboard"
            className="flex items-center justify-center gap-2 px-6 py-3 bg-neutral-800 hover:bg-neutral-700 rounded-xl font-medium transition-colors"
          >
            <LayoutDashboard className="w-4 h-4" />
            Back to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
