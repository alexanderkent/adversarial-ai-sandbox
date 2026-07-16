import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, test } from "vitest";
import { ThemeToggle } from "./ThemeToggle";

beforeEach(() => { localStorage.clear(); document.documentElement.removeAttribute("data-theme"); });

test("renders a theme button and flips the theme on click", async () => {
  render(<ThemeToggle />);
  const btn = screen.getByRole("button", { name: /theme/i });
  await userEvent.click(btn);
  expect(document.documentElement.dataset.theme).toBe("dark");
});
