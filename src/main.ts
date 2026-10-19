import { describeRun, runModeFrom } from "./app.ts";

console.log(describeRun(runModeFrom(process.env)));
