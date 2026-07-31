import {
  Body1,
  Button,
  Subtitle1,
  makeStyles,
  shorthands,
  tokens,
} from "@fluentui/react-components";
import { WeatherMoonRegular, WeatherSunnyRegular } from "@fluentui/react-icons";
import { NavLink, Route, Routes } from "react-router-dom";

import { InventoryPositionView } from "../features/inventory/InventoryPositionView";
import { AlertWorklist } from "../features/alerting/AlertWorklist";
import { RecommendationPanel } from "../features/replenishment/RecommendationPanel";
import { ForecastView } from "../features/forecasting/ForecastView";
import { TransferSuggestions } from "../features/transfer-balance/TransferSuggestions";
import { StorePriorityView } from "../features/transfer-balance/StorePriorityView";
import { ProductLocationPolicyAdmin } from "../features/admin/ProductLocationPolicyAdmin";
import { Dashboard } from "../features/analytics/Dashboard";
import { useThemeMode } from "../theme";

const useStyles = makeStyles({
  shell: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    backgroundColor: tokens.colorNeutralBackground1,
    color: tokens.colorNeutralForeground1,
  },
  header: {
    display: "flex",
    flexWrap: "wrap",
    alignItems: "center",
    justifyContent: "space-between",
    gap: "8px",
    ...shorthands.padding("12px", "20px"),
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
  },
  nav: {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px 16px",
  },
  main: {
    flex: 1,
    minWidth: 0,
    ...shorthands.padding("20px"),
  },
});

const navLinkStyle = ({ isActive }: { isActive: boolean }) => ({
  fontWeight: isActive ? 700 : 400,
  textDecoration: "none",
  color: "inherit",
});

export function App() {
  const styles = useStyles();
  const { mode, toggleMode } = useThemeMode();

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <Subtitle1 as="h1">Retail Replenishment</Subtitle1>
        <nav className={styles.nav} aria-label="Primary">
          <NavLink to="/inventory" style={navLinkStyle}>
            <Body1>Inventory</Body1>
          </NavLink>
          <NavLink to="/alerts" style={navLinkStyle}>
            <Body1>Alerts</Body1>
          </NavLink>
          <NavLink to="/replenishment" style={navLinkStyle}>
            <Body1>Replenishment</Body1>
          </NavLink>
          <NavLink to="/forecasts" style={navLinkStyle}>
            <Body1>Forecasts</Body1>
          </NavLink>
          <NavLink to="/transfers" style={navLinkStyle}>
            <Body1>Transfers</Body1>
          </NavLink>
          <NavLink to="/store-priority" style={navLinkStyle}>
            <Body1>Store Priority</Body1>
          </NavLink>
          <NavLink to="/analytics" style={navLinkStyle}>
            <Body1>Analytics</Body1>
          </NavLink>
          <NavLink to="/admin/policies" style={navLinkStyle}>
            <Body1>Admin</Body1>
          </NavLink>
        </nav>
        <Button
          appearance="subtle"
          icon={mode === "dark" ? <WeatherSunnyRegular /> : <WeatherMoonRegular />}
          onClick={toggleMode}
          aria-label={`Switch to ${mode === "dark" ? "light" : "dark"} mode`}
        >
          {mode === "dark" ? "Light mode" : "Dark mode"}
        </Button>
      </header>
      <main className={styles.main}>
        <Routes>
          <Route path="/" element={<InventoryPositionView />} />
          <Route path="/inventory" element={<InventoryPositionView />} />
          <Route path="/alerts" element={<AlertWorklist />} />
          <Route path="/replenishment" element={<RecommendationPanel />} />
          <Route path="/forecasts" element={<ForecastView />} />
          <Route path="/transfers" element={<TransferSuggestions />} />
          <Route path="/store-priority" element={<StorePriorityView />} />
          <Route path="/analytics" element={<Dashboard />} />
          <Route path="/admin/policies" element={<ProductLocationPolicyAdmin />} />
        </Routes>
      </main>
    </div>
  );
}
