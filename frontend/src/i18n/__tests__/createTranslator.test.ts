import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { createTranslator } from "../core/createTranslator";

describe("createTranslator", () => {
  beforeEach(() => {
    vi.spyOn(console, "warn").mockImplementation(() => {});
    vi.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("basic translation", () => {
    it("returns correct translation for simple key", () => {
      // Arrange
      const t = createTranslator("en");

      // Act
      const result = t("nav.home");

      // Assert
      expect(result).toBe("Home");
    });

    it("returns correct translation for nested key", () => {
      // Arrange
      const t = createTranslator("en");

      // Act
      const result = t("auth.login.title");

      // Assert
      expect(result).toBe("Welcome back");
    });

    it("returns correct translation for deeply nested key", () => {
      // Arrange
      const t = createTranslator("en");

      // Act
      const result = t("dashboard.stats.jobsMatched");

      // Assert
      expect(result).toBe("Jobs Matched");
    });
  });

  describe("interpolation", () => {
    it("interpolates parameters correctly", () => {
      // Arrange
      const t = createTranslator("en");

      // Act
      const result = t("profile.greeting", { name: "Ateet" });

      // Assert
      expect(result).toBe("Hello, Ateet!");
    });

    it("interpolates score parameter", () => {
      // Arrange
      const t = createTranslator("en");

      // Act
      const result = t("applications.card.matchScore", { score: "85" });

      // Assert
      expect(result).toBe("85% match");
    });

    it("handles numeric interpolation", () => {
      // Arrange
      const t = createTranslator("en");

      // Act
      const result = t("dashboard.topMatches.matchScore", { score: 92 });

      // Assert
      expect(result).toBe("92% Match");
    });
  });

  describe("locale switching", () => {
    it("returns German translation for de locale", () => {
      // Arrange
      const t = createTranslator("de");

      // Act
      const result = t("nav.home");

      // Assert
      expect(result).toBe("Startseite");
    });

    it("returns German nested translation", () => {
      // Arrange
      const t = createTranslator("de");

      // Act
      const result = t("auth.login.title");

      // Assert
      expect(result).toBe("Willkommen zurück");
    });

    it("interpolates in German", () => {
      // Arrange
      const t = createTranslator("de");

      // Act
      const result = t("profile.greeting", { name: "Ateet" });

      // Assert
      expect(result).toBe("Hallo, Ateet!");
    });
  });

  describe("all locales have same keys", () => {
    it("both en and de have the same nav keys", () => {
      // Arrange
      const tEn = createTranslator("en");
      const tDe = createTranslator("de");

      // Act & Assert - these should all work without errors
      expect(tEn("nav.home")).toBe("Home");
      expect(tDe("nav.home")).toBe("Startseite");
      expect(tEn("nav.dashboard")).toBe("Dashboard");
      expect(tDe("nav.dashboard")).toBe("Dashboard");
    });

    it("creates translator without errors for valid locale", () => {
      // Arrange & Act
      const tEn = createTranslator("en");
      const tDe = createTranslator("de");

      // Assert
      expect(typeof tEn).toBe("function");
      expect(typeof tDe).toBe("function");
    });
  });

  describe("type safety", () => {
    it("accepts valid translation keys", () => {
      // Arrange
      const t = createTranslator("en");

      // Act - These should compile without errors
      const nav = t("nav.home");
      const auth = t("auth.login.title");
      const common = t("common.loading");

      // Assert
      expect(nav).toBe("Home");
      expect(auth).toBe("Welcome back");
      expect(common).toBe("Loading...");
    });

    // Type-level test: Invalid keys should cause TypeScript errors
    // The following would fail type-checking if uncommented:
    // const t = createTranslator("en");
    // t("invalid.key"); // Type error!
  });

  describe("edge cases", () => {
    it("handles keys at different nesting levels", () => {
      // Arrange
      const t = createTranslator("en");

      // Act & Assert
      // Top-level namespace
      expect(t("common.loading")).toBe("Loading...");
      // Two levels deep
      expect(t("nav.home")).toBe("Home");
      // Three levels deep
      expect(t("auth.login.title")).toBe("Welcome back");
      // Four levels deep
      expect(t("dashboard.stats.jobsMatched")).toBe("Jobs Matched");
    });

    it("handles templates without interpolation", () => {
      // Arrange
      const t = createTranslator("en");

      // Act
      const result = t("common.save");

      // Assert
      expect(result).toBe("Save");
    });

    it("handles complex interpolation in nested keys", () => {
      // Arrange
      const t = createTranslator("en");

      // Act
      const result = t("dashboard.welcomeWithName", { name: "John" });

      // Assert
      expect(result).toBe("Welcome back, John!");
    });
  });
});
