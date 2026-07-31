import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/apiClient";

export interface StorePriorityProfile {
  id: string;
  store_id: string;
  region: string;
  recent_consumption_rate: number;
  region_weight: number;
  consumption_weight: number;
  current_priority_rank: number;
  priority_factors: Record<string, unknown> | null;
  narration: string | null;
}

export function useStorePriorityProfiles(region?: string) {
  const query = region ? `?region=${encodeURIComponent(region)}` : "";
  return useQuery({
    queryKey: ["store-priority-profiles", region ?? ""],
    queryFn: () => apiClient.get<StorePriorityProfile[]>(`/store-priority/profiles${query}`),
  });
}

export function useUpdatePriorityRules(actingUserId: string, actingRole: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (rules: { region_weight?: number; consumption_weight?: number }) =>
      apiClient.post<StorePriorityProfile[]>("/store-priority/rules", rules, {
        "X-User-Id": actingUserId,
        "X-User-Role": actingRole,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["store-priority-profiles"] });
    },
  });
}
