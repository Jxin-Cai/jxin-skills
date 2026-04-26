import fs from "node:fs/promises";
import path from "node:path";
import { findImageCall, getEndpoint, parseResponseText, readConfig, sanitizeText } from "./config.js";

interface GenerateOptions {
  workspace: string;
  promptFile: string;
  output: string;
  size?: string;
  quality?: string;
  format?: string;
}

const MAX_RETRIES = 2;
const RETRY_DELAY_MS = 60_000;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function parseArgs(args: string[]): Record<string, string | boolean> {
  const parsed: Record<string, string | boolean> = {};

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (!arg.startsWith("--") && arg !== "-p" && arg !== "-o") continue;

    const key = arg === "-p" ? "prompt-file" : arg === "-o" ? "output" : arg.slice(2);
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

function isRetryableGenerateError(error: unknown): boolean {
  const message = error instanceof Error ? error.message : String(error);
  return /(429|5\d\d|rate limit|timed out|timeout|fetch failed|ECONNREFUSED|AbortError|ConnectionRefused)/i.test(message);
}

async function getDefaultImageOutputPath(promptFile: string): Promise<string> {
  const promptFileAbs = path.isAbsolute(promptFile)
    ? promptFile
    : path.resolve(process.cwd(), promptFile);

  const promptDir = path.dirname(promptFileAbs);
  const promptBasename = path.basename(promptFile, path.extname(promptFile));

  if (path.basename(promptDir) === "prompts") {
    return path.join(path.dirname(promptDir), "images", `${promptBasename}.png`);
  }

  return path.join(process.cwd(), "image_output", "images", `${promptBasename}.png`);
}

async function generateImageOnce(options: GenerateOptions): Promise<string> {
  console.log(`读取提示词：${options.promptFile}`);
  const prompt = await fs.readFile(options.promptFile, "utf-8");

  if (!prompt.trim()) {
    throw new Error("提示词文件为空");
  }

  const outputPath = path.isAbsolute(options.output)
    ? options.output
    : path.resolve(process.cwd(), options.output);
  const outputDir = path.dirname(outputPath);
  const filename = path.basename(outputPath);

  const { config, credentials } = await readConfig(options.workspace);
  const size = options.size || config.size;
  const quality = options.quality || config.quality;
  const format = options.format || config.format;

  console.log(`
生图计划

渠道：GPT / ${config.imageModel}
尺寸：${size}
质量：${quality}
格式：${format}
输出：${outputPath}
`);

  const response = await fetch(getEndpoint(config.host), {
    method: "POST",
    headers: {
      Authorization: `Bearer ${credentials.apiKey}`,
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      model: config.imageModel,
      input: prompt,
      size,
      quality,
      output_format: format,
    }),
  });

  const text = await response.text();
  const payload = parseResponseText(text);

  if (!response.ok) {
    throw new Error(`Responses API 请求失败：HTTP ${response.status} ${sanitizeText(text, credentials.apiKey).slice(0, 1600)}`);
  }

  const imageCall = findImageCall(payload);
  if (!imageCall) {
    throw new Error(`Responses API 未返回 image_generation_call：${sanitizeText(text, credentials.apiKey).slice(0, 1600)}`);
  }

  const imageBytes = Buffer.from(imageCall.result, "base64");
  if (imageBytes.length === 0) {
    throw new Error("图片结果为空");
  }

  await fs.mkdir(outputDir, { recursive: true });
  await fs.writeFile(outputPath, imageBytes);

  return outputPath;
}

async function generateImage(options: GenerateOptions): Promise<string> {
  console.log(`
╔═══════════════════════════════════════════════════════╗
║   GPT 图片生成器                                      ║
╚═══════════════════════════════════════════════════════╝
`);

  let lastError: unknown;

  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const savedPath = await generateImageOnce(options);
      console.log(`
图片生成完成

文件：${savedPath}
提示词：${options.promptFile}

你可以继续：
- 调整提示词重新生成
- 换成 Gemini 渠道再试一版
- 直接使用这张图
`);
      return savedPath;
    } catch (error) {
      lastError = error;
      if (attempt >= MAX_RETRIES || !isRetryableGenerateError(error)) {
        throw error;
      }

      console.warn(`第 ${attempt + 1} 次生成失败，将在 ${RETRY_DELAY_MS / 1000} 秒后重试...`);
      await sleep(RETRY_DELAY_MS);
    }
  }

  throw lastError;
}

function printUsage(): void {
  console.error(`用法: bun scripts/generate-image.ts [选项]

选项:
  --workspace <dir>       项目根目录，用于读取 .gpt-image-gen 配置（默认当前目录）
  -p, --prompt-file <file> 提示词文件路径（必需）
  -o, --output <file>      输出图片路径（可选）
  --size <size>            图片尺寸（可选，默认配置值）
  --quality <quality>      图片质量（可选，默认配置值）
  --format <format>        输出格式（可选，默认配置值）

示例:
  bun scripts/generate-image.ts --workspace /path/to/project -p prompts/cover.md -o images/cover.png`);
}

if (import.meta.main) {
  const args = parseArgs(process.argv.slice(2));
  const promptFile = getStringArg(args, "prompt-file") || getStringArg(args, "prompt");

  if (!promptFile) {
    printUsage();
    process.exit(1);
  }

  const workspace = path.resolve(getStringArg(args, "workspace") || process.cwd());
  const output = getStringArg(args, "output") || await getDefaultImageOutputPath(promptFile);

  try {
    await generateImage({
      workspace,
      promptFile,
      output,
      size: getStringArg(args, "size"),
      quality: getStringArg(args, "quality"),
      format: getStringArg(args, "format"),
    });
  } catch (error) {
    console.error("错误:", sanitizeText(error instanceof Error ? error.message : error));
    process.exit(1);
  }
}

export { generateImage, type GenerateOptions };
