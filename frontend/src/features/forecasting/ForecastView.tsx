import { useState } from "react";
import {
  Badge,
  Body1,
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

import { type ForecastErrorIndicator, useForecasts } from "./hooks/useForecasts";

const useStyles = makeStyles({
  container: { display: "flex", flexDirection: "column", gap: "12px" },
  filters: { display: "flex", gap: "8px", flexWrap: "wrap" },
  narration: { maxWidth: "360px" },
});

const errorIndicatorColor: Record<ForecastErrorIndicator, "success" | "warning" | "danger" | "informative"> = {
  low: "success",
  medium: "warning",
  high: "danger",
  insufficient_history: "informative",
};

/**
 * Demand forecast review view (T064, US4, FR-006, FR-007). Surfaces the
 * trend/seasonality/promotion factors and error indicator alongside the agent's
 * plain-language narration so planners can gauge confidence at a glance.
 */
export function ForecastView() {
  const styles = useStyles();
  const [skuId, setSkuId] = useState("");
  const [locationId, setLocationId] = useState("");
  const { data, isLoading, isError, error } = useForecasts({
    skuId: skuId || undefined,
    locationId: locationId || undefined,
  });

  return (
    <div className={styles.container}>
      <Title2 as="h2">Demand Forecasts</Title2>

      <div className={styles.filters}>
        <Input placeholder="Filter by SKU" value={skuId} onChange={(_e, d) => setSkuId(d.value)} />
        <Input
          placeholder="Filter by location"
          value={locationId}
          onChange={(_e, d) => setLocationId(d.value)}
        />
      </div>

      {isLoading && <Spinner size="small" label="Loading forecasts..." />}

      {isError && (
        <Body1 role="alert">
          Could not load forecasts: {error instanceof Error ? error.message : "Unknown error"}
        </Body1>
      )}

      {!isLoading && !isError && data && data.length === 0 && <Body1>No forecasts available.</Body1>}

      {!isLoading && !isError && data && data.length > 0 && (
        <Table aria-label="Demand forecasts">
          <TableHeader>
            <TableRow>
              <TableHeaderCell>SKU</TableHeaderCell>
              <TableHeaderCell>Location</TableHeaderCell>
              <TableHeaderCell>Period</TableHeaderCell>
              <TableHeaderCell>Forecast Qty</TableHeaderCell>
              <TableHeaderCell>Trend</TableHeaderCell>
              <TableHeaderCell>Confidence</TableHeaderCell>
              <TableHeaderCell>Explanation</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((forecast) => (
              <TableRow key={forecast.id}>
                <TableCell>{forecast.sku_id}</TableCell>
                <TableCell>{forecast.location_id}</TableCell>
                <TableCell>
                  {forecast.period_start} – {forecast.period_end}
                </TableCell>
                <TableCell>{forecast.forecast_quantity.toFixed(0)}</TableCell>
                <TableCell>{forecast.trend_factor.toFixed(2)}x</TableCell>
                <TableCell>
                  <Badge color={errorIndicatorColor[forecast.error_indicator]}>
                    {forecast.error_indicator.replace("_", " ")}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Title3 as="span" className={styles.narration}>
                    {forecast.narration ?? "—"}
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
