import {
  Body1,
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
import { useInventoryPositions } from "./hooks/useInventoryPositions";
import { useInventoryKpis } from "./hooks/useInventoryKpis";

const useStyles = makeStyles({
  container: { display: "flex", flexDirection: "column", gap: tokens.spacingVerticalM },
  state: { display: "flex", alignItems: "center", gap: tokens.spacingHorizontalS },
  kpiRow: { display: "flex", flexWrap: "wrap", gap: tokens.spacingHorizontalM },
});

/**
 * Inventory position table/detail view (T036, T038, US1). Shows shelf/backroom/reconciled
 * total with a freshness indicator, and explicit loading/empty/error/stale-data states
 * per copilot-instructions.md React guidance.
 */
export function InventoryPositionView() {
  const styles = useStyles();
  const { data, isLoading, isError, error, isFetching } = useInventoryPositions();
  const kpis = useInventoryKpis(data);

  return (
    <div className={styles.container}>
      <Title2 as="h2">Inventory Positions</Title2>

      {isLoading && (
        <div className={styles.state}>
          <Spinner size="small" label="Loading inventory positions..." />
        </div>
      )}

      {isError && (
        <Body1 role="alert">
          Could not load inventory positions: {error instanceof Error ? error.message : "Unknown error"}
        </Body1>
      )}

      {!isLoading && !isError && data && data.length === 0 && (
        <Body1>No inventory positions found for the current filters.</Body1>
      )}

      {!isLoading && !isError && data && data.length > 0 && (
        <>
          <div className={styles.kpiRow}>
            {kpis.map((kpi) => (
              <KpiCard key={kpi.key} label={kpi.label} value={kpi.value} delta={kpi.delta} />
            ))}
          </div>
          {isFetching && <Body1>Refreshing...</Body1>}
          <ScrollableTableContainer>
            <Table aria-label="Inventory positions">
            <TableHeader>
              <TableRow>
                <TableHeaderCell>SKU</TableHeaderCell>
                <TableHeaderCell>Location</TableHeaderCell>
                <TableHeaderCell>Shelf</TableHeaderCell>
                <TableHeaderCell>Backroom</TableHeaderCell>
                <TableHeaderCell>Reconciled Total</TableHeaderCell>
                <TableHeaderCell>Freshness</TableHeaderCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((position) => (
                <TableRow key={position.id}>
                  <TableCell>{position.sku_id}</TableCell>
                  <TableCell>{position.location_id}</TableCell>
                  <TableCell>{position.shelf_quantity}</TableCell>
                  <TableCell>{position.backroom_quantity}</TableCell>
                  <TableCell>{position.reconciled_total}</TableCell>
                  <TableCell>
                    {position.data_freshness_warning ? (
                      <StatusBadge tone="warning" label="Stale - reconciling" />
                    ) : (
                      <StatusBadge tone="success" label="Fresh" />
                    )}
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
