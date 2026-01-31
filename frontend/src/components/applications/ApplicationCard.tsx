"use client";

import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical, MessageSquareText, Building2 } from "lucide-react";
import { formatRelativeTime, getStatusColor, getMatchScoreColor } from "@/lib/utils";
import type { Application } from "@/lib/api";

interface ApplicationCardProps {
  application: Application;
  onClick: () => void;
  isDragging?: boolean;
}

export function ApplicationCard({
  application,
  onClick,
  isDragging,
}: ApplicationCardProps) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging: isSortableDragging,
  } = useSortable({ id: application.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const isCurrentlyDragging = isDragging || isSortableDragging;

  // Get company initial for avatar
  const companyInitial = application.company.charAt(0).toUpperCase();

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={`
        glass-card p-4 cursor-pointer group
        transition-all duration-200
        hover:border-primary-500/30 hover:shadow-lg
        ${isCurrentlyDragging ? "opacity-50 scale-105 shadow-2xl z-50 rotate-2" : ""}
      `}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        {/* Drag handle */}
        <button
          {...attributes}
          {...listeners}
          className="p-1 -ml-1 rounded opacity-0 group-hover:opacity-100 hover:bg-neutral-800 transition-all cursor-grab active:cursor-grabbing"
          onClick={(e) => e.stopPropagation()}
        >
          <GripVertical className="w-4 h-4 text-neutral-500" />
        </button>

        {/* Company avatar */}
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center shrink-0">
          <span className="text-sm font-semibold text-primary-400">
            {companyInitial}
          </span>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-neutral-100 truncate mb-0.5">
            {application.job_title}
          </h4>
          <div className="flex items-center gap-1.5 text-sm text-neutral-400 mb-2">
            <Building2 className="w-3.5 h-3.5" />
            <span className="truncate">{application.company}</span>
          </div>

          {/* Footer with badges */}
          <div className="flex items-center flex-wrap gap-2">
            {/* Match score */}
            <span
              className={`text-xs font-medium ${getMatchScoreColor(
                application.match_score
              )}`}
            >
              {application.match_score}% match
            </span>

            {/* Status badge */}
            <span
              className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                application.status
              )}`}
            >
              {application.status.replace("_", " ")}
            </span>

            {/* Notes indicator */}
            {application.notes.length > 0 && (
              <span className="flex items-center gap-1 text-xs text-neutral-500">
                <MessageSquareText className="w-3 h-3" />
                {application.notes.length}
              </span>
            )}
          </div>

          {/* Time */}
          <p className="text-xs text-neutral-500 mt-2">
            {formatRelativeTime(application.created_at)}
          </p>
        </div>
      </div>
    </div>
  );
}
