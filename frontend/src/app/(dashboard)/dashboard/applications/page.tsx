"use client";

import { useState, useCallback } from "react";
import { Loader2, FileText } from "lucide-react";
import { useGroupedApplications } from "@/hooks/useApplications";
import {
  KanbanBoard,
  StatsBar,
  ProTips,
  SearchFilter,
  DetailDrawer,
} from "@/components/applications";
import type { Application } from "@/lib/api";

export default function ApplicationsPage() {
  const [search, setSearch] = useState("");
  const [selectedApplication, setSelectedApplication] =
    useState<Application | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const { data, isLoading, error } = useGroupedApplications({
    search: search || undefined,
  });

  const handleCardClick = useCallback((application: Application) => {
    setSelectedApplication(application);
    setDrawerOpen(true);
  }, []);

  const handleDrawerClose = useCallback((open: boolean) => {
    setDrawerOpen(open);
    if (!open) {
      // Delay clearing selection for exit animation
      setTimeout(() => setSelectedApplication(null), 300);
    }
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold">Application Tracker</h1>
          <p className="text-neutral-400">
            Manage your job applications pipeline
          </p>
        </div>
      </div>

      {/* Stats Bar */}
      <StatsBar data={data} isLoading={isLoading} />

      {/* Pro Tips */}
      <ProTips data={data} />

      {/* Search Filter */}
      <SearchFilter value={search} onChange={setSearch} />

      {/* Kanban Board */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      ) : error ? (
        <div className="glass-card p-12 text-center">
          <div className="text-error-500 mb-4">
            <FileText className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Failed to load applications</h3>
          <p className="text-neutral-400">
            {error instanceof Error ? error.message : "An error occurred"}
          </p>
        </div>
      ) : data ? (
        data.total === 0 && !search ? (
          <div className="glass-card p-12 text-center">
            <FileText className="w-12 h-12 text-neutral-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No applications yet</h3>
            <p className="text-neutral-400">
              Start applying to jobs to see your applications here.
            </p>
          </div>
        ) : (
          <KanbanBoard data={data} onCardClick={handleCardClick} />
        )
      ) : null}

      {/* Detail Drawer */}
      <DetailDrawer
        application={selectedApplication}
        open={drawerOpen}
        onOpenChange={handleDrawerClose}
      />
    </div>
  );
}
