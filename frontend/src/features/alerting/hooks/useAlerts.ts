import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/apiClient";

export type AlertStatus = "Open" | "Acknowledged" | "Escalated" | "Snoozed" | "Resolved";
export type AlertSeverity = "low_stock" | "out_of_stock";

export interface StockAlert {
  id: string;
  sku_id: string;
  location_id: string;
  severity: AlertSeverity;
  status: AlertStatus;
  owner_user_id: string | null;
  routing_channel: string | null;
  created_at: string;
  updated_at: string;
}

export function useAlerts(filters: { status?: string; severity?: string } = {}) {
  const params = new URLSearchParams();
  if (filters.status) params.set("status", filters.status);
  if (filters.severity) params.set("severity", filters.severity);
  const query = params.toString();

  return useQuery({
    queryKey: ["alerts", filters.status, filters.severity],
    queryFn: () => apiClient.get<StockAlert[]>(`/alerts${query ? `?${query}` : ""}`),
  });
}

export function useTransitionAlert(_actingUserId: string, _actingRole: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ alertId, status }: { alertId: string; status: AlertStatus }) =>
      apiClient.post<StockAlert>(`/alerts/${alertId}/transition`, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
}
