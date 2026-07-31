import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../../services/apiClient";

export interface InventoryPosition {
  id: string;
  sku_id: string;
  location_id: string;
  shelf_quantity: number;
  backroom_quantity: number;
  reconciled_total: number;
  freshness_at: string;
  data_freshness_warning: boolean;
}

export function useInventoryPositions(filters: { skuId?: string; locationId?: string } = {}) {
  const params = new URLSearchParams();
  if (filters.skuId) params.set("sku_id", filters.skuId);
  if (filters.locationId) params.set("location_id", filters.locationId);
  const query = params.toString();

  return useQuery({
    queryKey: ["inventory-positions", filters.skuId, filters.locationId],
    queryFn: () => apiClient.get<InventoryPosition[]>(`/inventory/positions${query ? `?${query}` : ""}`),
  });
}
