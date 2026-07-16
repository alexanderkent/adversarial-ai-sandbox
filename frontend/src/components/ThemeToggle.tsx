import { useTheme } from "../hooks/useTheme";

export function ThemeToggle() {
  const { theme, toggle } = useTheme();
  return (
    <button
      onClick={toggle}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
      className="rounded-lg border border-border bg-surface px-2.5 py-1.5 text-sm text-ink-muted transition hover:text-ink"
    >
      {theme === "dark" ? "☀︎" : "☾"}
    </button>
  );
}
