import { afterEach, describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { AppThemeProvider, useThemeMode } from "../../src/theme";

const STORAGE_KEY = "retail-replenishment-theme-mode";

function ModeProbe() {
  const { mode, toggleMode } = useThemeMode();
  return (
    <button onClick={toggleMode} data-testid="toggle">
      {mode}
    </button>
  );
}

/**
 * Theme persistence test (T043, US4, FR-013). The user's dark/light preference must
 * survive a full "new session" (a fresh `AppThemeProvider` mount reading from
 * `localStorage`, simulating a page reload) rather than only persisting via in-memory
 * React state.
 */
describe("theme preference persistence", () => {
  afterEach(() => {
    window.localStorage.removeItem(STORAGE_KEY);
  });

  it("persists the toggled mode across a fresh provider mount (simulated reload)", async () => {
    const user = userEvent.setup();
    const { unmount } = render(
      <AppThemeProvider>
        <ModeProbe />
      </AppThemeProvider>,
    );

    const toggle = screen.getByTestId("toggle");
    const initialMode = toggle.textContent;
    await user.click(toggle);
    const toggledMode = toggle.textContent;
    expect(toggledMode).not.toBe(initialMode);
    expect(window.localStorage.getItem(STORAGE_KEY)).toBe(toggledMode);

    // Simulate a reload: unmount entirely and mount a brand-new provider instance.
    unmount();
    render(
      <AppThemeProvider>
        <ModeProbe />
      </AppThemeProvider>,
    );

    expect(screen.getByTestId("toggle").textContent).toBe(toggledMode);
  });
});
