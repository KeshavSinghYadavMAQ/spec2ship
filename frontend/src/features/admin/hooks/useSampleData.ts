import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ApiError, apiClient } from "../../../services/apiClient";

export type SeedRunStatus = "in_progress" | "completed" | "partially_completed";

export interface SeedRunSummary {
  seed_batch_id: string;
  status: SeedRunStatus;
  counts_by_entity_type: Record<string, number>;
  started_at: string;
  completed_at: string | null;
}

export interface ClearRunSummary {
  removed_counts_by_entity_type: Record<string, number>;
  cleared_at: string;
}

/**
 * Sample-data status; resolves to `null` (rather than throwing) when the environment has
 * never been seeded (404), so the panel can render a clean "not seeded yet" empty state.
 */
export function useSampleDataStatus(actingUserId: string, actingRole: string) {
  void actingUserId;
  void actingRole;
  return useQuery({
    queryKey: ["sample-data-status"],
    queryFn: async (): Promise<SeedRunSummary | null> => {
      try {
        return await apiClient.get<SeedRunSummary>("/admin/sample-data/status");
      } catch (error) {
        if (error instanceof ApiError && error.status === 404) {
          return null;
        }
        throw error;
      }
    },
  });
}

export function useSeedSampleData(actingUserId: string, actingRole: string) {
  void actingUserId;
  void actingRole;
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.post<SeedRunSummary>("/admin/sample-data/seed", undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sample-data-status"] });
    },
  });
}

export function useClearSampleData(actingUserId: string, actingRole: string) {
  void actingUserId;
  void actingRole;
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.delete<ClearRunSummary>("/admin/sample-data"),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sample-data-status"] });
    },
  });
}

export { ApiError };
