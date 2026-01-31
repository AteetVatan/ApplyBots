"use client";

import { useDroppable } from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { motion, AnimatePresence } from "framer-motion";
import { Bookmark, Send, MessageSquare, Trophy, Plus } from "lucide-react";
import { ApplicationCard } from "./ApplicationCard";
import type { Application, ApplicationStage } from "@/lib/api";

interface StageColumnProps {
  stage: ApplicationStage;
  applications: Application[];
  onCardClick: (application: Application) => void;
  isOver?: boolean;
}

const STAGE_CONFIG: Record<
  ApplicationStage,
  {
    label: string;
    icon: typeof Bookmark;
    color: string;
    bgColor: string;
    borderColor: string;
  }
> = {
  saved: {
    label: "Saved",
    icon: Bookmark,
    color: "text-warning-500",
    bgColor: "bg-warning-500/10",
    borderColor: "border-warning-500/30",
  },
  applied: {
    label: "Applied",
    icon: Send,
    color: "text-primary-400",
    bgColor: "bg-primary-500/10",
    borderColor: "border-primary-500/30",
  },
  interviewing: {
    label: "Interviewing",
    icon: MessageSquare,
    color: "text-accent-500",
    bgColor: "bg-accent-500/10",
    borderColor: "border-accent-500/30",
  },
  offer: {
    label: "Offer",
    icon: Trophy,
    color: "text-success-500",
    bgColor: "bg-success-500/10",
    borderColor: "border-success-500/30",
  },
  rejected: {
    label: "Rejected",
    icon: Bookmark,
    color: "text-neutral-500",
    bgColor: "bg-neutral-500/10",
    borderColor: "border-neutral-500/30",
  },
};

export function StageColumn({
  stage,
  applications,
  onCardClick,
  isOver,
}: StageColumnProps) {
  const { setNodeRef } = useDroppable({ id: stage });
  const config = STAGE_CONFIG[stage];
  const Icon = config.icon;

  return (
    <div
      ref={setNodeRef}
      className={`
        flex flex-col h-full min-h-[400px] rounded-2xl
        bg-neutral-900/30 border transition-all duration-200
        ${isOver ? `border-2 ${config.borderColor} ${config.bgColor}` : "border-neutral-800/50"}
      `}
    >
      {/* Header */}
      <div className="p-4 border-b border-neutral-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className={`p-1.5 rounded-lg ${config.bgColor}`}>
              <Icon className={`w-4 h-4 ${config.color}`} />
            </div>
            <h3 className="font-medium text-neutral-200">{config.label}</h3>
            <span
              className={`px-2 py-0.5 rounded-full text-xs font-medium ${config.bgColor} ${config.color}`}
            >
              {applications.length}
            </span>
          </div>
        </div>
      </div>

      {/* Cards */}
      <div className="flex-1 p-3 overflow-y-auto">
        <SortableContext
          items={applications.map((a) => a.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-3">
            <AnimatePresence mode="popLayout">
              {applications.map((application) => (
                <motion.div
                  key={application.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ duration: 0.2 }}
                >
                  <ApplicationCard
                    application={application}
                    onClick={() => onCardClick(application)}
                  />
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </SortableContext>

        {/* Empty state */}
        {applications.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full py-8 text-center">
            <div className={`p-3 rounded-xl ${config.bgColor} mb-3`}>
              <Icon className={`w-6 h-6 ${config.color} opacity-50`} />
            </div>
            <p className="text-sm text-neutral-500">
              No applications in {config.label.toLowerCase()}
            </p>
            <p className="text-xs text-neutral-600 mt-1">
              Drag applications here
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
