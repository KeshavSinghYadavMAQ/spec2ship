import { useMemo } from "react";

import type { TransferSuggestion } from "./useTransfers";

export type TransferKpi = {
  key: string;
  label: string;
  value: string;
};

export function useTransferKpis(suggestions: TransferSuggestion[] | undefined): TransferKpi[] {
  return useMemo(() => {
    const rows = suggestions ?? [];
    const feasible = rows.filter((row) => row.feasibility_status === "feasible").length;
    const inTransit = rows.filter((row) => row.status === "in_transit").length;

    return [
      { key: "total_suggestions", label: "Suggestions", value: String(rows.length) },
      { key: "feasible", label: "Feasible", value: String(feasible) },
      { key: "in_transit", label: "In transit", value: String(inTransit) },
    ];
  }, [suggestions]);
}
