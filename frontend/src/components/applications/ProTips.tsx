"use client";

import { Lightbulb, X } from "lucide-react";
import { useState } from "react";
import type { GroupedApplicationsResponse } from "@/lib/api";

interface ProTipsProps {
  data: GroupedApplicationsResponse | undefined;
}

interface Tip {
  id: string;
  message: string;
  condition: (data: GroupedApplicationsResponse) => boolean;
}

const TIPS: Tip[] = [
  {
    id: "empty-board",
    message:
      "Start by saving jobs you're interested in. Use the Jobs tab to discover opportunities!",
    condition: (data) => data.total === 0,
  },
  {
    id: "has-saved",
    message:
      "You have saved jobs ready to apply. Review them and start your applications!",
    condition: (data) =>
      data.stages.saved.count > 0 && data.stages.applied.count === 0,
  },
  {
    id: "applied-no-interviews",
    message:
      "Follow up on applications after 1 week if you haven't heard back. Persistence pays off!",
    condition: (data) =>
      data.stages.applied.count >= 3 && data.stages.interviewing.count === 0,
  },
  {
    id: "has-interviews",
    message:
      "Prepare for your interviews by researching the company and practicing common questions.",
    condition: (data) => data.stages.interviewing.count > 0,
  },
  {
    id: "has-offers",
    message:
      "Congratulations on your offers! Compare compensation, culture, and growth opportunities carefully.",
    condition: (data) => data.stages.offer.count > 0,
  },
  {
    id: "many-applied",
    message:
      "Great momentum! Consider focusing on quality over quantity - tailor each application.",
    condition: (data) => data.stages.applied.count >= 10,
  },
];

export function ProTips({ data }: ProTipsProps) {
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  if (!data) return null;

  // Find the first applicable tip that hasn't been dismissed
  const activeTip = TIPS.find(
    (tip) => !dismissed.has(tip.id) && tip.condition(data)
  );

  if (!activeTip) return null;

  const handleDismiss = () => {
    setDismissed((prev) => new Set(prev).add(activeTip.id));
  };

  return (
    <div className="glass-card p-4 border border-primary-500/20 bg-primary-500/5">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-xl bg-primary-500/10 shrink-0">
          <Lightbulb className="w-5 h-5 text-primary-400" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-primary-400 mb-1">Pro Tip</p>
          <p className="text-neutral-300 text-sm">{activeTip.message}</p>
        </div>
        <button
          onClick={handleDismiss}
          className="p-1 rounded-lg hover:bg-neutral-800 transition-colors shrink-0"
          aria-label="Dismiss tip"
        >
          <X className="w-4 h-4 text-neutral-500" />
        </button>
      </div>
    </div>
  );
}
