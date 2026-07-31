import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "../../../services/apiClient";

export type RecommendationStatus = "proposed" | "accepted" | "overridden" | "dismissed";
export type ActionabilityRating = "actionable" | "not_actionable";

export interface ReplenishmentRecommendation {
  id: string;
  sku_id: string;
  location_id: string;
  recommended_quantity: number;
  recommended_by_date: string;
  policy_snapshot: Record<string, unknown>;
  rationale: { factors: Record<string, unknown>; narration: string };
  status: RecommendationStatus;
  override_reason: string | null;
  actionability_rating: ActionabilityRating | null;
  created_at: string;
}

export function useRecommendations() {
  return useQuery({
    queryKey: ["replenishment-recommendations"],
    queryFn: () => apiClient.get<ReplenishmentRecommendation[]>("/replenishment/recommendations"),
  });
}

export interface DecisionInput {
  recommendationId: string;
  decision: RecommendationStatus;
  overrideReason?: string;
  actionabilityRating?: ActionabilityRating;
}

export function useDecideRecommendation(actingUserId: string, actingRole: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ recommendationId, decision, overrideReason, actionabilityRating }: DecisionInput) =>
      apiClient.post<ReplenishmentRecommendation>(
        `/replenishment/recommendations/${recommendationId}/decision`,
        {
          decision,
          override_reason: overrideReason,
          actionability_rating: actionabilityRating,
        },
        { "X-User-Id": actingUserId, "X-User-Role": actingRole },
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["replenishment-recommendations"] });
    },
  });
}
