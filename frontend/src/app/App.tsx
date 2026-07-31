import {
  Button,
  Subtitle1,
  makeStyles,
  shorthands,
  tokens,
} from "@fluentui/react-components";
import { useQuery } from "@tanstack/react-query";
import { WeatherMoonRegular, WeatherSunnyRegular } from "@fluentui/react-icons";
import { Route, Routes, useNavigate } from "react-router-dom";

import { AuthGuard } from "../components/AuthGuard";
import { NavItem } from "../components/NavItem";
import { primaryNavigation } from "./navigation";
import { InventoryPositionView } from "../features/inventory/InventoryPositionView";
import { AlertWorklist } from "../features/alerting/AlertWorklist";
import { RecommendationPanel } from "../features/replenishment/RecommendationPanel";
import { ForecastView } from "../features/forecasting/ForecastView";
import { TransferSuggestions } from "../features/transfer-balance/TransferSuggestions";
import { StorePriorityView } from "../features/transfer-balance/StorePriorityView";
import { LoginPage } from "../features/auth/LoginPage";
import { ProductLocationPolicyAdmin } from "../features/admin/ProductLocationPolicyAdmin";
import { SampleDataPanel } from "../features/admin/SampleDataPanel";
import { Dashboard } from "../features/analytics/Dashboard";
import { authClient } from "../services/authClient";
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
    gap: tokens.spacingHorizontalL,
    ...shorthands.padding(tokens.spacingVerticalL, tokens.spacingHorizontalXXL),
    borderBottom: `1px solid ${tokens.colorNeutralStroke1}`,
    backgroundColor: tokens.colorNeutralBackground2,
  },
  nav: {
    display: "flex",
    flexWrap: "wrap",
    gap: `${tokens.spacingVerticalS} ${tokens.spacingHorizontalM}`,
  },
  main: {
    flex: 1,
    minWidth: 0,
    ...shorthands.padding(tokens.spacingVerticalXXL),
  },
});

export function App() {
  const styles = useStyles();
  const { mode, toggleMode } = useThemeMode();
  const navigate = useNavigate();
  const sessionQuery = useQuery({
    queryKey: ["auth", "session"],
    queryFn: authClient.getSession,
    retry: false,
  });

  async function handleLogout() {
    await authClient.logout();
    await sessionQuery.refetch();
    navigate("/login", { replace: true });
  }

  return (
    <div className={styles.shell}>
      <header className={styles.header}>
        <Subtitle1 as="h1">Retail Replenishment</Subtitle1>
        <nav className={styles.nav} aria-label="Primary">
          {primaryNavigation.map((item) => (
            <NavItem key={item.to} to={item.to} label={item.label} icon={item.icon} />
          ))}
        </nav>
        <Button
          appearance="subtle"
          icon={mode === "dark" ? <WeatherSunnyRegular /> : <WeatherMoonRegular />}
          onClick={toggleMode}
          aria-label={`Switch to ${mode === "dark" ? "light" : "dark"} mode`}
        >
          {mode === "dark" ? "Light mode" : "Dark mode"}
        </Button>
        {sessionQuery.data?.authenticated ? (
          <Button appearance="subtle" onClick={handleLogout}>
            Logout
          </Button>
        ) : null}
      </header>
      <main className={styles.main}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <AuthGuard>
                <InventoryPositionView />
              </AuthGuard>
            }
          />
          <Route
            path="/inventory"
            element={
              <AuthGuard>
                <InventoryPositionView />
              </AuthGuard>
            }
          />
          <Route
            path="/alerts"
            element={
              <AuthGuard>
                <AlertWorklist />
              </AuthGuard>
            }
          />
          <Route
            path="/replenishment"
            element={
              <AuthGuard>
                <RecommendationPanel />
              </AuthGuard>
            }
          />
          <Route
            path="/forecasts"
            element={
              <AuthGuard>
                <ForecastView />
              </AuthGuard>
            }
          />
          <Route
            path="/transfers"
            element={
              <AuthGuard>
                <TransferSuggestions />
              </AuthGuard>
            }
          />
          <Route
            path="/store-priority"
            element={
              <AuthGuard>
                <StorePriorityView />
              </AuthGuard>
            }
          />
          <Route
            path="/analytics"
            element={
              <AuthGuard>
                <Dashboard />
              </AuthGuard>
            }
          />
          <Route
            path="/admin/policies"
            element={
              <AuthGuard>
                <ProductLocationPolicyAdmin />
              </AuthGuard>
            }
          />
          <Route
            path="/admin/sample-data"
            element={
              <AuthGuard>
                <SampleDataPanel />
              </AuthGuard>
            }
          />
        </Routes>
      </main>
    </div>
  );
}
