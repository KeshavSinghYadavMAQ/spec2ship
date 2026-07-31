import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../services/apiClient";

export type ForecastErrorIndicator = "low" | "medium" | "high" | "insufficient_history";

export interface DemandForecast {
  id: string;
  sku_id: string;
  location_id: string;
  period_start: string;
  period_end: string;
  forecast_quantity: number;
  trend_factor: number;
  seasonality_factor: number;
  promotion_factor: number;
  history_points_used: number;
  error_indicator: ForecastErrorIndicator;
  factors: Record<string, unknown>;
  narration: string | null;
  created_at: string;
}

export interface ForecastFilters {
  skuId?: string;
  locationId?: string;
}

export function useForecasts(filters: ForecastFilters = {}) {
  const params = new URLSearchParams();
  if (filters.skuId) params.set("sku_id", filters.skuId);
  if (filters.locationId) params.set("location_id", filters.locationId);
  const query = params.toString();

  return useQuery({
    queryKey: ["forecasts", filters.skuId ?? "", filters.locationId ?? ""],
    queryFn: () => apiClient.get<DemandForecast[]>(`/forecasts${query ? `?${query}` : ""}`),
  });
}
