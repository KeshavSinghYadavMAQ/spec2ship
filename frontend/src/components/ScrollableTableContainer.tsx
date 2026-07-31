import type { ReactNode } from "react";
import { makeStyles, shorthands, tokens } from "@fluentui/react-components";

const useStyles = makeStyles({
  scrollContainer: {
    width: "100%",
    maxWidth: "100%",
    overflowX: "auto",
    overflowY: "auto",
    ...shorthands.borderRadius(tokens.borderRadiusXLarge),
    ...shorthands.border("1px", "solid", tokens.colorNeutralStroke2),
    boxShadow: tokens.shadow4,
    backgroundColor: tokens.colorNeutralBackground1,
  },
  content: {
    minWidth: "640px",
    "& table": {
      width: "100%",
      borderCollapse: "separate",
      borderSpacing: 0,
    },
    "& thead th": {
      position: "sticky",
      top: 0,
      zIndex: 1,
      backgroundColor: tokens.colorNeutralBackground2,
      minHeight: "56px",
    },
    "& tbody td": {
      minHeight: "56px",
    },
    "& tbody tr:hover td": {
      backgroundColor: tokens.colorNeutralBackground1Hover,
    },
  },
});

/**
 * Wraps wide data tables so they scroll within their own container at narrow
 * viewports instead of forcing the whole page to scroll horizontally (T039-T042,
 * US3, FR-009).
 */
export function ScrollableTableContainer({ children }: { children: ReactNode }) {
  const styles = useStyles();
  return (
    <div className={styles.scrollContainer}>
      <div className={styles.content}>{children}</div>
    </div>
  );
}
