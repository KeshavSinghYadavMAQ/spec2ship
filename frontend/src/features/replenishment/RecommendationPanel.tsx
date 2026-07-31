import { useState } from "react";
import {
  Body1,
  Button,
  Dropdown,
  Input,
  Option,
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
  type ActionabilityRating,
  type ReplenishmentRecommendation,
  useDecideRecommendation,
  useRecommendations,
} from "./hooks/useRecommendations";
import { IdentityBar } from "../../components/IdentityBar";
import { ScrollableTableContainer } from "../../components/ScrollableTableContainer";

const useStyles = makeStyles({
  container: { display: "flex", flexDirection: "column", gap: tokens.spacingVerticalM },
  rowActions: {
    display: "flex",
    gap: tokens.spacingHorizontalS,
    alignItems: "center",
    flexWrap: "wrap",
  },
  narration: { maxWidth: "360px" },
});

/**
 * Replenishment recommendation review panel (T056, T057, US3; T105/SC-004 actionability
 * rating capture). Every accept/override/dismiss decision requires an actionability
 * rating so operator feedback can be measured against SC-004.
 */
export function RecommendationPanel() {
  const styles = useStyles();
  const [actingUserId, setActingUserId] = useState("inventory-manager-1");
  const [actingRole, setActingRole] = useState("inventory_manager");
  const { data, isLoading, isError, error } = useRecommendations();

  return (
    <div className={styles.container}>
      <Title2 as="h2">Replenishment Recommendations</Title2>

      <IdentityBar
        actingUserId={actingUserId}
        onActingUserIdChange={setActingUserId}
        actingRole={actingRole}
        onActingRoleChange={setActingRole}
      />

      {isLoading && <Spinner size="small" label="Loading recommendations..." />}

      {isError && (
        <Body1 role="alert">
          Could not load recommendations: {error instanceof Error ? error.message : "Unknown error"}
        </Body1>
      )}

      {!isLoading && !isError && data && data.length === 0 && (
        <Body1>No pending recommendations.</Body1>
      )}

      {!isLoading && !isError && data && data.length > 0 && (
        <ScrollableTableContainer>
        <Table aria-label="Replenishment recommendations">
          <TableHeader>
            <TableRow>
              <TableHeaderCell>SKU</TableHeaderCell>
              <TableHeaderCell>Location</TableHeaderCell>
              <TableHeaderCell>Recommended Qty</TableHeaderCell>
              <TableHeaderCell>By Date</TableHeaderCell>
              <TableHeaderCell>Explanation</TableHeaderCell>
              <TableHeaderCell>Status</TableHeaderCell>
              <TableHeaderCell>Decision</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((recommendation) => (
              <RecommendationRow
                key={recommendation.id}
                recommendation={recommendation}
                actingUserId={actingUserId}
                actingRole={actingRole}
              />
            ))}
          </TableBody>
        </Table>
        </ScrollableTableContainer>
      )}
    </div>
  );
}

function RecommendationRow({
  recommendation,
  actingUserId,
  actingRole,
}: {
  recommendation: ReplenishmentRecommendation;
  actingUserId: string;
  actingRole: string;
}) {
  const styles = useStyles();
  const decide = useDecideRecommendation(actingUserId, actingRole);
  const [rating, setRating] = useState<ActionabilityRating | undefined>(
    recommendation.actionability_rating ?? undefined,
  );
  const [overrideReason, setOverrideReason] = useState("");
  const [showOverrideInput, setShowOverrideInput] = useState(false);

  const isDecided = recommendation.status !== "proposed";
  const canSubmit = Boolean(rating);

  const submit = (decision: "accepted" | "overridden" | "dismissed") => {
    decide.mutate({
      recommendationId: recommendation.id,
      decision,
      actionabilityRating: rating,
      overrideReason: decision === "overridden" ? overrideReason : undefined,
    });
  };

  return (
    <TableRow>
      <TableCell>{recommendation.sku_id}</TableCell>
      <TableCell>{recommendation.location_id}</TableCell>
      <TableCell>{recommendation.recommended_quantity}</TableCell>
      <TableCell>{recommendation.recommended_by_date}</TableCell>
      <TableCell>
        <Title3 as="span" className={styles.narration}>
          {recommendation.rationale.narration}
        </Title3>
      </TableCell>
      <TableCell>{recommendation.status}</TableCell>
      <TableCell>
        {isDecided ? (
          <Body1>Decision recorded</Body1>
        ) : (
          <div className={styles.rowActions}>
            <Dropdown
              aria-label="Actionability rating"
              placeholder="Rate actionability"
              value={rating ? (rating === "actionable" ? "Actionable" : "Not actionable") : ""}
              onOptionSelect={(_event, data) =>
                setRating(data.optionValue as ActionabilityRating | undefined)
              }
            >
              <Option value="actionable">Actionable</Option>
              <Option value="not_actionable">Not actionable</Option>
            </Dropdown>
            <Button size="small" disabled={!canSubmit || decide.isPending} onClick={() => submit("accepted")}>
              Accept
            </Button>
            <Button
              size="small"
              disabled={!canSubmit || decide.isPending}
              onClick={() => submit("dismissed")}
            >
              Dismiss
            </Button>
            {showOverrideInput ? (
              <>
                <Input
                  placeholder="Override reason"
                  value={overrideReason}
                  onChange={(_event, data) => setOverrideReason(data.value)}
                />
                <Button
                  size="small"
                  disabled={!canSubmit || !overrideReason || decide.isPending}
                  onClick={() => submit("overridden")}
                >
                  Confirm Override
                </Button>
              </>
            ) : (
              <Button size="small" appearance="subtle" onClick={() => setShowOverrideInput(true)}>
                Override
              </Button>
            )}
          </div>
        )}
      </TableCell>
    </TableRow>
  );
}
