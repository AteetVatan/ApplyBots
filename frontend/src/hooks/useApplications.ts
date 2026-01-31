"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type ApplicationListResponse } from "@/lib/api";

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
