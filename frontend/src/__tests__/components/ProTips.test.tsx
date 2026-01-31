import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ProTips } from "@/components/applications/ProTips";
import type { GroupedApplicationsResponse } from "@/lib/api";

function createMockData(
  overrides: Partial<{
    savedCount: number;
    appliedCount: number;
    interviewingCount: number;
    offerCount: number;
  }> = {}
): GroupedApplicationsResponse {
  const {
    savedCount = 0,
    appliedCount = 0,
    interviewingCount = 0,
    offerCount = 0,
  } = overrides;

  return {
    stages: {
      saved: { items: [], count: savedCount },
      applied: { items: [], count: appliedCount },
      interviewing: { items: [], count: interviewingCount },
      offer: { items: [], count: offerCount },
    },
    total: savedCount + appliedCount + interviewingCount + offerCount,
  };
}

describe("ProTips", () => {
  it("shows empty board tip when total is 0", () => {
    // Arrange
    const data = createMockData({ savedCount: 0 });

    // Act
    render(<ProTips data={data} />);

    // Assert
    expect(
      screen.getByText(/Start by saving jobs you're interested in/i)
    ).toBeInTheDocument();
  });

  it("shows saved jobs tip when has saved but no applied", () => {
    // Arrange
    const data = createMockData({ savedCount: 3, appliedCount: 0 });

    // Act
    render(<ProTips data={data} />);

    // Assert
    expect(
      screen.getByText(/You have saved jobs ready to apply/i)
    ).toBeInTheDocument();
  });

  it("shows follow up tip when many applied but no interviews", () => {
    // Arrange
    const data = createMockData({ appliedCount: 5, interviewingCount: 0 });

    // Act
    render(<ProTips data={data} />);

    // Assert
    expect(
      screen.getByText(/Follow up on applications after 1 week/i)
    ).toBeInTheDocument();
  });

  it("shows interview prep tip when has interviews", () => {
    // Arrange
    const data = createMockData({ interviewingCount: 2 });

    // Act
    render(<ProTips data={data} />);

    // Assert
    expect(
      screen.getByText(/Prepare for your interviews/i)
    ).toBeInTheDocument();
  });

  it("shows congratulations tip when has offers", () => {
    // Arrange
    const data = createMockData({ offerCount: 1 });

    // Act
    render(<ProTips data={data} />);

    // Assert
    expect(screen.getByText(/Congratulations on your offers/i)).toBeInTheDocument();
  });

  it("can dismiss a tip", () => {
    // Arrange
    const data = createMockData({ savedCount: 0 });
    render(<ProTips data={data} />);

    // Act
    const dismissButton = screen.getByRole("button", { name: /dismiss/i });
    fireEvent.click(dismissButton);

    // Assert - tip should be gone
    expect(
      screen.queryByText(/Start by saving jobs/i)
    ).not.toBeInTheDocument();
  });

  it("renders nothing when data is undefined", () => {
    // Act
    const { container } = render(<ProTips data={undefined} />);

    // Assert
    expect(container.firstChild).toBeNull();
  });
});
