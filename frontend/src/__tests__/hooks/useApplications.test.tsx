import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useGroupedApplications, useUpdateStage, useAddNote, useDeleteNote } from "@/hooks/useApplications";
import { api } from "@/lib/api";
import type { GroupedApplicationsResponse, Application } from "@/lib/api";
import type { ReactNode } from "react";

// Mock the API
vi.mock("@/lib/api", () => ({
  api: {
    getGroupedApplications: vi.fn(),
    updateApplicationStage: vi.fn(),
    addApplicationNote: vi.fn(),
    deleteApplicationNote: vi.fn(),
  },
}));

const mockApplication: Application = {
  id: "app-1",
  job_id: "job-1",
  job_title: "Software Engineer",
  company: "TechCorp",
  status: "pending_review",
  stage: "saved",
  match_score: 85,
  notes: [],
  created_at: "2026-01-31T10:00:00Z",
  submitted_at: null,
  stage_updated_at: null,
};

const mockGroupedResponse: GroupedApplicationsResponse = {
  stages: {
    saved: { items: [mockApplication], count: 1 },
    applied: { items: [], count: 0 },
    interviewing: { items: [], count: 0 },
    offer: { items: [], count: 0 },
  },
  total: 1,
};

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
}

describe("useGroupedApplications", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetches grouped applications", async () => {
    // Arrange
    vi.mocked(api.getGroupedApplications).mockResolvedValue(mockGroupedResponse);

    // Act
    const { result } = renderHook(() => useGroupedApplications({}), {
      wrapper: createWrapper(),
    });

    // Assert
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockGroupedResponse);
    expect(api.getGroupedApplications).toHaveBeenCalledWith({});
  });

  it("passes search parameter", async () => {
    // Arrange
    vi.mocked(api.getGroupedApplications).mockResolvedValue(mockGroupedResponse);

    // Act
    const { result } = renderHook(
      () => useGroupedApplications({ search: "engineer" }),
      { wrapper: createWrapper() }
    );

    // Assert
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.getGroupedApplications).toHaveBeenCalledWith({
      search: "engineer",
    });
  });
});

describe("useUpdateStage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("updates application stage", async () => {
    // Arrange
    const updatedApp = { ...mockApplication, stage: "applied" as const };
    vi.mocked(api.updateApplicationStage).mockResolvedValue(updatedApp);

    // Act
    const { result } = renderHook(() => useUpdateStage(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ id: "app-1", stage: "applied" });

    // Assert
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.updateApplicationStage).toHaveBeenCalledWith("app-1", "applied");
  });
});

describe("useAddNote", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("adds note to application", async () => {
    // Arrange
    const mockNote = {
      id: "note-1",
      content: "Follow up next week",
      created_at: "2026-01-31T12:00:00Z",
    };
    vi.mocked(api.addApplicationNote).mockResolvedValue(mockNote);

    // Act
    const { result } = renderHook(() => useAddNote(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      applicationId: "app-1",
      content: "Follow up next week",
    });

    // Assert
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.addApplicationNote).toHaveBeenCalledWith(
      "app-1",
      "Follow up next week"
    );
  });
});

describe("useDeleteNote", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("deletes note from application", async () => {
    // Arrange
    vi.mocked(api.deleteApplicationNote).mockResolvedValue(undefined);

    // Act
    const { result } = renderHook(() => useDeleteNote(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({ applicationId: "app-1", noteId: "note-1" });

    // Assert
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(api.deleteApplicationNote).toHaveBeenCalledWith("app-1", "note-1");
  });
});
