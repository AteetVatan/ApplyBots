/**
 * Timeline section for the application detail drawer.
 */

"use client";

import { Calendar, Send } from "lucide-react";
import { formatDate, formatRelativeTime } from "@/lib/utils";

interface DrawerTimelineProps {
  createdAt: string;
  submittedAt: string | null;
  stageUpdatedAt?: string | null;
}

export function DrawerTimeline({
  createdAt,
  submittedAt,
  stageUpdatedAt,
}: DrawerTimelineProps) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-medium text-neutral-400 uppercase tracking-wider">
        Timeline
      </h3>
      <div className="space-y-2">
        <div className="flex items-center gap-3 text-sm">
          <Calendar className="w-4 h-4 text-neutral-500" />
          <span className="text-neutral-400">Created:</span>
          <span className="text-neutral-200">{formatDate(createdAt)}</span>
        </div>
        {submittedAt && (
          <div className="flex items-center gap-3 text-sm">
            <Send className="w-4 h-4 text-neutral-500" />
            <span className="text-neutral-400">Submitted:</span>
            <span className="text-neutral-200">{formatDate(submittedAt)}</span>
          </div>
        )}
        {stageUpdatedAt && (
          <div className="flex items-center gap-3 text-sm">
            <Calendar className="w-4 h-4 text-neutral-500" />
            <span className="text-neutral-400">Stage updated:</span>
            <span className="text-neutral-200">{formatRelativeTime(stageUpdatedAt)}</span>
          </div>
        )}
      </div>
    </div>
  );
}
