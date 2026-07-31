import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { AppThemeProvider, useThemeMode } from "../src/theme";

function ModeProbe() {
  const { mode, toggleMode } = useThemeMode();
  return (
    <button onClick={toggleMode} data-testid="toggle">
      {mode}
    </button>
  );
}

describe("AppThemeProvider", () => {
  it("defaults to a valid theme mode and toggles between light and dark", async () => {
    const user = userEvent.setup();
    render(
      <AppThemeProvider>
        <ModeProbe />
      </AppThemeProvider>,
    );

    const button = screen.getByTestId("toggle");
    const initialMode = button.textContent;
    expect(["light", "dark"]).toContain(initialMode);

    await user.click(button);
    expect(button.textContent).not.toBe(initialMode);
  });
});
