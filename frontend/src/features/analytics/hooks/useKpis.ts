import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../services/apiClient";

export interface KPIView {
  region: string | null;
  store_id: string | null;
  category: string | null;
  date_from: string | null;
  date_to: string | null;
  total_positions: number;
  fill_rate: number;
  open_alert_count: number;
  average_alert_age_hours: number;
  recommendation_outcomes: Record<string, number>;
  forecast_quality: Record<string, number>;
}

export interface KpiFilters {
  region?: string;
  storeId?: string;
  category?: string;
  from?: string;
  to?: string;
}

export function useKpis(filters: KpiFilters = {}) {
  const params = new URLSearchParams();
  if (filters.region) params.set("region", filters.region);
  if (filters.storeId) params.set("store_id", filters.storeId);
  if (filters.category) params.set("category", filters.category);
  if (filters.from) params.set("from", filters.from);
  if (filters.to) params.set("to", filters.to);
  const query = params.toString();

  return useQuery({
    queryKey: ["analytics-kpis", query],
    queryFn: () => apiClient.get<KPIView[]>(`/analytics/kpis${query ? `?${query}` : ""}`),
  });
}
