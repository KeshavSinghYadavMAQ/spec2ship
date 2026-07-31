import { Body1, Card, makeStyles, tokens } from "@fluentui/react-components";

const useStyles = makeStyles({
  card: {
    minWidth: "180px",
    display: "flex",
    flexDirection: "column",
    gap: tokens.spacingVerticalXS,
    padding: tokens.spacingVerticalM,
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    borderRadius: tokens.borderRadiusLarge,
  },
  value: {
    fontSize: tokens.fontSizeHero700,
    fontWeight: tokens.fontWeightSemibold,
    color: tokens.colorBrandForeground1,
  },
  delta: {
    color: tokens.colorNeutralForeground2,
  },
});

export type KpiCardProps = {
  label: string;
  value: string;
  delta?: string;
};

export function KpiCard({ label, value, delta }: KpiCardProps) {
  const styles = useStyles();

  return (
    <Card className={styles.card}>
      <Body1>{label}</Body1>
      <span className={styles.value}>{value}</span>
      {delta ? <Body1 className={styles.delta}>{delta}</Body1> : null}
    </Card>
  );
}
