"use client";

import { useState } from "react";
import { useApplications, useApproveApplication } from "@/hooks/useApplications";
import { formatRelativeTime, getStatusColor, getMatchScoreColor } from "@/lib/utils";
import { CheckCircle, XCircle, Loader2, FileText } from "lucide-react";

// #region agent log
const debugLog = (location: string, message: string, data: Record<string, unknown>) => {
  fetch('http://127.0.0.1:7242/ingest/478687fd-7ff3-4069-9a5d-c1e34f5138df',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location,message,data,timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'H3'})}).catch(()=>{});
};
// #endregion

const statusTabs = [
  { value: "", label: "All" },
  { value: "pending_review", label: "Pending Review" },
  { value: "approved", label: "Approved" },
  { value: "submitted", label: "Submitted" },
  { value: "failed", label: "Failed" },
];

export default function ApplicationsPage() {
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const { data, isLoading, error } = useApplications({ status: status || undefined, page });
  const approveApplication = useApproveApplication();

  // #region agent log
  debugLog('applications/page.tsx:render', 'Applications page render', { 
    status, page, isLoading, total: data?.total, error: error?.message 
  });
  // #endregion

  const handleApprove = async (id: string) => {
    // #region agent log
    debugLog('applications/page.tsx:approve', 'Approving application', { id });
    // #endregion
    try {
      await approveApplication.mutateAsync(id);
      // #region agent log
      debugLog('applications/page.tsx:approveSuccess', 'Application approved', { id });
      // #endregion
    } catch (error) {
      // #region agent log
      debugLog('applications/page.tsx:approveError', 'Approve failed', { id, error: error instanceof Error ? error.message : 'Unknown' });
      // #endregion
      console.error("Failed to approve application:", error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-display font-bold">Applications</h1>
        <p className="text-neutral-400">
          Track and manage your job applications
        </p>
      </div>

      {/* Status Tabs */}
      <div className="flex flex-wrap gap-2">
        {statusTabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => {
              setStatus(tab.value);
              setPage(1);
            }}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
              status === tab.value
                ? "bg-primary-600 text-white"
                : "bg-neutral-800 text-neutral-400 hover:bg-neutral-700"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Application List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      ) : data?.items.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <FileText className="w-12 h-12 text-neutral-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">No applications found</h3>
          <p className="text-neutral-400">
            {status
              ? "No applications with this status."
              : "Start applying to jobs to see your applications here."}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {data?.items.map((app) => (
            <div
              key={app.id}
              className="glass-card p-6 hover:border-primary-500/30 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold">{app.job_title}</h3>
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(app.status)}`}>
                      {app.status.replace("_", " ")}
                    </span>
                  </div>
                  <p className="text-neutral-300 mb-3">{app.company}</p>
                  
                  <div className="flex items-center gap-4 text-sm text-neutral-400">
                    <span className={`font-medium ${getMatchScoreColor(app.match_score)}`}>
                      {app.match_score}% match
                    </span>
                    <span>Applied {formatRelativeTime(app.created_at)}</span>
                    {app.submitted_at && (
                      <span>Submitted {formatRelativeTime(app.submitted_at)}</span>
                    )}
                  </div>
                </div>

                {app.status === "pending_review" && (
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleApprove(app.id)}
                      disabled={approveApplication.isPending}
                      className="flex items-center gap-2 px-4 py-2 bg-success-500 hover:bg-success-600 rounded-xl font-medium transition-colors disabled:opacity-50"
                    >
                      {approveApplication.isPending ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <CheckCircle className="w-4 h-4" />
                      )}
                      Approve
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2 bg-neutral-700 hover:bg-neutral-600 rounded-xl font-medium transition-colors">
                      <XCircle className="w-4 h-4" />
                      Reject
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Pagination */}
          {data && data.total > 20 && (
            <div className="flex items-center justify-center gap-4 pt-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg disabled:opacity-50 transition-colors"
              >
                Previous
              </button>
              <span className="text-neutral-400">
                Page {page} of {Math.ceil(data.total / 20)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={!data.has_more}
                className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg disabled:opacity-50 transition-colors"
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
