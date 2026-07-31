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

import { StatusBadge } from "../../components/StatusBadge";
import { ScrollableTableContainer } from "../../components/ScrollableTableContainer";
import { ApiError, type PolicyInput, usePolicies, useUpsertPolicy } from "./hooks/usePolicies";

const useStyles = makeStyles({
  container: { display: "flex", flexDirection: "column", gap: tokens.spacingVerticalL },
  identityBar: { display: "flex", gap: tokens.spacingHorizontalS, alignItems: "center", flexWrap: "wrap" },
  form: { display: "flex", gap: tokens.spacingHorizontalS, flexWrap: "wrap", alignItems: "flex-end" },
  field: { display: "flex", flexDirection: "column", gap: tokens.spacingVerticalXS, minWidth: "140px" },
});

const numericFields: (keyof PolicyInput)[] = [
  "low_stock_threshold",
  "out_of_stock_threshold",
  "reorder_point",
  "min_qty",
  "max_qty",
  "safety_stock",
];

const emptyForm: PolicyInput = {
  sku_id: "",
  location_id: "",
  low_stock_threshold: 0,
  out_of_stock_threshold: 0,
  reorder_point: 0,
  min_qty: 0,
  max_qty: 0,
  safety_stock: 0,
};

/**
 * Product-location threshold admin panel (T079, US7, FR-016, FR-017, FR-018, FR-023).
 * Shows validation feedback (422) and edit-lock state (409, held during an in-flight
 * evaluation) so admins understand why a save was rejected rather than silently failing.
 */
export function ProductLocationPolicyAdmin() {
  const styles = useStyles();
  const [actingUserId, setActingUserId] = useState("admin-1");
  const [actingRole, setActingRole] = useState("admin");
  const [form, setForm] = useState<PolicyInput>(emptyForm);
  const [feedback, setFeedback] = useState<{ kind: "success" | "error"; message: string } | null>(
    null,
  );

  const { data, isLoading, isError, error } = usePolicies();
  const upsertPolicy = useUpsertPolicy(actingUserId, actingRole);

  const submit = () => {
    setFeedback(null);
    upsertPolicy.mutate(form, {
      onSuccess: () => {
        setFeedback({ kind: "success", message: "Policy saved." });
        setForm(emptyForm);
      },
      onError: (mutationError) => {
        if (mutationError instanceof ApiError) {
          if (mutationError.status === 409) {
            setFeedback({
              kind: "error",
              message: "Locked by an in-flight evaluation. Retry after the current cycle completes.",
            });
            return;
          }
          setFeedback({ kind: "error", message: mutationError.detail });
          return;
        }
        setFeedback({ kind: "error", message: "Unknown error saving policy." });
      },
    });
  };

  return (
    <div className={styles.container}>
      <Title2 as="h2">Product-Location Threshold Admin</Title2>

      <div className={styles.identityBar}>
        <Body1>Acting as:</Body1>
        <Input value={actingUserId} onChange={(_e, d) => setActingUserId(d.value)} aria-label="Acting user id" />
        <Dropdown
          aria-label="Acting role"
          value={actingRole}
          selectedOptions={[actingRole]}
          onOptionSelect={(_e, d) => setActingRole(d.optionValue ?? "admin")}
        >
          <Option value="admin">admin</Option>
          <Option value="regional_manager">regional_manager</Option>
          <Option value="inventory_manager">inventory_manager</Option>
          <Option value="store_manager">store_manager</Option>
          <Option value="procurement_officer">procurement_officer</Option>
        </Dropdown>
      </div>

      <Title3 as="h3">Set / update threshold</Title3>
      <div className={styles.form}>
        <div className={styles.field}>
          <Body1 id="policy-sku-label">SKU</Body1>
          <Input
            aria-labelledby="policy-sku-label"
            value={form.sku_id}
            onChange={(_e, d) => setForm({ ...form, sku_id: d.value })}
          />
        </div>
        <div className={styles.field}>
          <Body1 id="policy-location-label">Location</Body1>
          <Input
            aria-labelledby="policy-location-label"
            value={form.location_id}
            onChange={(_e, d) => setForm({ ...form, location_id: d.value })}
          />
        </div>
        {numericFields.map((field) => (
          <div className={styles.field} key={field}>
            <Body1 id={`policy-${field}-label`}>{field.replace(/_/g, " ")}</Body1>
            <Input
              type="number"
              aria-labelledby={`policy-${field}-label`}
              value={String(form[field])}
              onChange={(_e, d) => setForm({ ...form, [field]: Number(d.value) || 0 })}
            />
          </div>
        ))}
        <Button
          appearance="primary"
          disabled={!form.sku_id || !form.location_id || upsertPolicy.isPending}
          onClick={submit}
        >
          Save policy
        </Button>
      </div>

      {feedback && (
        <Body1 role={feedback.kind === "error" ? "alert" : undefined}>{feedback.message}</Body1>
      )}

      {isLoading && <Spinner size="small" label="Loading policies..." />}

      {isError && (
        <Body1 role="alert">
          Could not load policies: {error instanceof Error ? error.message : "Unknown error"}
        </Body1>
      )}

      {!isLoading && !isError && data && data.length === 0 && <Body1>No policies configured.</Body1>}

      {!isLoading && !isError && data && data.length > 0 && (
        <ScrollableTableContainer>
        <Table aria-label="Product-location policies">
          <TableHeader>
            <TableRow>
              <TableHeaderCell>SKU</TableHeaderCell>
              <TableHeaderCell>Location</TableHeaderCell>
              <TableHeaderCell>Low stock</TableHeaderCell>
              <TableHeaderCell>Out of stock</TableHeaderCell>
              <TableHeaderCell>Reorder point</TableHeaderCell>
              <TableHeaderCell>Min / Max</TableHeaderCell>
              <TableHeaderCell>Lock</TableHeaderCell>
              <TableHeaderCell>Updated by</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((policy) => (
              <TableRow key={policy.id}>
                <TableCell>{policy.sku_id}</TableCell>
                <TableCell>{policy.location_id}</TableCell>
                <TableCell>{policy.low_stock_threshold}</TableCell>
                <TableCell>{policy.out_of_stock_threshold}</TableCell>
                <TableCell>{policy.reorder_point}</TableCell>
                <TableCell>
                  {policy.min_qty} / {policy.max_qty}
                </TableCell>
                <TableCell>
                  <StatusBadge
                    tone={policy.edit_lock_held ? "warning" : "success"}
                    label={policy.edit_lock_held ? "Locked" : "Editable"}
                  />
                </TableCell>
                <TableCell>{policy.updated_by ?? "—"}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        </ScrollableTableContainer>
      )}
    </div>
  );
}
