import {
  AlertFilled,
  ArrowSwapRegular,
  BoxFilled,
  ClipboardTaskRegular,
  DataTrendingRegular,
  GridRegular,
  PersonSettingsRegular,
  PulseRegular,
  SparkleRegular,
  type FluentIcon,
} from "@fluentui/react-icons";

export type NavItemConfig = {
  to: string;
  label: string;
  icon: FluentIcon;
};

export const primaryNavigation: NavItemConfig[] = [
  { to: "/inventory", label: "Inventory", icon: BoxFilled },
  { to: "/alerts", label: "Alerts", icon: AlertFilled },
  { to: "/replenishment", label: "Replenishment", icon: ClipboardTaskRegular },
  { to: "/forecasts", label: "Forecasts", icon: DataTrendingRegular },
  { to: "/transfers", label: "Transfers", icon: ArrowSwapRegular },
  { to: "/store-priority", label: "Store Priority", icon: SparkleRegular },
  { to: "/analytics", label: "Analytics", icon: PulseRegular },
  { to: "/admin/policies", label: "Admin", icon: PersonSettingsRegular },
  { to: "/admin/sample-data", label: "Sample Data", icon: GridRegular },
];
