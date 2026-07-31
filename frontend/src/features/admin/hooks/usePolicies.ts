import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiClient } from "../../../services/apiClient";

export interface ProductLocationPolicy {
  id: string;
  sku_id: string;
  location_id: string;
  low_stock_threshold: number;
  out_of_stock_threshold: number;
  reorder_point: number;
  min_qty: number;
  max_qty: number;
  safety_stock: number;
  is_active: boolean;
  edit_lock_held: boolean;
  updated_by: string | null;
  updated_at: string | null;
  change_history: Record<string, unknown>[] | null;
}

export interface PolicyInput {
  sku_id: string;
  location_id: string;
  low_stock_threshold: number;
  out_of_stock_threshold: number;
  reorder_point: number;
  min_qty: number;
  max_qty: number;
  safety_stock: number;
}

export function usePolicies() {
  return useQuery({
    queryKey: ["product-location-policies"],
    queryFn: () => apiClient.get<ProductLocationPolicy[]>("/admin/product-location-policies"),
  });
}

export function useUpsertPolicy(_actingUserId: string, _actingRole: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: PolicyInput) =>
      apiClient.post<ProductLocationPolicy>("/admin/product-location-policies", input),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["product-location-policies"] });
    },
  });
}

export { ApiError };
