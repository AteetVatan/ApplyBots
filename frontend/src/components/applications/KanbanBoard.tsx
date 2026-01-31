"use client";

import { useState, useCallback } from "react";
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragStartEvent,
  type DragEndEvent,
  type DragOverEvent,
} from "@dnd-kit/core";
import { sortableKeyboardCoordinates } from "@dnd-kit/sortable";
import { StageColumn } from "./StageColumn";
import { ApplicationCard } from "./ApplicationCard";
import { useUpdateStage } from "@/hooks/useApplications";
import type { Application, ApplicationStage, GroupedApplicationsResponse } from "@/lib/api";

// Ordered stages for display (excluding rejected)
const STAGES: ApplicationStage[] = ["saved", "applied", "interviewing", "offer"];

interface KanbanBoardProps {
  data: GroupedApplicationsResponse;
  onCardClick: (application: Application) => void;
}

export function KanbanBoard({ data, onCardClick }: KanbanBoardProps) {
  const [activeId, setActiveId] = useState<string | null>(null);
  const [overId, setOverId] = useState<string | null>(null);
  const updateStage = useUpdateStage();

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  // Find active application across all stages
  const findApplication = useCallback(
    (id: string): Application | undefined => {
      for (const stage of STAGES) {
        const found = data.stages[stage]?.items.find((app) => app.id === id);
        if (found) return found;
      }
      return undefined;
    },
    [data]
  );

  const activeApplication = activeId ? findApplication(activeId) : null;

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  };

  const handleDragOver = (event: DragOverEvent) => {
    const { over } = event;
    setOverId(over?.id as string | null);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    setActiveId(null);
    setOverId(null);

    if (!over) return;

    const activeApp = findApplication(active.id as string);
    if (!activeApp) return;

    // Determine target stage
    let targetStage: ApplicationStage | null = null;

    // Check if dropped on a stage column
    if (STAGES.includes(over.id as ApplicationStage)) {
      targetStage = over.id as ApplicationStage;
    } else {
      // Dropped on another card - find its stage
      for (const stage of STAGES) {
        if (data.stages[stage]?.items.some((app) => app.id === over.id)) {
          targetStage = stage;
          break;
        }
      }
    }

    // Only update if moving to a different stage
    if (targetStage && targetStage !== activeApp.stage) {
      updateStage.mutate({
        id: activeApp.id,
        stage: targetStage,
      });
    }
  };

  const handleDragCancel = () => {
    setActiveId(null);
    setOverId(null);
  };

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragOver={handleDragOver}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {STAGES.map((stage) => (
          <StageColumn
            key={stage}
            stage={stage}
            applications={data.stages[stage]?.items ?? []}
            onCardClick={onCardClick}
            isOver={overId === stage}
          />
        ))}
      </div>

      {/* Drag overlay - renders the dragged card */}
      <DragOverlay dropAnimation={null}>
        {activeApplication ? (
          <div className="w-[280px]">
            <ApplicationCard
              application={activeApplication}
              onClick={() => {}}
              isDragging
            />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
