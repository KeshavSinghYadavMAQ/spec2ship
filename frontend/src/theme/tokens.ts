/**
 * Design tokens (T010, T011, T045, US2/US3/US4, FR-010).
 *
 * `brandVariants`: a custom, colorful Fluent UI `BrandVariants` ramp (16 steps, 10-160)
 * used to derive both the light and dark themes via `createLightTheme`/`createDarkTheme`
 * (research.md #5), replacing the default `webLightTheme`/`webDarkTheme`.
 *
 * `statusTokens`: semantic success/warning/danger/info colors, each paired with a
 * non-color affordance (icon + text label) so status is never conveyed by color alone
 * (FR-010, WCAG 2.2 AA). Values are hand-tuned to keep foreground/background contrast at
 * or above 4.5:1 in both themes (T045).
 */
import { CheckmarkCircleFilled, DismissCircleFilled, InfoFilled, WarningFilled, type FluentIcon } from "@fluentui/react-icons";
import {
  createDarkTheme,
  createLightTheme,
  type BrandVariants,
  type Theme,
} from "@fluentui/react-components";

/** A cobalt-and-teal retail brand ramp from light tints (10) to deep shades (160). */
export const brandVariants: BrandVariants = {
  10: "#06101C",
  20: "#0B1F33",
  30: "#10304A",
  40: "#154363",
  50: "#1A567D",
  60: "#1F6997",
  70: "#267CB1",
  80: "#2C90CB",
  90: "#39A4E1",
  100: "#56B4E8",
  110: "#74C3ED",
  120: "#92D2F2",
  130: "#B0E0F6",
  140: "#CDECF9",
  150: "#E6F5FC",
  160: "#F6FCFF",
};

export const lightTheme: Theme = createLightTheme(brandVariants);
export const darkTheme: Theme = createDarkTheme(brandVariants);

export type StatusTone = "success" | "warning" | "danger" | "info";

export interface StatusToken {
  /** Foreground/icon color, tuned for >= 4.5:1 contrast against its paired background. */
  foreground: string;
  /** Background tint for badges/chips. */
  background: string;
  /** Icon component - always render alongside the label so color is never the only signal. */
  icon: FluentIcon;
  /** Default human-readable label paired with the icon (FR-010). */
  label: string;
}

export interface StatusTokens {
  light: Record<StatusTone, StatusToken>;
  dark: Record<StatusTone, StatusToken>;
}

export const statusTokens: StatusTokens = {
  light: {
    success: {
      foreground: "#166534",
      background: "#DCFCE7",
      icon: CheckmarkCircleFilled,
      label: "Healthy",
    },
    warning: {
      foreground: "#92400E",
      background: "#FFEDD5",
      icon: WarningFilled,
      label: "Low stock",
    },
    danger: {
      foreground: "#991B1B",
      background: "#FEE2E2",
      icon: DismissCircleFilled,
      label: "Out of stock",
    },
    info: {
      foreground: "#1E3A8A",
      background: "#DBEAFE",
      icon: InfoFilled,
      label: "Informational",
    },
  },
  dark: {
    success: {
      foreground: "#86EFAC",
      background: "#052E1A",
      icon: CheckmarkCircleFilled,
      label: "Healthy",
    },
    warning: {
      foreground: "#FDBA74",
      background: "#3A1B00",
      icon: WarningFilled,
      label: "Low stock",
    },
    danger: {
      foreground: "#FCA5A5",
      background: "#450A0A",
      icon: DismissCircleFilled,
      label: "Out of stock",
    },
    info: {
      foreground: "#93C5FD",
      background: "#172554",
      icon: InfoFilled,
      label: "Informational",
    },
  },
};

export const typographyTokens = {
  fontFamilyBase: '"Segoe UI Variable Display", "Aptos", "Trebuchet MS", sans-serif',
  fontFamilyHeadings: '"Bahnschrift", "Segoe UI Variable Display", sans-serif',
  fontSizeDisplay: "2rem",
  fontSizeHeading: "1.375rem",
  fontSizeBody: "0.9375rem",
  fontSizeCaption: "0.8125rem",
};

/** Shared spacing scale (px) so feature screens stop hand-rolling one-off gap/padding values. */
export const spacingTokens = {
  xs: "4px",
  sm: "8px",
  md: "12px",
  lg: "16px",
  xl: "24px",
  xxl: "32px",
};

/** Responsive breakpoints (FR-009, US3): 360px mobile minimum, 768px tablet, 1440px desktop. */
export const breakpoints = {
  mobile: "360px",
  tablet: "768px",
  desktop: "1440px",
};

export const mediaQueries = {
  tabletUp: `@media (min-width: ${breakpoints.tablet})`,
  desktopUp: `@media (min-width: ${breakpoints.desktop})`,
};
