import { describe, expect, it } from "vitest";

import { darkTheme, statusTokens } from "../../src/theme/tokens";

describe("dark theme tokens", () => {
  it("defines dark semantic tokens for all status tones", () => {
    expect(statusTokens.dark.success.foreground).toMatch(/^#/);
    expect(statusTokens.dark.warning.background).toMatch(/^#/);
    expect(statusTokens.dark.danger.foreground).toMatch(/^#/);
    expect(statusTokens.dark.info.background).toMatch(/^#/);
  });

  it("provides theme background and foreground entries", () => {
    expect(darkTheme.colorNeutralBackground1).toBeDefined();
    expect(darkTheme.colorNeutralForeground1).toBeDefined();
  });
});
