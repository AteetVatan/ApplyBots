"use client";

import { Bookmark, Send, MessageSquare, Trophy } from "lucide-react";
import type { GroupedApplicationsResponse } from "@/lib/api";

interface StatsBarProps {
  data: GroupedApplicationsResponse | undefined;
  isLoading: boolean;
}

const STAGE_CONFIG = [
  {
    key: "saved" as const,
    label: "Saved",
    icon: Bookmark,
    color: "text-warning-500",
    bgColor: "bg-warning-500/10",
    borderColor: "border-warning-500/30",
  },
  {
    key: "applied" as const,
    label: "Applied",
    icon: Send,
    color: "text-primary-400",
    bgColor: "bg-primary-500/10",
    borderColor: "border-primary-500/30",
  },
  {
    key: "interviewing" as const,
    label: "Interviewing",
    icon: MessageSquare,
    color: "text-accent-500",
    bgColor: "bg-accent-500/10",
    borderColor: "border-accent-500/30",
  },
  {
    key: "offer" as const,
    label: "Offer",
    icon: Trophy,
    color: "text-success-500",
    bgColor: "bg-success-500/10",
    borderColor: "border-success-500/30",
  },
] as const;

export function StatsBar({ data, isLoading }: StatsBarProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {STAGE_CONFIG.map((stage) => {
        const count = data?.stages[stage.key]?.count ?? 0;

        return (
          <div
            key={stage.key}
            className={`glass-card p-4 border ${stage.borderColor} transition-all hover:scale-[1.02]`}
          >
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-xl ${stage.bgColor}`}>
                <stage.icon className={`w-5 h-5 ${stage.color}`} />
              </div>
              <div>
                <p className="text-neutral-400 text-sm">{stage.label}</p>
                <p className={`text-2xl font-display font-bold ${stage.color}`}>
                  {isLoading ? (
                    <span className="inline-block w-8 h-7 bg-neutral-800 rounded animate-pulse" />
                  ) : (
                    count
                  )}
                </p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
