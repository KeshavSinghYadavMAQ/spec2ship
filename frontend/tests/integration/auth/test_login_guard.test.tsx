import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../../../src/app/App";
import { AppThemeProvider } from "../../../src/theme";

describe("login guard", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("redirects unauthenticated users to login", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ title: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      }),
    );

    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });

    render(
      <AppThemeProvider>
        <QueryClientProvider client={queryClient}>
          <MemoryRouter initialEntries={["/inventory"]}>
            <App />
          </MemoryRouter>
        </QueryClientProvider>
      </AppThemeProvider>,
    );

    await waitFor(() => {
      expect(screen.getByText("Sign in to continue.")).toBeInTheDocument();
    });
  });
});
