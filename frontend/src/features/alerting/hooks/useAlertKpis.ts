import { useMemo } from "react";

import type { StockAlert } from "./useAlerts";

export type AlertKpi = {
  key: string;
  label: string;
  value: string;
};

export function useAlertKpis(alerts: StockAlert[] | undefined): AlertKpi[] {
  return useMemo(() => {
    const rows = alerts ?? [];
    const outOfStock = rows.filter((row) => row.severity === "out_of_stock").length;
    const open = rows.filter((row) => row.status !== "Resolved").length;

    return [
      { key: "total_alerts", label: "Total alerts", value: String(rows.length) },
      { key: "out_of_stock", label: "Out of stock", value: String(outOfStock) },
      { key: "open_alerts", label: "Open alerts", value: String(open) },
    ];
  }, [alerts]);
}
