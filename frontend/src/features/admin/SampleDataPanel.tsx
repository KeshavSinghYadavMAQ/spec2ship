import {
  Body1,
  Button,
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
  tokens,
} from "@fluentui/react-components";

import {
  useClearSampleData,
  useSampleDataStatus,
  useSeedSampleData,
} from "./hooks/useSampleData";
import { ScrollableTableContainer } from "../../components/ScrollableTableContainer";
import { StatusBadge } from "../../components/StatusBadge";

const useStyles = makeStyles({
  container: {
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacingVerticalM,
  },
  actions: {
    display: "flex",
    gap: tokens.spacingHorizontalS,
    flexWrap: "wrap",
    alignItems: "center",
  },
  emptyState: {
    padding: tokens.spacingVerticalL,
    border: `1px dashed ${tokens.colorNeutralStroke2}`,
    borderRadius: tokens.borderRadiusMedium,
    textAlign: "center",
  },
});

const ACTING_USER_ID = "admin-1";
const ACTING_ROLE = "admin";

/**
 * Admin "Sample Data" panel (T024, US1). Lets an admin seed the environment with
 * realistic, pilot-scale sample retail data, view the last run's status, and clear all
 * previously seeded data - all gated server-side by `require_non_production_admin`.
 */
export function SampleDataPanel() {
  const styles = useStyles();
  const { data: status, isLoading, isError, error } = useSampleDataStatus(
    ACTING_USER_ID,
    ACTING_ROLE,
  );
  const seedMutation = useSeedSampleData(ACTING_USER_ID, ACTING_ROLE);
  const clearMutation = useClearSampleData(ACTING_USER_ID, ACTING_ROLE);

  return (
    <div className={styles.container}>
      <Title2 as="h2">Sample Data</Title2>
      <Body1>
        Populate this environment with realistic, pilot-scale fictitious retail data across
        every dashboard, or clear it back to empty. Only available for admins in
        non-production environments.
      </Body1>

      <div className={styles.actions}>
        <Button
          appearance="primary"
          disabled={seedMutation.isPending}
          onClick={() => seedMutation.mutate()}
        >
          {seedMutation.isPending ? "Seeding..." : "Seed sample data"}
        </Button>
        <Button
          appearance="secondary"
          disabled={clearMutation.isPending || !status}
          onClick={() => clearMutation.mutate()}
        >
          {clearMutation.isPending ? "Clearing..." : "Clear sample data"}
        </Button>
      </div>

      {(seedMutation.isError || clearMutation.isError) && (
        <Body1 role="alert">
          {seedMutation.error instanceof Error
            ? seedMutation.error.message
            : clearMutation.error instanceof Error
              ? clearMutation.error.message
              : "Unknown error performing the sample-data action."}
        </Body1>
      )}

      {isLoading && <Spinner size="small" label="Checking sample-data status..." />}

      {isError && (
        <Body1 role="alert">
          Could not load sample-data status: {error instanceof Error ? error.message : "Unknown error"}
        </Body1>
      )}

      {!isLoading && !isError && !status && (
        <div className={styles.emptyState}>
          <Body1>No sample data has been seeded in this environment yet.</Body1>
        </div>
      )}

      {!isLoading && !isError && status && (
        <>
          <Title3 as="h3">Last seeding run</Title3>
          <div className={styles.actions}>
            <StatusBadge
              tone={status.status === "completed" ? "success" : "warning"}
              label={status.status.replace(/_/g, " ")}
            />
            <Body1>Batch {status.seed_batch_id}</Body1>
          </div>
          <ScrollableTableContainer>
          <Table aria-label="Seeded record counts by entity type">
            <TableHeader>
              <TableRow>
                <TableHeaderCell>Entity type</TableHeaderCell>
                <TableHeaderCell>Records seeded</TableHeaderCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {Object.entries(status.counts_by_entity_type).map(([entityType, count]) => (
                <TableRow key={entityType}>
                  <TableCell>{entityType.replace(/_/g, " ")}</TableCell>
                  <TableCell>{count}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          </ScrollableTableContainer>
        </>
      )}
    </div>
  );
}
