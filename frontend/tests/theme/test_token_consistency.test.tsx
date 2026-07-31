import { readdirSync, readFileSync, statSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * Token-consistency test (T026, US2, FR-010). Feature screens and shared components
 * must consume the shared `tokens.ts` design tokens (brand palette, status tokens,
 * spacing scale) rather than hard-coding one-off hex/rgb colors or px gap values.
 * `theme/tokens.ts` itself is the source of truth and is exempt.
 */
const SRC_ROOT = resolve(__dirname, "../../src");

const EXEMPT_FILES = new Set([
  resolve(SRC_ROOT, "theme/tokens.ts"),
]);

const HARD_CODED_COLOR_PATTERN = /#[0-9a-fA-F]{3,8}\b|rgba?\(/;

function walk(dir: string): string[] {
  const entries = readdirSync(dir);
  const files: string[] = [];
  for (const entry of entries) {
    const fullPath = resolve(dir, entry);
    if (statSync(fullPath).isDirectory()) {
      files.push(...walk(fullPath));
    } else if (/\.(ts|tsx)$/.test(entry)) {
      files.push(fullPath);
    }
  }
  return files;
}

function collectSourceFiles(): string[] {
  return [...walk(resolve(SRC_ROOT, "features")), ...walk(resolve(SRC_ROOT, "components"))];
}

describe("design token consistency", () => {
  it("feature screens and shared components have no hard-coded one-off colors", () => {
    const offenders: string[] = [];

    for (const filePath of collectSourceFiles()) {
      if (EXEMPT_FILES.has(filePath)) {
        continue;
      }
      const contents = readFileSync(filePath, "utf-8");
      if (HARD_CODED_COLOR_PATTERN.test(contents)) {
        offenders.push(filePath);
      }
    }

    expect(offenders, `Hard-coded colors found outside theme/tokens.ts:\n${offenders.join("\n")}`).toEqual(
      [],
    );
  });

  it("feature screens and shared components use gap/spacing tokens instead of raw px literals", () => {
    const rawGapPattern = /gap:\s*["'`]\d/;
    const offenders: string[] = [];

    for (const filePath of collectSourceFiles()) {
      if (EXEMPT_FILES.has(filePath)) {
        continue;
      }
      const contents = readFileSync(filePath, "utf-8");
      if (rawGapPattern.test(contents)) {
        offenders.push(filePath);
      }
    }

    expect(offenders, `Raw px gap literals found (use tokens.* instead):\n${offenders.join("\n")}`).toEqual(
      [],
    );
  });
});
