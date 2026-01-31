import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatsBar } from "@/components/applications/StatsBar";
import type { GroupedApplicationsResponse } from "@/lib/api";

const mockData: GroupedApplicationsResponse = {
  stages: {
    saved: { items: [], count: 5 },
    applied: { items: [], count: 12 },
    interviewing: { items: [], count: 3 },
    offer: { items: [], count: 1 },
  },
  total: 21,
};

describe("StatsBar", () => {
  it("renders all stage labels", () => {
    // Act
    render(<StatsBar data={mockData} isLoading={false} />);

    // Assert
    expect(screen.getByText("Saved")).toBeInTheDocument();
    expect(screen.getByText("Applied")).toBeInTheDocument();
    expect(screen.getByText("Interviewing")).toBeInTheDocument();
    expect(screen.getByText("Offer")).toBeInTheDocument();
  });

  it("displays correct counts", () => {
    // Act
    render(<StatsBar data={mockData} isLoading={false} />);

    // Assert
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("12")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
  });

  it("shows loading state", () => {
    // Act
    render(<StatsBar data={undefined} isLoading={true} />);

    // Assert - should not show any numbers when loading
    expect(screen.queryByText("5")).not.toBeInTheDocument();
    expect(screen.queryByText("12")).not.toBeInTheDocument();
  });

  it("displays zero counts when data is undefined", () => {
    // Act
    render(<StatsBar data={undefined} isLoading={false} />);

    // Assert - should show 0 for all stages
    const zeros = screen.getAllByText("0");
    expect(zeros).toHaveLength(4);
  });
});
