import { useMemo } from "react";

import type { InventoryPosition } from "./useInventoryPositions";

export type InventoryKpi = {
  key: string;
  label: string;
  value: string;
  delta?: string;
};

export function useInventoryKpis(positions: InventoryPosition[] | undefined): InventoryKpi[] {
  return useMemo(() => {
    const rows = positions ?? [];
    const totalSkus = rows.length;
    const totalUnits = rows.reduce((sum, row) => sum + row.reconciled_total, 0);
    const staleCount = rows.filter((row) => row.data_freshness_warning).length;

    return [
      { key: "sku_count", label: "SKU rows", value: String(totalSkus) },
      { key: "unit_total", label: "Total units", value: String(totalUnits) },
      { key: "stale_rows", label: "Stale rows", value: String(staleCount) },
    ];
  }, [positions]);
}
