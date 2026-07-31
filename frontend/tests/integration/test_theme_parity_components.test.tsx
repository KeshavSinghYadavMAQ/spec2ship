import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../../src/app/App";
import { AppThemeProvider } from "../../src/theme";

function renderApp() {
  const queryClient = new QueryClient();
  return render(
    <AppThemeProvider>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/inventory"]}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>
    </AppThemeProvider>,
  );
}

describe("theme parity", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("toggles from light to dark while retaining nav and shell surfaces", () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ title: "Not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      }),
    );

    renderApp();
    const toggle = screen.getByRole("button", { name: /switch to dark mode/i });
    fireEvent.click(toggle);

    expect(screen.getByRole("button", { name: /switch to light mode/i })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Primary" })).toBeInTheDocument();
    expect(screen.getByRole("main")).toBeInTheDocument();
  });
});
