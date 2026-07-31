import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AppThemeProvider } from "../../src/theme";
import { AlertWorklist } from "../../src/features/alerting/AlertWorklist";

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

/**
 * Responsive primary-workflow test (T037, US3, FR-009). The alert triage worklist is a
 * primary operational workflow (per the accessibility audit route list); its data table
 * must be wrapped in a horizontally-scrollable container rather than forcing page-level
 * horizontal scrolling at a 360px mobile viewport.
 */
describe("alert triage remains usable at mobile width", () => {
  it("wraps the alert table in a horizontally scrollable container", () => {
    const queryClient = new QueryClient();
    render(
      <QueryClientProvider client={queryClient}>
        <AppThemeProvider>
          <AlertWorklist />
        </AppThemeProvider>
      </QueryClientProvider>,
    );

    const table = screen.getByRole("table", { name: "Stock alerts" });
    const scrollContainer = table.parentElement;
    expect(scrollContainer).not.toBeNull();
    expect(getComputedStyle(scrollContainer as HTMLElement).overflowX).toBe("auto");
  });
});
