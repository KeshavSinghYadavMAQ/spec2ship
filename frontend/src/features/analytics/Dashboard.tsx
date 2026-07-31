import { useState } from "react";
import {
  Body1,
  Card,
  Input,
  Spinner,
  Title2,
  Title3,
  makeStyles,
  tokens,
} from "@fluentui/react-components";

import { useCostGuardrails } from "./hooks/useCostGuardrails";
import { useKpis } from "./hooks/useKpis";

const useStyles = makeStyles({
  container: { display: "flex", flexDirection: "column", gap: tokens.spacingVerticalL },
  filters: { display: "flex", gap: tokens.spacingHorizontalS, flexWrap: "wrap" },
  cards: { display: "flex", gap: tokens.spacingHorizontalL, flexWrap: "wrap" },
  card: {
    padding: tokens.spacingVerticalL,
    minWidth: "200px",
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacingVerticalXS,
  },
  metric: { fontSize: tokens.fontSizeHero800, fontWeight: tokens.fontWeightSemibold },
  breakdown: { display: "flex", flexDirection: "column", gap: tokens.spacingVerticalXS },
});

/**
 * Operational KPI dashboard (T093, US6, FR-010, FR-011): fill rate, alert staleness,
 * replenishment decision outcomes, and forecast quality distribution, scoped by
 * region/store.
 */
export function Dashboard() {
  const styles = useStyles();
  const [region, setRegion] = useState("");
  const [storeId, setStoreId] = useState("");
  const { data, isLoading, isError, error } = useKpis({
    region: region || undefined,
    storeId: storeId || undefined,
  });
  const kpi = data?.[0];
  const { data: cost } = useCostGuardrails();

  return (
    <div className={styles.container}>
      <Title2 as="h2">Operational Dashboard</Title2>

      <div className={styles.filters}>
        <Input placeholder="Filter by region" value={region} onChange={(_e, d) => setRegion(d.value)} />
        <Input placeholder="Filter by store" value={storeId} onChange={(_e, d) => setStoreId(d.value)} />
      </div>

      {cost && (
        <Card className={styles.card}>
          <Body1>Estimated ingestion cost (SC-008)</Body1>
          <span className={styles.metric}>
            ${cost.estimated_ingestion_cost_usd.toFixed(2)} / ${cost.monthly_cost_ceiling_usd.toFixed(0)}
          </span>
          <Body1 role={cost.within_ceiling ? undefined : "alert"}>
            {cost.within_ceiling ? "Within pilot ceiling" : "Over pilot ceiling"} ·{" "}
            {cost.ingested_event_count} events ingested
          </Body1>
        </Card>
      )}

      {isLoading && <Spinner size="small" label="Loading dashboard..." />}

      {isError && (
        <Body1 role="alert">
          Could not load KPIs: {error instanceof Error ? error.message : "Unknown error"}
        </Body1>
      )}

      {!isLoading && !isError && kpi && (
        <>
          <div className={styles.cards}>
            <Card className={styles.card}>
              <Body1>Fill rate</Body1>
              <span className={styles.metric}>{(kpi.fill_rate * 100).toFixed(0)}%</span>
              <Body1>{kpi.total_positions} SKU/location positions</Body1>
            </Card>
            <Card className={styles.card}>
              <Body1>Open alerts</Body1>
              <span className={styles.metric}>{kpi.open_alert_count}</span>
              <Body1>Avg age {kpi.average_alert_age_hours.toFixed(1)}h</Body1>
            </Card>
          </div>

          <div className={styles.cards}>
            <Card className={styles.card}>
              <Title3 as="h3">Recommendation outcomes</Title3>
              <div className={styles.breakdown}>
                {Object.entries(kpi.recommendation_outcomes).length === 0 && (
                  <Body1>No recommendations recorded.</Body1>
                )}
                {Object.entries(kpi.recommendation_outcomes).map(([status, count]) => (
                  <Body1 key={status}>
                    {status}: {count}
                  </Body1>
                ))}
              </div>
            </Card>
            <Card className={styles.card}>
              <Title3 as="h3">Forecast quality</Title3>
              <div className={styles.breakdown}>
                {Object.entries(kpi.forecast_quality).length === 0 && (
                  <Body1>No forecasts recorded.</Body1>
                )}
                {Object.entries(kpi.forecast_quality).map(([indicator, count]) => (
                  <Body1 key={indicator}>
                    {indicator}: {count}
                  </Body1>
                ))}
              </div>
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
