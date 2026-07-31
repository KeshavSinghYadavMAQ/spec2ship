import { describe, expect, it } from "vitest";

import { lightTheme, spacingTokens, statusTokens, typographyTokens } from "../../src/theme/tokens";

describe("light theme tokens", () => {
  it("defines non-empty typography and spacing scales", () => {
    expect(typographyTokens.fontFamilyBase.length).toBeGreaterThan(0);
    expect(typographyTokens.fontFamilyHeadings.length).toBeGreaterThan(0);
    expect(spacingTokens.md).toBe("12px");
    expect(spacingTokens.xxl).toBe("32px");
  });

  it("exposes semantic status tokens with readable labels", () => {
    expect(statusTokens.light.success.label).toBe("Healthy");
    expect(statusTokens.light.warning.label).toBe("Low stock");
    expect(statusTokens.light.danger.label).toBe("Out of stock");
  });

  it("uses a customized light brand palette", () => {
    expect(lightTheme.colorBrandBackground).toBeDefined();
    expect(lightTheme.colorNeutralBackground1).toBeDefined();
  });
});
