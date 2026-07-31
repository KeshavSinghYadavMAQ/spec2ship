import { Body1, Dropdown, Input, Option, makeStyles, tokens } from "@fluentui/react-components";

export const ROLE_OPTIONS = [
  "admin",
  "regional_manager",
  "inventory_manager",
  "store_manager",
  "procurement_officer",
] as const;

const useStyles = makeStyles({
  identityBar: {
    display: "flex",
    gap: tokens.spacingHorizontalS,
    alignItems: "center",
    flexWrap: "wrap",
  },
});

interface IdentityBarProps {
  actingUserId: string;
  onActingUserIdChange: (value: string) => void;
  actingRole: string;
  onActingRoleChange: (value: string) => void;
}

/**
 * "Acting as" identity bar (T102, FR-013): captures the `X-User-Id`/`X-User-Role`
 * headers sent with RBAC-protected mutations, standing in for the Azure AD-integrated
 * auth described in research.md until that's wired up.
 */
export function IdentityBar({
  actingUserId,
  onActingUserIdChange,
  actingRole,
  onActingRoleChange,
}: IdentityBarProps) {
  const styles = useStyles();
  return (
    <div className={styles.identityBar}>
      <Body1>Acting as:</Body1>
      <Input
        value={actingUserId}
        onChange={(_e, d) => onActingUserIdChange(d.value)}
        aria-label="Acting user id"
      />
      <Dropdown
        aria-label="Acting role"
        value={actingRole}
        selectedOptions={[actingRole]}
        onOptionSelect={(_e, d) => onActingRoleChange(d.optionValue ?? actingRole)}
      >
        {ROLE_OPTIONS.map((role) => (
          <Option key={role} value={role}>
            {role}
          </Option>
        ))}
      </Dropdown>
    </div>
  );
}
