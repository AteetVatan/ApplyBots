"use client";

import { useState } from "react";
import Link from "next/link";
import { useJobs } from "@/hooks/useJobs";
import { useCreateApplication } from "@/hooks/useApplications";
import { formatSalary, formatRelativeTime, getMatchScoreColor } from "@/lib/utils";
import { MapPin, Briefcase, DollarSign, Clock, Plus, Loader2, RefreshCw, Sparkles, ClipboardPaste } from "lucide-react";
import { api } from "@/lib/api";

export default function JobsPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading, refetch, isFetching } = useJobs({ page, limit: 20 });
  const createApplication = useCreateApplication();
  const [refreshing, setRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [applyingJobId, setApplyingJobId] = useState<string | null>(null);

  const handleRefresh = async () => {
    setRefreshing(true);
    setRefreshError(null);
    try {
      await api.refreshJobs();
      setTimeout(() => {
        refetch();
        setRefreshing(false);
      }, 2000);
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      setRefreshError(errorMsg);
      setRefreshing(false);
    }
  };

  const handleApply = async (jobId: string) => {
    setApplyingJobId(jobId);
    try {
      await createApplication.mutateAsync({ jobId });
    } catch {
      // Error handled by TanStack Query's error state
    } finally {
      setApplyingJobId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold">Job Matches</h1>
          <p className="text-neutral-400">
            {data?.total || 0} jobs matching your profile
          </p>
        </div>
        <div className="flex items-center gap-3">
          {refreshError && (
            <span className="text-sm text-error-500">{refreshError}</span>
          )}
          <Link
            href="/dashboard/jobs/custom/expert-apply"
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-primary-600 hover:from-purple-500 hover:to-primary-500 rounded-xl font-medium transition-all"
          >
            <ClipboardPaste className="w-4 h-4" />
            Paste External JD
          </Link>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-xl transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
            Refresh Jobs
          </button>
        </div>
      </div>

      {/* Job List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      ) : (
        <div className="space-y-4">
          {data?.items.map((job) => (
            <div
              key={job.id}
              className="glass-card p-6 hover:border-primary-500/30 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold">{job.title}</h3>
                    {job.match_score !== null && (
                      <span className={`text-sm font-medium ${getMatchScoreColor(job.match_score)}`}>
                        {job.match_score}% match
                      </span>
                    )}
                  </div>
                  <p className="text-neutral-300 mb-4">{job.company}</p>

                  <div className="flex flex-wrap items-center gap-4 text-sm text-neutral-400">
                    {job.location && (
                      <span className="flex items-center gap-1.5">
                        <MapPin className="w-4 h-4" />
                        {job.location}
                      </span>
                    )}
                    {job.remote && (
                      <span className="flex items-center gap-1.5">
                        <Briefcase className="w-4 h-4" />
                        Remote
                      </span>
                    )}
                    <span className="flex items-center gap-1.5">
                      <DollarSign className="w-4 h-4" />
                      {formatSalary(job.salary_min, job.salary_max)}
                    </span>
                    {job.posted_at && (
                      <span className="flex items-center gap-1.5">
                        <Clock className="w-4 h-4" />
                        {formatRelativeTime(job.posted_at)}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleApply(job.id)}
                    disabled={applyingJobId === job.id}
                    className="flex items-center gap-2 px-4 py-2 bg-neutral-700 hover:bg-neutral-600 rounded-xl font-medium transition-colors disabled:opacity-50"
                  >
                    {applyingJobId === job.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Plus className="w-4 h-4" />
                    )}
                    Quick Apply
                  </button>
                  <Link
                    href={`/dashboard/jobs/${job.id}/expert-apply`}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary-600 to-purple-600 hover:from-primary-500 hover:to-purple-500 rounded-xl font-medium transition-all"
                  >
                    <Sparkles className="w-4 h-4" />
                    Expert Apply
                  </Link>
                </div>
              </div>
            </div>
          ))}

          {/* Pagination */}
          {data && data.total > 20 && (
            <div className="flex items-center justify-center gap-4 pt-4">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1 || isFetching}
                className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 rounded-lg disabled:opacity-50 transition-colors"
              >
                Previous
              </button>
              <span className="text-neutral-400">
                Page {page} of {Math.ceil(data.total / 20)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={!data.has_more || isFetching}
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
