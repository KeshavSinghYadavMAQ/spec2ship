import { useState } from "react";
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
  makeStyles,
  tokens,
} from "@fluentui/react-components";

import { StatusBadge } from "../../components/StatusBadge";
import { ScrollableTableContainer } from "../../components/ScrollableTableContainer";
import { KpiCard } from "../../components/KpiCard";
import { IdentityBar } from "../../components/IdentityBar";
import { useAlertKpis } from "./hooks/useAlertKpis";
import { type AlertStatus, useAlerts, useTransitionAlert } from "./hooks/useAlerts";

const useStyles = makeStyles({
  container: { display: "flex", flexDirection: "column", gap: tokens.spacingVerticalM },
  actions: { display: "flex", gap: tokens.spacingHorizontalS, flexWrap: "wrap" },
  kpiRow: { display: "flex", gap: tokens.spacingHorizontalM, flexWrap: "wrap" },
});

const NEXT_STATUS_ACTIONS: Record<AlertStatus, AlertStatus[]> = {
  Open: ["Acknowledged", "Escalated"],
  Acknowledged: ["Escalated", "Snoozed", "Resolved"],
  Escalated: ["Snoozed", "Resolved"],
  Snoozed: ["Resolved"],
  Resolved: [],
};

/**
 * Alert worklist view (T047, T048, US2): status/severity filters and lifecycle
 * transitions, with explicit loading/empty/error states.
 */
export function AlertWorklist() {
  const styles = useStyles();
  const [actingUserId, setActingUserId] = useState("store-manager-1");
  const [actingRole, setActingRole] = useState("store_manager");
  const { data, isLoading, isError, error } = useAlerts();
  const kpis = useAlertKpis(data);
  const transitionAlert = useTransitionAlert(actingUserId, actingRole);

  return (
    <div className={styles.container}>
      <Title2 as="h2">Alert Worklist</Title2>

      <IdentityBar
        actingUserId={actingUserId}
        onActingUserIdChange={setActingUserId}
        actingRole={actingRole}
        onActingRoleChange={setActingRole}
      />

      {isLoading && <Spinner size="small" label="Loading alerts..." />}

      {isError && (
        <Body1 role="alert">
          Could not load alerts: {error instanceof Error ? error.message : "Unknown error"}
        </Body1>
      )}

      {!isLoading && !isError && data && data.length === 0 && <Body1>No active alerts.</Body1>}

      {!isLoading && !isError && data && data.length > 0 && (
        <>
        <div className={styles.kpiRow}>
          {kpis.map((kpi) => (
            <KpiCard key={kpi.key} label={kpi.label} value={kpi.value} />
          ))}
        </div>
        <ScrollableTableContainer>
        <Table aria-label="Stock alerts">
          <TableHeader>
            <TableRow>
              <TableHeaderCell>SKU</TableHeaderCell>
              <TableHeaderCell>Location</TableHeaderCell>
              <TableHeaderCell>Severity</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Actions</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((alert) => (
              <TableRow key={alert.id}>
                <TableCell>{alert.sku_id}</TableCell>
                <TableCell>{alert.location_id}</TableCell>
                <TableCell>
                  <StatusBadge
                    tone={alert.severity === "out_of_stock" ? "danger" : "warning"}
                    label={alert.severity.replace(/_/g, " ")}
                  />
                </TableCell>
                <TableCell>{alert.status}</TableCell>
                <TableCell>
                  <div className={styles.actions}>
                    {NEXT_STATUS_ACTIONS[alert.status].map((nextStatus) => (
                      <Button
                        key={nextStatus}
                        size="small"
                        onClick={() =>
                          transitionAlert.mutate({ alertId: alert.id, status: nextStatus })
                        }
                        disabled={transitionAlert.isPending}
                      >
                        {nextStatus}
                      </Button>
                    ))}
                  </div>
                </TableCell>
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
