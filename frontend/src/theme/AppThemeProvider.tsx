import { useMemo, useState, type ReactNode } from "react";
import { FluentProvider, webDarkTheme, webLightTheme } from "@fluentui/react-components";

import { ThemeModeContext, type ThemeMode } from "./ThemeModeContext";

const STORAGE_KEY = "retail-replenishment-theme-mode";

function getInitialMode(): ThemeMode {
  if (typeof window === "undefined") return "light";
  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark") return stored;
  return window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function AppThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>(getInitialMode);

  const toggleMode = () => {
    setMode((previous) => {
      const next = previous === "light" ? "dark" : "light";
      window.localStorage.setItem(STORAGE_KEY, next);
      return next;
    });
  };

  const value = useMemo(() => ({ mode, toggleMode }), [mode]);
  const theme = mode === "dark" ? webDarkTheme : webLightTheme;

  return (
    <ThemeModeContext.Provider value={value}>
      <FluentProvider theme={theme} data-testid={`theme-${mode}`}>
        {children}
      </FluentProvider>
    </ThemeModeContext.Provider>
  );
}
