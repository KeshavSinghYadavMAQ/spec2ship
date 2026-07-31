import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { InventoryPositionView } from "../../src/features/inventory/InventoryPositionView";
import { AlertWorklist } from "../../src/features/alerting/AlertWorklist";
import { TransferSuggestions } from "../../src/features/transfer-balance/TransferSuggestions";
import { AppThemeProvider } from "../../src/theme";

vi.mock("../../src/features/inventory/hooks/useInventoryPositions", () => ({
  useInventoryPositions: () => ({
    data: [
      {
        id: "inv-1",
        sku_id: "SKU-1",
        location_id: "STORE-A",
        shelf_quantity: 3,
        backroom_quantity: 2,
        reconciled_total: 5,
        freshness_at: "2024-01-01T00:00:00Z",
        data_freshness_warning: false,
      },
    ],
    isLoading: false,
    isError: false,
    error: null,
    isFetching: false,
  }),
}));

vi.mock("../../src/features/alerting/hooks/useAlerts", () => ({
  useAlerts: () => ({
    data: [
      {
        id: "al-1",
        sku_id: "SKU-1",
        location_id: "STORE-A",
        severity: "out_of_stock",
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

vi.mock("../../src/features/transfer-balance/hooks/useTransfers", () => ({
  useTransferSuggestions: () => ({
    data: [
      {
        id: "tr-1",
        sku_id: "SKU-1",
        source_location_id: "STORE-A",
        destination_location_id: "STORE-B",
        suggested_quantity: 4,
        feasibility_status: "feasible",
        feasibility_reason: "ok",
        priority_rank: 1,
        status: "proposed",
        factors: {},
        created_at: "2024-01-01T00:00:00Z",
      },
    ],
    isLoading: false,
    isError: false,
    error: null,
  }),
  useUpdateTransferStatus: () => ({ mutate: vi.fn(), isPending: false }),
}));

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient();
  return render(
    <AppThemeProvider>
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </AppThemeProvider>,
  );
}

describe("KPI cards", () => {
  it("shows inventory KPI cards above the inventory table", () => {
    renderWithProviders(<InventoryPositionView />);
    expect(screen.getByText("SKU rows")).toBeInTheDocument();
    expect(screen.getByText("Total units")).toBeInTheDocument();
  });

  it("shows alert KPI cards above the alert table", () => {
    renderWithProviders(<AlertWorklist />);
    expect(screen.getByText("Total alerts")).toBeInTheDocument();
    expect(screen.getByText("Out of stock")).toBeInTheDocument();
  });

  it("shows transfer KPI cards above the transfer table", () => {
    renderWithProviders(<TransferSuggestions />);
    expect(screen.getByText("Suggestions")).toBeInTheDocument();
    expect(screen.getByText("Feasible")).toBeInTheDocument();
  });
});
