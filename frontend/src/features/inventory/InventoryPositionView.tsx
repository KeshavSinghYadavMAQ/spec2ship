import {
  Badge,
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
} from "@fluentui/react-components";

import { useInventoryPositions } from "./hooks/useInventoryPositions";

const useStyles = makeStyles({
  container: { display: "flex", flexDirection: "column", gap: "12px" },
  state: { display: "flex", alignItems: "center", gap: "8px" },
});

/**
 * Inventory position table/detail view (T036, T038, US1). Shows shelf/backroom/reconciled
 * total with a freshness indicator, and explicit loading/empty/error/stale-data states
 * per copilot-instructions.md React guidance.
 */
export function InventoryPositionView() {
  const styles = useStyles();
  const { data, isLoading, isError, error, isFetching } = useInventoryPositions();

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
          {isFetching && <Body1>Refreshing...</Body1>}
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
                      <Badge color="warning">Stale - reconciling</Badge>
                    ) : (
                      <Badge color="success">Fresh</Badge>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </>
      )}
    </div>
  );
}
