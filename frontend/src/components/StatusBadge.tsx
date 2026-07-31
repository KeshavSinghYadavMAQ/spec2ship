import { Badge, makeStyles, mergeClasses, shorthands, tokens } from "@fluentui/react-components";

import { statusTokens, useThemeMode, type StatusTone } from "../theme";

const useStyles = makeStyles({
  badge: {
    display: "inline-flex",
    alignItems: "center",
    columnGap: tokens.spacingHorizontalXS,
    borderRadius: tokens.borderRadiusCircular,
    ...shorthands.border("1px", "solid", "transparent"),
    fontWeight: tokens.fontWeightSemibold,
  },
});

export interface StatusBadgeProps {
  /** Semantic status this badge represents; drives color, icon, and default label. */
  tone: StatusTone;
  /** Overrides the tone's default label (e.g. a domain-specific severity string). */
  label?: string;
  className?: string;
}

/**
 * Shared status/severity badge (T036, FR-010). Always pairs a status color with an
 * icon and a text label so meaning never depends on color alone (WCAG 2.2 AA).
 */
export function StatusBadge({ tone, label, className }: StatusBadgeProps) {
  const styles = useStyles();
  const { mode } = useThemeMode();
  const token = statusTokens[mode][tone];
  const Icon = token.icon;

  return (
    <Badge
      appearance="tint"
      className={mergeClasses(styles.badge, className)}
      style={{
        color: token.foreground,
        backgroundColor: token.background,
        borderColor: token.foreground,
      }}
      icon={<Icon aria-hidden="true" />}
    >
      {label ?? token.label}
    </Badge>
  );
}
