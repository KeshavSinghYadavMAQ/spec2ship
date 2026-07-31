import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/apiClient";

export type FeasibilityStatus = "feasible" | "infeasible";
export type TransferStatus = "proposed" | "accepted" | "in_transit" | "completed" | "rejected";

export interface TransferSuggestion {
  id: string;
  sku_id: string;
  source_location_id: string;
  destination_location_id: string;
  suggested_quantity: number;
  feasibility_status: FeasibilityStatus;
  feasibility_reason: string;
  priority_rank: number;
  status: TransferStatus;
  factors: Record<string, unknown>;
  created_at: string;
}

export function useTransferSuggestions() {
  return useQuery({
    queryKey: ["transfer-suggestions"],
    queryFn: () => apiClient.get<TransferSuggestion[]>("/transfers/suggestions"),
  });
}

export function useUpdateTransferStatus(actingUserId: string, actingRole: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ suggestionId, status }: { suggestionId: string; status: TransferStatus }) =>
      apiClient.post<TransferSuggestion>(
        `/transfers/suggestions/${suggestionId}/status`,
        { status },
        { "X-User-Id": actingUserId, "X-User-Role": actingRole },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transfer-suggestions"] });
    },
  });
}
