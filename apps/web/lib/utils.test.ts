import { describe, it, expect } from "vitest";
import { cn } from "./utils";

describe("cn utility function", () => {
  it("should merge class names", () => {
    expect(cn("foo", "bar")).toBe("foo bar");
  });

  it("should handle conditional classes with clsx", () => {
    expect(cn("base", true && "included", false && "excluded")).toBe(
      "base included"
    );
  });

  it("should handle undefined and null values", () => {
    expect(cn("base", undefined, null, "end")).toBe("base end");
  });

  it("should merge conflicting Tailwind classes correctly", () => {
    // tailwind-merge should keep the last conflicting class
    expect(cn("px-2", "px-4")).toBe("px-4");
    expect(cn("text-red-500", "text-blue-500")).toBe("text-blue-500");
    expect(cn("bg-white", "bg-black")).toBe("bg-black");
  });

  it("should handle object syntax", () => {
    expect(
      cn({
        "text-red-500": true,
        "text-blue-500": false,
      })
    ).toBe("text-red-500");
  });

  it("should handle array syntax", () => {
    expect(cn(["foo", "bar"])).toBe("foo bar");
  });

  it("should handle complex combinations", () => {
    const result = cn(
      "base-class",
      ["array-class"],
      { "conditional-class": true },
      undefined,
      "final-class"
    );
    expect(result).toBe("base-class array-class conditional-class final-class");
  });

  it("should return empty string for no arguments", () => {
    expect(cn()).toBe("");
  });

  it("should handle empty strings", () => {
    expect(cn("", "foo", "", "bar")).toBe("foo bar");
  });
});
