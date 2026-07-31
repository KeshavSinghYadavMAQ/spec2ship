import { Body1, makeStyles, mergeClasses, shorthands, tokens } from "@fluentui/react-components";
import type { FluentIcon } from "@fluentui/react-icons";
import { NavLink } from "react-router-dom";

const useStyles = makeStyles({
  link: {
    textDecoration: "none",
    color: "inherit",
  },
  pill: {
    display: "inline-flex",
    alignItems: "center",
    columnGap: tokens.spacingHorizontalXS,
    ...shorthands.padding(tokens.spacingVerticalXS, tokens.spacingHorizontalM),
    borderRadius: tokens.borderRadiusCircular,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    transitionProperty: "background-color, color, border-color, box-shadow",
    transitionDuration: "180ms",
    transitionTimingFunction: "ease",
  },
  inactive: {
    color: tokens.colorNeutralForeground2,
    backgroundColor: tokens.colorNeutralBackground1,
  },
  active: {
    color: tokens.colorBrandForeground1,
    backgroundColor: tokens.colorBrandBackground2,
    ...shorthands.border("1px", "solid", tokens.colorBrandStroke1),
    boxShadow: tokens.shadow4,
  },
});

type NavItemProps = {
  to: string;
  label: string;
  icon: FluentIcon;
};

export function NavItem({ to, label, icon: Icon }: NavItemProps) {
  const styles = useStyles();

  return (
    <NavLink to={to} className={styles.link}>
      {({ isActive }) => (
        <span
          className={mergeClasses(styles.pill, isActive ? styles.active : styles.inactive)}
          aria-current={isActive ? "page" : undefined}
        >
          <Icon aria-hidden="true" />
          <Body1>{label}</Body1>
        </span>
      )}
    </NavLink>
  );
}
