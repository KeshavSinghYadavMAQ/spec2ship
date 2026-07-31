import { useState } from "react";
import {
  Badge,
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
  makeStyles,
} from "@fluentui/react-components";

import { IdentityBar } from "../../components/IdentityBar";
import {
  type TransferStatus,
  type TransferSuggestion,
  useTransferSuggestions,
  useUpdateTransferStatus,
} from "./hooks/useTransfers";

const useStyles = makeStyles({
  container: { display: "flex", flexDirection: "column", gap: "12px" },
  actions: { display: "flex", gap: "8px", flexWrap: "wrap" },
});

const nextActions: Partial<Record<TransferStatus, { label: string; target: TransferStatus }[]>> = {
  proposed: [
    { label: "Accept", target: "accepted" },
    { label: "Reject", target: "rejected" },
  ],
  accepted: [{ label: "Mark in transit", target: "in_transit" }],
  in_transit: [{ label: "Mark completed", target: "completed" }],
};

/**
 * Transfer-balance suggestion worklist (T072, US5, FR-008, FR-009, FR-020). Feasibility
 * status/reason is always shown so operators understand why a transfer was (or was not)
 * proposed before acting on it.
 */
export function TransferSuggestions() {
  const styles = useStyles();
  const [actingUserId, setActingUserId] = useState("regional-manager-1");
  const [actingRole, setActingRole] = useState("regional_manager");
  const { data, isLoading, isError, error } = useTransferSuggestions();
  const updateStatus = useUpdateTransferStatus(actingUserId, actingRole);

  return (
    <div className={styles.container}>
      <Title2 as="h2">Transfer Suggestions</Title2>

      <IdentityBar
        actingUserId={actingUserId}
        onActingUserIdChange={setActingUserId}
        actingRole={actingRole}
        onActingRoleChange={setActingRole}
      />

      {isLoading && <Spinner size="small" label="Loading transfer suggestions..." />}

      {isError && (
        <Body1 role="alert">
          Could not load transfer suggestions: {error instanceof Error ? error.message : "Unknown error"}
        </Body1>
      )}

      {!isLoading && !isError && data && data.length === 0 && (
        <Body1>No transfer suggestions at this time.</Body1>
      )}

      {!isLoading && !isError && data && data.length > 0 && (
        <Table aria-label="Transfer suggestions">
          <TableHeader>
            <TableRow>
              <TableHeaderCell>SKU</TableHeaderCell>
              <TableHeaderCell>Source</TableHeaderCell>
              <TableHeaderCell>Destination</TableHeaderCell>
              <TableHeaderCell>Qty</TableHeaderCell>
              <TableHeaderCell>Priority</TableHeaderCell>
              <TableHeaderCell>Feasibility</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Actions</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((suggestion: TransferSuggestion) => (
              <TableRow key={suggestion.id}>
                <TableCell>{suggestion.sku_id}</TableCell>
                <TableCell>{suggestion.source_location_id}</TableCell>
                <TableCell>{suggestion.destination_location_id}</TableCell>
                <TableCell>{suggestion.suggested_quantity}</TableCell>
                <TableCell>{suggestion.priority_rank}</TableCell>
                <TableCell>
                  <Badge color={suggestion.feasibility_status === "feasible" ? "success" : "danger"}>
                    {suggestion.feasibility_status}
                  </Badge>
                  <Body1>{suggestion.feasibility_reason}</Body1>
                </TableCell>
                <TableCell>{suggestion.status}</TableCell>
                <TableCell>
                  <div className={styles.actions}>
                    {(nextActions[suggestion.status] ?? []).map((action) => (
                      <Button
                        key={action.target}
                        size="small"
                        disabled={updateStatus.isPending}
                        onClick={() =>
                          updateStatus.mutate({ suggestionId: suggestion.id, status: action.target })
                        }
                      >
                        {action.label}
                      </Button>
                    ))}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
