/**
 * Application identity and run description.
 *
 * Kept free of side effects so it can be imported from tests; `main.ts` is
 * the only module that touches the process.
 */

export const APP_NAME = "meseta-ingesta";

export type RunMode = "dry-run" | "live";

/** Reads the run mode from the environment. Anything but an explicit `false` is dry-run. */
export function runModeFrom(env: Readonly<Record<string, string | undefined>>): RunMode {
  return env["DRY_RUN"]?.trim().toLowerCase() === "false" ? "live" : "dry-run";
}

export function describeRun(mode: RunMode): string {
  return `${APP_NAME} starting in ${mode} mode`;
}
