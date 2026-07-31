import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AppThemeProvider } from "../../src/theme";
import { AlertWorklist } from "../../src/features/alerting/AlertWorklist";
import { InventoryPositionView } from "../../src/features/inventory/InventoryPositionView";

vi.mock("../../src/features/alerting/hooks/useAlerts", () => ({
  useAlerts: () => ({
    data: [
      {
        id: "alert-1",
        sku_id: "SKU-1",
        location_id: "LOC-1",
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

vi.mock("../../src/features/inventory/hooks/useInventoryPositions", () => ({
  useInventoryPositions: () => ({
    data: [
      {
        id: "pos-1",
        sku_id: "SKU-1",
        location_id: "LOC-1",
        shelf_quantity: 5,
        backroom_quantity: 2,
        reconciled_total: 7,
        data_freshness_warning: true,
      },
    ],
    isLoading: false,
    isError: false,
    error: null,
    isFetching: false,
  }),
}));

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <AppThemeProvider>{ui}</AppThemeProvider>
    </QueryClientProvider>,
  );
}

/**
 * Shared-component consistency test (T027, US2, FR-010). The alert worklist (severity)
 * and the inventory position view (freshness) are different feature screens that both
 * render status indicators via the shared `StatusBadge` component; both must pair color
 * with an icon and a text label consistently.
 */
describe("shared status badge consistency across feature screens", () => {
  it("renders an icon alongside a text label on the alert worklist", () => {
    renderWithProviders(<AlertWorklist />);
    const badge = screen.getByText(/out of stock/i);
    expect(badge.closest("span")?.querySelector("svg")).not.toBeNull();
  });

  it("renders an icon alongside a text label on the inventory position view", () => {
    renderWithProviders(<InventoryPositionView />);
    const badge = screen.getByText(/stale - reconciling/i);
    expect(badge.closest("span")?.querySelector("svg")).not.toBeNull();
  });
});
