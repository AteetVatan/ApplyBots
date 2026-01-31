"use client";

import { useQuery } from "@tanstack/react-query";
import { api, type JobListResponse } from "@/lib/api";

interface UseJobsParams {
  page?: number;
  limit?: number;
}

export function useJobs({ page = 1, limit = 20 }: UseJobsParams = {}) {
  return useQuery<JobListResponse>({
    queryKey: ["jobs", { page, limit }],
    queryFn: () => api.getJobs({ page, limit }),
  });
}

export function useJob(id: string) {
  return useQuery({
    queryKey: ["job", id],
    queryFn: () => api.getJob(id),
    enabled: !!id,
  });
}
