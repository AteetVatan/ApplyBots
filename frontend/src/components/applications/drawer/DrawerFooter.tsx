/**
 * Footer actions for the application detail drawer.
 */

"use client";

import { ExternalLink, CheckCircle, XCircle, Loader2 } from "lucide-react";

interface DrawerFooterProps {
  jobId: string;
  status: string;
  onApprove: () => void;
  isApproving: boolean;
}

export function DrawerFooter({
  jobId,
  status,
  onApprove,
  isApproving,
}: DrawerFooterProps) {
  const handleViewJob = () => {
    window.open(`/dashboard/jobs?id=${jobId}`, "_blank");
  };

  return (
    <div className="p-6 border-t border-neutral-800 space-y-3">
      {status === "pending_review" && (
        <div className="flex gap-2">
          <button
            onClick={onApprove}
            disabled={isApproving}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-success-500 hover:bg-success-600 disabled:opacity-50 rounded-xl font-medium transition-colors"
          >
            {isApproving ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <CheckCircle className="w-4 h-4" />
            )}
            Approve & Submit
          </button>
          <button className="flex items-center justify-center gap-2 px-4 py-3 bg-neutral-700 hover:bg-neutral-600 rounded-xl font-medium transition-colors">
            <XCircle className="w-4 h-4" />
            Reject
          </button>
        </div>
      )}

      <button
        onClick={handleViewJob}
        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-neutral-800 hover:bg-neutral-700 rounded-xl font-medium transition-colors"
      >
        <ExternalLink className="w-4 h-4" />
        View Job Details
      </button>
    </div>
  );
}
