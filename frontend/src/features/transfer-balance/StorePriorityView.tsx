import { useState } from "react";
import {
  Body1,
  Button,
  Input,
  Spinner,
  Table,
  TableBody,
  TableCell,
  TableHeader,
  TableHeaderCell,
  TableRow,
  Title2,
  Title3,
  makeStyles,
} from "@fluentui/react-components";

import { ApiError } from "../../services/apiClient";
import { useStorePriorityProfiles, useUpdatePriorityRules } from "./hooks/useStorePriority";

const useStyles = makeStyles({
  container: { display: "flex", flexDirection: "column", gap: "16px" },
  filters: { display: "flex", gap: "8px", flexWrap: "wrap", alignItems: "flex-end" },
  narration: { maxWidth: "360px" },
});

/**
 * Store restoration priority view (T086, US8, FR-019, FR-020, FR-021). Ranks stores by
 * region-shortage signal and recent consumption; only elevated roles (admin/regional
 * manager) can adjust the global region/consumption weighting.
 */
export function StorePriorityView() {
  const styles = useStyles();
  const [region, setRegion] = useState("");
  const [actingUserId, setActingUserId] = useState("regional-1");
  const [regionWeight, setRegionWeight] = useState("0.5");
  const [consumptionWeight, setConsumptionWeight] = useState("0.5");
  const [feedback, setFeedback] = useState<string | null>(null);

  const { data, isLoading, isError, error } = useStorePriorityProfiles(region || undefined);
  const updateRules = useUpdatePriorityRules(actingUserId, "regional_manager");

  const submitRules = () => {
    setFeedback(null);
    updateRules.mutate(
      { region_weight: Number(regionWeight), consumption_weight: Number(consumptionWeight) },
      {
        onSuccess: () => setFeedback("Priority rules updated; rankings recomputed."),
        onError: (mutationError) => {
          if (mutationError instanceof ApiError) {
            setFeedback(mutationError.detail);
            return;
          }
          setFeedback("Unknown error updating priority rules.");
        },
      },
    );
  };

  return (
    <div className={styles.container}>
      <Title2 as="h2">Store Restoration Priority</Title2>

      <div className={styles.filters}>
        <Input placeholder="Filter by region" value={region} onChange={(_e, d) => setRegion(d.value)} />
      </div>

      <Title3 as="h3">Update weighting rules</Title3>
      <div className={styles.filters}>
        <Input value={actingUserId} onChange={(_e, d) => setActingUserId(d.value)} aria-label="Acting user id" />
        <Input
          type="number"
          value={regionWeight}
          onChange={(_e, d) => setRegionWeight(d.value)}
          aria-label="Region weight"
        />
        <Input
          type="number"
          value={consumptionWeight}
          onChange={(_e, d) => setConsumptionWeight(d.value)}
          aria-label="Consumption weight"
        />
        <Button appearance="primary" disabled={updateRules.isPending} onClick={submitRules}>
          Apply rules
        </Button>
      </div>
      {feedback && <Body1 role="status">{feedback}</Body1>}

      {isLoading && <Spinner size="small" label="Loading store priority profiles..." />}

      {isError && (
        <Body1 role="alert">
          Could not load store priority profiles: {error instanceof Error ? error.message : "Unknown error"}
        </Body1>
      )}

      {!isLoading && !isError && data && data.length === 0 && <Body1>No store profiles found.</Body1>}

      {!isLoading && !isError && data && data.length > 0 && (
        <Table aria-label="Store priority profiles">
          <TableHeader>
            <TableRow>
              <TableHeaderCell>Rank</TableHeaderCell>
              <TableHeaderCell>Store</TableHeaderCell>
              <TableHeaderCell>Region</TableHeaderCell>
              <TableHeaderCell>Consumption rate</TableHeaderCell>
              <TableHeaderCell>Explanation</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((profile) => (
              <TableRow key={profile.id}>
                <TableCell>{profile.current_priority_rank}</TableCell>
                <TableCell>{profile.store_id}</TableCell>
                <TableCell>{profile.region}</TableCell>
                <TableCell>{profile.recent_consumption_rate.toFixed(1)}</TableCell>
                <TableCell>
                  <Title3 as="span" className={styles.narration}>
                    {profile.narration ?? "—"}
                  </Title3>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
