import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import {
  extractParamNames,
  validateParams,
} from "../core/interpolate";

// We need to test interpolate with different NODE_ENV values
// Since NODE_ENV is read at module load time, we test the core functions directly
// and trust that the dev/prod behavior is correctly implemented

describe("extractParamNames", () => {
  it("extracts single parameter", () => {
    // Arrange
    const template = "Hello, {name}!";

    // Act
    const params = extractParamNames(template);

    // Assert
    expect(params).toEqual(["name"]);
  });

  it("extracts multiple parameters", () => {
    // Arrange
    const template = "Hi {first} {last}, welcome!";

    // Act
    const params = extractParamNames(template);

    // Assert
    expect(params).toEqual(["first", "last"]);
  });

  it("returns empty array for no parameters", () => {
    // Arrange
    const template = "Hello, World!";

    // Act
    const params = extractParamNames(template);

    // Assert
    expect(params).toEqual([]);
  });

  it("deduplicates repeated parameters", () => {
    // Arrange
    const template = "Hello {name}, your name is {name}!";

    // Act
    const params = extractParamNames(template);

    // Assert
    expect(params).toEqual(["name"]);
  });

  it("handles parameters with underscores", () => {
    // Arrange
    const template = "User {user_name} has {item_count} items";

    // Act
    const params = extractParamNames(template);

    // Assert
    expect(params).toEqual(["user_name", "item_count"]);
  });
});

describe("validateParams", () => {
  it("returns valid when all params provided", () => {
    // Arrange
    const template = "Hello, {name}!";
    const params = { name: "World" };

    // Act
    const result = validateParams(template, params);

    // Assert
    expect(result.valid).toBe(true);
    expect(result.missing).toEqual([]);
  });

  it("returns missing params when not provided", () => {
    // Arrange
    const template = "Hi {first} {last}!";
    const params = { first: "John" };

    // Act
    const result = validateParams(template, params);

    // Assert
    expect(result.valid).toBe(false);
    expect(result.missing).toEqual(["last"]);
  });

  it("returns valid for templates without params", () => {
    // Arrange
    const template = "Hello, World!";

    // Act
    const result = validateParams(template, undefined);

    // Assert
    expect(result.valid).toBe(true);
    expect(result.missing).toEqual([]);
  });

  it("returns all missing when params is undefined", () => {
    // Arrange
    const template = "Hi {first} {last}!";

    // Act
    const result = validateParams(template, undefined);

    // Assert
    expect(result.valid).toBe(false);
    expect(result.missing).toEqual(["first", "last"]);
  });
});

describe("interpolate (via createTranslator)", () => {
  // Since interpolate behavior depends on NODE_ENV which is evaluated at import time,
  // we test interpolation behavior through the createTranslator function in its own test file.
  // Here we test the pure validation and extraction functions.

  beforeEach(() => {
    vi.spyOn(console, "warn").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // Import interpolate dynamically to test with current NODE_ENV
  it("replaces single parameter", async () => {
    // Arrange
    const { interpolate } = await import("../core/interpolate");
    const template = "Hello, {name}!";
    const params = { name: "World" };

    // Act
    const result = interpolate(template, params, "test.key");

    // Assert
    expect(result).toBe("Hello, World!");
  });

  it("replaces multiple parameters", async () => {
    // Arrange
    const { interpolate } = await import("../core/interpolate");
    const template = "Hi {first} {last}!";
    const params = { first: "John", last: "Doe" };

    // Act
    const result = interpolate(template, params, "test.key");

    // Assert
    expect(result).toBe("Hi John Doe!");
  });

  it("handles numeric values", async () => {
    // Arrange
    const { interpolate } = await import("../core/interpolate");
    const template = "You have {count} items";
    const params = { count: 42 };

    // Act
    const result = interpolate(template, params, "test.key");

    // Assert
    expect(result).toBe("You have 42 items");
  });

  it("returns template unchanged when no params needed and none provided", async () => {
    // Arrange
    const { interpolate } = await import("../core/interpolate");
    const template = "Hello, World!";

    // Act
    const result = interpolate(template, undefined, "test.key");

    // Assert
    expect(result).toBe("Hello, World!");
  });

  it("escapes HTML entities for XSS prevention", async () => {
    // Arrange
    const { interpolate } = await import("../core/interpolate");
    const template = "Hello, {name}!";
    const params = { name: "<script>alert('xss')</script>" };

    // Act
    const result = interpolate(template, params, "test.key");

    // Assert
    expect(result).toBe("Hello, &lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;!");
    expect(result).not.toContain("<script>");
  });

  it("escapes ampersands and quotes", async () => {
    // Arrange
    const { interpolate } = await import("../core/interpolate");
    const template = "Value: {val}";
    const params = { val: 'A & B "quoted"' };

    // Act
    const result = interpolate(template, params, "test.key");

    // Assert
    expect(result).toBe("Value: A &amp; B &quot;quoted&quot;");
  });

  it("ignores extra parameters silently", async () => {
    // Arrange
    const { interpolate } = await import("../core/interpolate");
    const template = "Hello, {name}!";
    const params = { name: "World", extra: "ignored" };

    // Act
    const result = interpolate(template, params, "test.key");

    // Assert
    expect(result).toBe("Hello, World!");
  });
});
