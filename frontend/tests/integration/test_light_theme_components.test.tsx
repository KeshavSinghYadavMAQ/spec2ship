import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../../src/app/App";
import { AppThemeProvider } from "../../src/theme";
import { AlertWorklist } from "../../src/features/alerting/AlertWorklist";

vi.mock("../../src/features/alerting/hooks/useAlerts", () => ({
  useAlerts: () => ({
    data: [
      {
        id: "alert-a",
        sku_id: "SKU-1",
        location_id: "STORE-A",
        severity: "low_stock",
        status: "Open",
        owner_user_id: null,
        routing_channel: null,
        created_at: "2024-01-01T00:00:00Z",
        updated_at: "2024-01-01T00:00:00Z",
      },
    ],
    isLoading: false,
    isError: false,
    error: null,
  }),
  useTransitionAlert: () => ({ mutate: vi.fn(), isPending: false }),
}));

function renderShell(route: string) {
  const queryClient = new QueryClient();
  return render(
    <AppThemeProvider>
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={[route]}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>
    </AppThemeProvider>,
  );
}

function renderAlertWorklist() {
  const queryClient = new QueryClient();
  return render(
    <AppThemeProvider>
      <QueryClientProvider client={queryClient}>
        <AlertWorklist />
      </QueryClientProvider>
    </AppThemeProvider>,
  );
}

describe("light-theme shared components", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders nav icon pills and theme toggle", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ title: "Not found" }), {
        status: 404,
        headers: { "Content-Type": "application/json" },
      }),
    );

    renderShell("/inventory");
    expect(screen.getByRole("navigation", { name: "Primary" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /switch to dark mode/i })).toBeInTheDocument();
  });

  it("renders sticky table container on list screens", () => {
    renderAlertWorklist();
    expect(screen.getByRole("table", { name: "Stock alerts" })).toBeInTheDocument();
  });
});
