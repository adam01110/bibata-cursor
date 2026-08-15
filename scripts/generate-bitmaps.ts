#!/usr/bin/env bun

import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { availableParallelism, tmpdir } from "node:os";
import path from "node:path";

type ColorReplacement = {
  match: string;
  replace: string;
};

type RenderOptions = {
  dir: string;
  out: string;
  colors?: ColorReplacement[];
  fps?: number;
  use?: "default" | "puppeteer";
};

type RenderConfig = Record<string, RenderOptions>;

type WorkerResult = {
  index: number;
  exitCode: number;
  stderr: string;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isColorReplacement(value: unknown): value is ColorReplacement {
  return isRecord(value) && typeof value.match === "string" && typeof value.replace === "string";
}

function isRenderOptions(value: unknown): value is RenderOptions {
  return (
    isRecord(value) &&
    typeof value.dir === "string" &&
    typeof value.out === "string" &&
    (value.colors === undefined ||
      (Array.isArray(value.colors) && value.colors.every(isColorReplacement))) &&
    (value.fps === undefined || typeof value.fps === "number") &&
    (value.use === undefined || value.use === "default" || value.use === "puppeteer")
  );
}

function isRenderConfig(value: unknown): value is RenderConfig {
  return isRecord(value) && Object.values(value).every(isRenderOptions);
}

const configPath = process.argv[2] ?? "render.json";
const config: unknown = await Bun.file(configPath).json();

if (!isRenderConfig(config)) {
  throw new TypeError(`Invalid render configuration in ${configPath}`);
}

const entries = Object.entries(config);

if (entries.length === 0) {
  throw new Error(`No render configurations found in ${configPath}`);
}

const requestedJobs = Number.parseInt(process.env.BIBATA_GENERATE_JOBS ?? "", 10);
const defaultJobs = Math.min(4, availableParallelism());
const jobCount = Math.min(
  entries.length,
  Number.isInteger(requestedJobs) && requestedJobs > 0 ? requestedJobs : defaultJobs,
);
const entriesPerJob = Math.ceil(entries.length / jobCount);
const shards = Array.from({ length: jobCount }, (_, index) =>
  entries.slice(index * entriesPerJob, (index + 1) * entriesPerJob),
).filter((shard) => shard.length > 0);

const temporaryDirectory = await mkdtemp(path.join(tmpdir(), "bibata-render-"));
const cbmpPath = path.resolve(import.meta.dir, "../node_modules/cbmp/bin/cbmp.js");

console.log(`Rendering ${entries.length} configurations with ${shards.length} workers`);

try {
  const results = await Promise.all(
    shards.map(async (shard, index) => {
      const shardPath = path.join(temporaryDirectory, `${index}.json`);
      await writeFile(shardPath, JSON.stringify(Object.fromEntries(shard)));

      const child = Bun.spawn([process.execPath, cbmpPath, shardPath], {
        cwd: process.cwd(),
        stdout: "ignore",
        stderr: "pipe",
      });
      const stderr = new Response(child.stderr).text();
      const exitCode = await child.exited;
      return { index, exitCode, stderr: await stderr } satisfies WorkerResult;
    }),
  );

  const failures = results.filter(({ exitCode }) => exitCode !== 0);
  if (failures.length > 0) {
    for (const { index, exitCode, stderr } of failures) {
      console.error(`Worker ${index + 1} failed with exit code ${exitCode}`);
      console.error(stderr.trim());
    }
    process.exitCode = 1;
  } else {
    console.log("Bitmap generation completed");
  }
} finally {
  await rm(temporaryDirectory, { recursive: true, force: true });
}
