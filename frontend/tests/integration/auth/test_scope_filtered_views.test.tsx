import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AlertWorklist } from "../../../src/features/alerting/AlertWorklist";
import { AppThemeProvider } from "../../../src/theme";

vi.mock("../../../src/features/alerting/hooks/useAlerts", () => ({
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

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient();
  return render(
    <AppThemeProvider>
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </AppThemeProvider>,
  );
}

describe("scope-filtered view rendering", () => {
  it("renders only server-filtered alert rows for the active persona", () => {
    renderWithProviders(<AlertWorklist />);
    expect(screen.getByText("STORE-A")).toBeInTheDocument();
    expect(screen.queryByText("STORE-B")).not.toBeInTheDocument();
  });
});
