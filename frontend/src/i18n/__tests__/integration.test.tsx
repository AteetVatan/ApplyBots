import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { I18nProvider, useT, useLocale } from "../next";
import type { Locale } from "../core/types";

// Test component that uses the translation hook
function TranslatedText({ translationKey }: { translationKey: Parameters<ReturnType<typeof useT>>[0] }) {
  const t = useT();
  return <span data-testid="translated">{t(translationKey)}</span>;
}

// Test component that uses interpolation
function InterpolatedText({
  translationKey,
  params,
}: {
  translationKey: Parameters<ReturnType<typeof useT>>[0];
  params: Record<string, string | number>;
}) {
  const t = useT();
  return <span data-testid="interpolated">{t(translationKey, params)}</span>;
}

// Test component that displays current locale
function LocaleDisplay() {
  const locale = useLocale();
  return <span data-testid="locale">{locale}</span>;
}

// Wrapper component for tests
function TestWrapper({
  locale,
  children,
}: {
  locale: Locale;
  children: React.ReactNode;
}) {
  return <I18nProvider locale={locale}>{children}</I18nProvider>;
}

describe("I18nProvider and useT hook", () => {
  beforeEach(() => {
    vi.spyOn(console, "warn").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("basic translation", () => {
    it("renders English translation", () => {
      // Arrange & Act
      render(
        <TestWrapper locale="en">
          <TranslatedText translationKey="nav.home" />
        </TestWrapper>
      );

      // Assert
      expect(screen.getByTestId("translated")).toHaveTextContent("Home");
    });

    it("renders German translation", () => {
      // Arrange & Act
      render(
        <TestWrapper locale="de">
          <TranslatedText translationKey="nav.home" />
        </TestWrapper>
      );

      // Assert
      expect(screen.getByTestId("translated")).toHaveTextContent("Startseite");
    });

    it("renders nested translations", () => {
      // Arrange & Act
      render(
        <TestWrapper locale="en">
          <TranslatedText translationKey="auth.login.submitButton" />
        </TestWrapper>
      );

      // Assert
      expect(screen.getByTestId("translated")).toHaveTextContent("Sign in");
    });
  });

  describe("interpolation", () => {
    it("interpolates parameters in English", () => {
      // Arrange & Act
      render(
        <TestWrapper locale="en">
          <InterpolatedText
            translationKey="profile.greeting"
            params={{ name: "John" }}
          />
        </TestWrapper>
      );

      // Assert
      expect(screen.getByTestId("interpolated")).toHaveTextContent("Hello, John!");
    });

    it("interpolates parameters in German", () => {
      // Arrange & Act
      render(
        <TestWrapper locale="de">
          <InterpolatedText
            translationKey="profile.greeting"
            params={{ name: "Hans" }}
          />
        </TestWrapper>
      );

      // Assert
      expect(screen.getByTestId("interpolated")).toHaveTextContent("Hallo, Hans!");
    });

    it("interpolates numeric values", () => {
      // Arrange & Act
      render(
        <TestWrapper locale="en">
          <InterpolatedText
            translationKey="dashboard.topMatches.matchScore"
            params={{ score: 87 }}
          />
        </TestWrapper>
      );

      // Assert
      expect(screen.getByTestId("interpolated")).toHaveTextContent("87% Match");
    });
  });

  describe("useLocale hook", () => {
    it("returns English locale", () => {
      // Arrange & Act
      render(
        <TestWrapper locale="en">
          <LocaleDisplay />
        </TestWrapper>
      );

      // Assert
      expect(screen.getByTestId("locale")).toHaveTextContent("en");
    });

    it("returns German locale", () => {
      // Arrange & Act
      render(
        <TestWrapper locale="de">
          <LocaleDisplay />
        </TestWrapper>
      );

      // Assert
      expect(screen.getByTestId("locale")).toHaveTextContent("de");
    });
  });

  describe("locale switching", () => {
    it("re-renders with new translations when locale changes", () => {
      // Arrange
      const { rerender } = render(
        <TestWrapper locale="en">
          <TranslatedText translationKey="common.save" />
        </TestWrapper>
      );

      // Assert initial English
      expect(screen.getByTestId("translated")).toHaveTextContent("Save");

      // Act - Switch to German
      rerender(
        <TestWrapper locale="de">
          <TranslatedText translationKey="common.save" />
        </TestWrapper>
      );

      // Assert German
      expect(screen.getByTestId("translated")).toHaveTextContent("Speichern");
    });
  });

  describe("multiple components", () => {
    it("provides translations to multiple nested components", () => {
      // Arrange & Act
      render(
        <TestWrapper locale="en">
          <div>
            <TranslatedText translationKey="nav.dashboard" />
            <TranslatedText translationKey="nav.jobs" />
            <TranslatedText translationKey="nav.profile" />
          </div>
        </TestWrapper>
      );

      // Assert
      const elements = screen.getAllByTestId("translated");
      expect(elements[0]).toHaveTextContent("Dashboard");
      expect(elements[1]).toHaveTextContent("Jobs");
      expect(elements[2]).toHaveTextContent("Profile");
    });
  });

  describe("fallback without provider", () => {
    it("falls back to default locale when used outside provider", () => {
      // Arrange & Act
      // Using without provider should warn but not crash
      render(<TranslatedText translationKey="nav.home" />);

      // Assert - Should use default locale (en)
      expect(screen.getByTestId("translated")).toHaveTextContent("Home");
      // Note: The warning only appears in development mode
      // In test environment, we just verify the fallback works
    });
  });
});

describe("I18nProvider edge cases", () => {
  it("handles empty children", () => {
    // Arrange & Act
    const { container } = render(
      <I18nProvider locale="en">
        <></>
      </I18nProvider>
    );

    // Assert - Should render without errors
    expect(container).toBeDefined();
  });

  it("handles deeply nested components", () => {
    // Arrange
    function DeepChild() {
      const t = useT();
      return <span data-testid="deep">{t("common.loading")}</span>;
    }

    function Level2() {
      return (
        <div>
          <DeepChild />
        </div>
      );
    }

    function Level1() {
      return (
        <div>
          <Level2 />
        </div>
      );
    }

    // Act
    render(
      <I18nProvider locale="en">
        <Level1 />
      </I18nProvider>
    );

    // Assert
    expect(screen.getByTestId("deep")).toHaveTextContent("Loading...");
  });
});
