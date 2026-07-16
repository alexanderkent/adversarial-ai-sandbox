import { renderHook, act } from "@testing-library/react";
import { afterEach, beforeEach, expect, test } from "vitest";
import { useTheme } from "./useTheme";

beforeEach(() => { localStorage.clear(); document.documentElement.removeAttribute("data-theme"); });
afterEach(() => localStorage.clear());

test("defaults to light and sets data-theme", () => {
  const { result } = renderHook(() => useTheme());
  expect(result.current.theme).toBe("light");
  expect(document.documentElement.dataset.theme).toBe("light");
});

test("toggle flips theme, persists, and updates data-theme", () => {
  const { result } = renderHook(() => useTheme());
  act(() => result.current.toggle());
  expect(result.current.theme).toBe("dark");
  expect(document.documentElement.dataset.theme).toBe("dark");
  expect(localStorage.getItem("theme")).toBe("dark");
});

test("honors a stored theme on init", () => {
  localStorage.setItem("theme", "dark");
  const { result } = renderHook(() => useTheme());
  expect(result.current.theme).toBe("dark");
});
