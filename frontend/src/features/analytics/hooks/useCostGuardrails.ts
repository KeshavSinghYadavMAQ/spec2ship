import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../services/apiClient";

export interface CostGuardrailView {
  ingested_event_count: number;
  estimated_ingestion_cost_usd: number;
  monthly_cost_ceiling_usd: number;
  per_event_cost_assumption_usd: number;
  within_ceiling: boolean;
}

/** SC-008 cost guardrail snapshot (T104): estimated ingestion cost vs. the pilot ceiling. */
export function useCostGuardrails() {
  return useQuery({
    queryKey: ["cost-guardrails"],
    queryFn: () => apiClient.get<CostGuardrailView>("/admin/cost-guardrails"),
    refetchInterval: 60_000,
  });
}
