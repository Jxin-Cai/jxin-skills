import fs from "node:fs/promises";
import path from "node:path";

interface Config {
  host: string;
  imageModel: string;
  size: string;
  quality: string;
  format: string;
}

interface Credentials {
  apiKey: string;
}

const DEFAULT_IMAGE_MODEL = "gpt-image-2";
const DEFAULT_SIZE = "1536x1024";
const DEFAULT_QUALITY = "auto";
const DEFAULT_FORMAT = "png";

function parseArgs(args: string[]): Record<string, string | boolean> {
  const parsed: Record<string, string | boolean> = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (!arg.startsWith("--")) continue;

    const key = arg.slice(2);
    const next = args[i + 1];
    if (!next || next.startsWith("--")) {
      parsed[key] = true;
    } else {
      parsed[key] = next;
      i++;
    }
  }

  return parsed;
}

function getStringArg(args: Record<string, string | boolean>, name: string): string | undefined {
  const value = args[name];
  return typeof value === "string" && value.trim() ? value.trim() : undefined;
}

function getWorkspace(args: Record<string, string | boolean>): string {
  const workspace = getStringArg(args, "workspace") || process.cwd();
  return path.resolve(workspace);
}

function getConfigDir(workspace: string): string {
  return path.join(workspace, ".gpt-image-gen");
}

function getConfigPath(workspace: string): string {
  return path.join(getConfigDir(workspace), "config.json");
}

function getCredentialsPath(workspace: string): string {
  return path.join(getConfigDir(workspace), "credentials.json");
}

function getEndpoint(host: string): string {
  const normalized = host.replace(/\/+$/, "");
  return normalized.endsWith("/v1") ? `${normalized}/responses` : `${normalized}/v1/responses`;
}

function redact(value: string): string {
  if (!value) return "";
  if (value.length <= 8) return `${value.slice(0, 2)}***`;
  return `${value.slice(0, 5)}***${value.slice(-4)}`;
}

function sanitizeText(text: unknown, apiKey?: string): string {
  let output = String(text ?? "");
  if (apiKey) output = output.replaceAll(apiKey, redact(apiKey));
  return output;
}

function parseSse(text: string): unknown[] {
  const events: unknown[] = [];

  for (const block of text.split(/\n\n+/)) {
    const dataLines = block
      .split(/\n/)
      .filter((line) => line.startsWith("data: "))
      .map((line) => line.slice(6));

    if (!dataLines.length) continue;

    const data = dataLines.join("\n");
    if (data === "[DONE]") continue;

    try {
      events.push(JSON.parse(data));
    } catch {
    }
  }

  return events;
}

function parseResponseText(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return parseSse(text);
  }
}

function findImageCall(value: unknown, seen = new Set<unknown>()): { result: string; status?: string } | null {
  if (!value || typeof value !== "object" || seen.has(value)) return null;
  seen.add(value);

  const record = value as Record<string, unknown>;
  if (record.type === "image_generation_call" && typeof record.result === "string" && record.result.length > 0) {
    return { result: record.result, status: typeof record.status === "string" ? record.status : undefined };
  }

  const values = Array.isArray(value) ? value : Object.values(record);
  for (const item of values) {
    const found = findImageCall(item, seen);
    if (found) return found;
  }

  return null;
}

async function readConfig(workspace: string): Promise<{ config: Config; credentials: Credentials }> {
  const [configText, credentialsText] = await Promise.all([
    fs.readFile(getConfigPath(workspace), "utf-8"),
    fs.readFile(getCredentialsPath(workspace), "utf-8"),
  ]);

  const config = JSON.parse(configText) as Config;
  const credentials = JSON.parse(credentialsText) as Credentials;

  if (!config.host || !credentials.apiKey) {
    throw new Error("配置不完整，请重新设置 host/key");
  }

  return { config, credentials };
}

async function ensurePrivateConfigDir(workspace: string): Promise<void> {
  const dir = getConfigDir(workspace);
  await fs.mkdir(dir, { recursive: true, mode: 0o700 });
  await fs.chmod(dir, 0o700).catch(() => undefined);
  await fs.writeFile(path.join(dir, ".gitignore"), "*\n!.gitignore\n", { mode: 0o600 });
}

async function validateConfig(config: Config, credentials: Credentials): Promise<{ bytes: number; status?: string }> {
  const response = await fetch(getEndpoint(config.host), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${credentials.apiKey}`,
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      model: config.imageModel,
      input: "Generate a tiny validation PNG image: a simple orange circle on a clean white background, no text.",
      size: config.size,
      quality: config.quality,
      output_format: config.format,
    }),
  });

  const text = await response.text();
  const payload = parseResponseText(text);

  if (!response.ok) {
    throw new Error(`Responses API 验证失败：HTTP ${response.status} ${sanitizeText(text, credentials.apiKey).slice(0, 1200)}`);
  }

  const imageCall = findImageCall(payload);
  if (!imageCall) {
    throw new Error(`Responses API 未返回 image_generation_call：${sanitizeText(text, credentials.apiKey).slice(0, 1200)}`);
  }

  return { bytes: Buffer.from(imageCall.result, "base64").length, status: imageCall.status };
}

async function checkConfig(workspace: string): Promise<void> {
  const { config, credentials } = await readConfig(workspace);
  console.log(JSON.stringify({
    configured: true,
    workspace,
    host: config.host,
    imageModel: config.imageModel,
    size: config.size,
    quality: config.quality,
    format: config.format,
    key: redact(credentials.apiKey),
  }, null, 2));
}

async function setConfig(args: Record<string, string | boolean>, workspace: string): Promise<void> {
  const host = getStringArg(args, "host");
  const apiKey = getStringArg(args, "key");

  if (!host || !apiKey) {
    throw new Error("--set 需要同时提供 --host 和 --key");
  }

  const config: Config = {
    host,
    imageModel: getStringArg(args, "image-model") || DEFAULT_IMAGE_MODEL,
    size: getStringArg(args, "size") || DEFAULT_SIZE,
    quality: getStringArg(args, "quality") || DEFAULT_QUALITY,
    format: getStringArg(args, "format") || DEFAULT_FORMAT,
  };
  const credentials: Credentials = { apiKey };

  console.log("正在验证 GPT 图片配置...");
  const validation = await validateConfig(config, credentials);

  await ensurePrivateConfigDir(workspace);
  await fs.writeFile(getConfigPath(workspace), `${JSON.stringify(config, null, 2)}\n`, { mode: 0o600 });
  await fs.writeFile(getCredentialsPath(workspace), `${JSON.stringify(credentials, null, 2)}\n`, { mode: 0o600 });
  await Promise.all([
    fs.chmod(getConfigPath(workspace), 0o600).catch(() => undefined),
    fs.chmod(getCredentialsPath(workspace), 0o600).catch(() => undefined),
  ]);

  console.log(JSON.stringify({
    configured: true,
    workspace,
    host: config.host,
    imageModel: config.imageModel,
    key: redact(credentials.apiKey),
    validation,
  }, null, 2));
}

async function clearConfig(workspace: string): Promise<void> {
  await fs.rm(getConfigDir(workspace), { recursive: true, force: true });
  console.log(JSON.stringify({ configured: false, cleared: true, workspace }, null, 2));
}

function printUsage(): void {
  console.error(`用法:
  bun scripts/config.ts --check --workspace <项目根目录>
  bun scripts/config.ts --set --workspace <项目根目录> --host <host> --key <key> [--image-model gpt-image-2]
  bun scripts/config.ts --clear --workspace <项目根目录>`);
}

if (import.meta.main) {
  const args = parseArgs(process.argv.slice(2));
  const workspace = getWorkspace(args);

  try {
    if (args.check) {
      await checkConfig(workspace);
    } else if (args.set) {
      await setConfig(args, workspace);
    } else if (args.clear) {
      await clearConfig(workspace);
    } else {
      printUsage();
      process.exit(1);
    }
  } catch (error) {
    console.error("错误:", sanitizeText(error instanceof Error ? error.message : error));
    process.exit(1);
  }
}

export { getEndpoint, parseResponseText, findImageCall, readConfig, redact, sanitizeText, type Config, type Credentials };
