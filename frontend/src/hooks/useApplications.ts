"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  api,
  type ApplicationListResponse,
  type ApplicationStage,
  type GroupedApplicationsResponse,
  type Application,
} from "@/lib/api";

interface UseApplicationsParams {
  status?: string;
  page?: number;
}

export function useApplications({ status, page = 1 }: UseApplicationsParams = {}) {
  return useQuery<ApplicationListResponse>({
    queryKey: ["applications", { status, page }],
    queryFn: () => api.getApplications({ status, page }),
  });
}

interface UseGroupedApplicationsParams {
  search?: string;
}

export function useGroupedApplications({
  search,
}: UseGroupedApplicationsParams = {}) {
  return useQuery<GroupedApplicationsResponse>({
    queryKey: ["applications", "grouped", { search }],
    queryFn: () => api.getGroupedApplications({ search }),
  });
}

export function useCreateApplication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ jobId, resumeId }: { jobId: string; resumeId?: string }) =>
      api.createApplication(jobId, resumeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
  });
}

export function useApproveApplication() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => api.approveApplication(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
  });
}

interface UpdateStageVariables {
  id: string;
  stage: ApplicationStage;
}

export function useUpdateStage() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, stage }: UpdateStageVariables) =>
      api.updateApplicationStage(id, stage),
    onMutate: async ({ id, stage }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ["applications", "grouped"] });

      // Snapshot previous value
      const previousData = queryClient.getQueryData<GroupedApplicationsResponse>([
        "applications",
        "grouped",
        {},
      ]);

      // Optimistically update
      if (previousData) {
        const newData = { ...previousData };
        let movedApp: Application | null = null;
        let sourceStage: ApplicationStage | null = null;

        // Find and remove from current stage
        for (const [stageKey, stageItems] of Object.entries(newData.stages)) {
          const idx = stageItems.items.findIndex((app) => app.id === id);
          if (idx !== -1) {
            movedApp = { ...stageItems.items[idx], stage };
            sourceStage = stageKey as ApplicationStage;
            stageItems.items.splice(idx, 1);
            stageItems.count--;
            break;
          }
        }

        // Add to new stage
        if (movedApp && newData.stages[stage]) {
          newData.stages[stage].items.unshift(movedApp);
          newData.stages[stage].count++;
        }

        queryClient.setQueryData(["applications", "grouped", {}], newData);
      }

      return { previousData };
    },
    onError: (_err, _vars, context) => {
      // Rollback on error
      if (context?.previousData) {
        queryClient.setQueryData(
          ["applications", "grouped", {}],
          context.previousData
        );
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
  });
}

interface AddNoteVariables {
  applicationId: string;
  content: string;
}

export function useAddNote() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ applicationId, content }: AddNoteVariables) =>
      api.addApplicationNote(applicationId, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
  });
}

interface DeleteNoteVariables {
  applicationId: string;
  noteId: string;
}

export function useDeleteNote() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ applicationId, noteId }: DeleteNoteVariables) =>
      api.deleteApplicationNote(applicationId, noteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
  });
}
