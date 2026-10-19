import { describe, expect, it } from "vitest";
import { APP_NAME, describeRun, runModeFrom } from "../src/app.ts";

describe("app", () => {
  it("defaults to dry-run unless DRY_RUN is explicitly false", () => {
    expect(runModeFrom({})).toBe("dry-run");
    expect(runModeFrom({ DRY_RUN: "true" })).toBe("dry-run");
    expect(runModeFrom({ DRY_RUN: "FALSE" })).toBe("live");
  });

  it("describes the run with the app name", () => {
    expect(describeRun("dry-run")).toBe(`${APP_NAME} starting in dry-run mode`);
  });
});
