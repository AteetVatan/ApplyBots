"use client";

import { useAuth } from "@/providers/AuthProvider";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Briefcase, FileText, CheckCircle, Clock, Loader2 } from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();

  // Fetch real data from API (fetch 5 items to display top 3 on dashboard)
  const { data: jobsData, isLoading: jobsLoading } = useQuery({
    queryKey: ["jobs", { page: 1, limit: 5 }],
    queryFn: () => api.getJobs({ page: 1, limit: 5 }),
  });

  const { data: applicationsData, isLoading: appsLoading } = useQuery({
    queryKey: ["applications", { page: 1 }],
    queryFn: () => api.getApplications({ page: 1 }),
  });

  // Calculate real stats from applications
  const pendingCount = applicationsData?.items.filter(a => a.status === "pending_review").length ?? 0;
  const submittedCount = applicationsData?.items.filter(a => a.status === "submitted").length ?? 0;

  const stats = [
    { label: "Jobs Matched", value: jobsLoading ? "..." : String(jobsData?.total ?? 0), icon: Briefcase, color: "text-primary-400" },
    { label: "Applications", value: appsLoading ? "..." : String(applicationsData?.total ?? 0), icon: FileText, color: "text-accent-400" },
    { label: "Submitted", value: appsLoading ? "..." : String(submittedCount), icon: CheckCircle, color: "text-success-500" },
    { label: "Pending Review", value: appsLoading ? "..." : String(pendingCount), icon: Clock, color: "text-warning-500" },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-display font-bold">
          Welcome back{user?.fullName ? `, ${user.fullName.split(" ")[0]}` : ""}!
        </h1>
        <p className="text-neutral-400 mt-1">
          Here&apos;s an overview of your job search
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => (
          <div key={stat.label} className="glass-card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-neutral-400 text-sm">{stat.label}</p>
                <p className="text-3xl font-bold mt-1">{stat.value}</p>
              </div>
              <div className={`w-12 h-12 rounded-xl bg-neutral-800 flex items-center justify-center ${stat.color}`}>
                <stat.icon className="w-6 h-6" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Applications</h2>
          <div className="space-y-4">
            {appsLoading ? (
              <div className="flex justify-center py-4">
                <Loader2 className="w-6 h-6 animate-spin text-primary-500" />
              </div>
            ) : applicationsData?.items.slice(0, 3).map((app) => (
              <div key={app.id} className="flex items-center justify-between p-4 bg-neutral-800/50 rounded-xl">
                <div>
                  <p className="font-medium">{app.job_title}</p>
                  <p className="text-sm text-neutral-400">{app.company}</p>
                </div>
                <span className={`px-3 py-1 text-sm rounded-full ${
                  app.status === "submitted" ? "bg-success-500/10 text-success-500" :
                  app.status === "pending_review" ? "bg-warning-500/10 text-warning-500" :
                  "bg-neutral-500/10 text-neutral-400"
                }`}>
                  {app.status.replace("_", " ")}
                </span>
              </div>
            ))}
            {!appsLoading && (!applicationsData?.items.length) && (
              <p className="text-neutral-500 text-center py-4">No applications yet</p>
            )}
          </div>
        </div>

        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold mb-4">Top Job Matches</h2>
          <div className="space-y-4">
            {jobsLoading ? (
              <div className="flex justify-center py-4">
                <Loader2 className="w-6 h-6 animate-spin text-primary-500" />
              </div>
            ) : jobsData?.items.slice(0, 3).map((job) => (
              <div key={job.id} className="flex items-center justify-between p-4 bg-neutral-800/50 rounded-xl">
                <div>
                  <p className="font-medium">{job.title}</p>
                  <p className="text-sm text-neutral-400">{job.company}</p>
                </div>
                <span className={`px-3 py-1 text-sm rounded-full ${
                  (job.match_score ?? 0) >= 80 ? "bg-success-500/10 text-success-500" :
                  (job.match_score ?? 0) >= 60 ? "bg-primary-500/10 text-primary-400" :
                  "bg-neutral-500/10 text-neutral-400"
                }`}>
                  {job.match_score !== null ? `${job.match_score}% Match` : "N/A"}
                </span>
              </div>
            ))}
            {!jobsLoading && (!jobsData?.items.length) && (
              <p className="text-neutral-500 text-center py-4">No jobs found</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
