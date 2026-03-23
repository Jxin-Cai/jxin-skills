/**
 * Gemini Web API 客户端
 * 支持自动浏览器登录和图片生成
 * 使用 Chrome DevTools Protocol (CDP) 实现自动化登录
 */

import fs from "node:fs/promises";
import fss from "node:fs";
import path from "node:path";
import { homedir } from "node:os";
import { spawn, type ChildProcess } from "node:child_process";
import net from "node:net";

// 配置路径
const CONFIG_DIR = path.join(homedir(), ".local/share/smart-image-generator");
const COOKIE_PATH = path.join(CONFIG_DIR, "cookies.txt");
const PROFILE_DIR = path.join(CONFIG_DIR, "chrome-profile");

// Gemini API 端点和常量
const GEMINI_ENDPOINT = "https://gemini.google.com";
const GEMINI_APP_URL = "https://gemini.google.com/app";
const GENERATE_ENDPOINT =
  "https://gemini.google.com/_/BardChatUi/data/assistant.lamda.BardFrontendService/StreamGenerate";

// HTTP 请求头
const GEMINI_HEADERS = {
  "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
  Host: "gemini.google.com",
  Origin: "https://gemini.google.com",
  Referer: "https://gemini.google.com/",
  "User-Agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "X-Same-Domain": "1",
};

// Gemini 模型配置
const GEMINI_MODEL_HEADER = {
  "x-goog-ext-525001261-jspb":
    '[1,null,null,null,"9d8ca3786ebdfbea",null,null,0,[4]]',
};

export interface GeminiImage {
  url: string;
  title?: string;
  alt?: string;
  save(dir: string, filename: string, cookies?: CookieMap): Promise<string>;
}

export interface GeminiOutput {
  text: string;
  images: GeminiImage[];
  metadata?: any;
}

type CookieMap = Record<string, string>;

/**
 * CDP (Chrome DevTools Protocol) 连接
 */
class CdpConnection {
  private ws: WebSocket;
  private nextId = 0;
  private pending = new Map<
    number,
    {
      resolve: (v: unknown) => void;
      reject: (e: Error) => void;
      timer: ReturnType<typeof setTimeout> | null;
    }
  >();

  private constructor(ws: WebSocket) {
    this.ws = ws;
    this.ws.addEventListener("message", (event) => {
      try {
        const data =
          typeof event.data === "string"
            ? event.data
            : new TextDecoder().decode(event.data as ArrayBuffer);
        const msg = JSON.parse(data) as {
          id?: number;
          result?: unknown;
          error?: { message?: string };
        };
        if (msg.id) {
          const p = this.pending.get(msg.id);
          if (p) {
            this.pending.delete(msg.id);
            if (p.timer) clearTimeout(p.timer);
            if (msg.error?.message) p.reject(new Error(msg.error.message));
            else p.resolve(msg.result);
          }
        }
      } catch {}
    });
  }

  static async connect(url: string, timeoutMs: number): Promise<CdpConnection> {
    const ws = new WebSocket(url);
    await new Promise<void>((resolve, reject) => {
      const t = setTimeout(() => reject(new Error("CDP 连接超时")), timeoutMs);
      ws.addEventListener("open", () => {
        clearTimeout(t);
        resolve();
      });
      ws.addEventListener("error", () => {
        clearTimeout(t);
        reject(new Error("CDP 连接失败"));
      });
    });
    return new CdpConnection(ws);
  }

  async send<T = unknown>(
    method: string,
    params?: Record<string, unknown>,
    opts?: { sessionId?: string; timeoutMs?: number },
  ): Promise<T> {
    const id = ++this.nextId;
    const msg: Record<string, unknown> = { id, method };
    if (params) msg.params = params;
    if (opts?.sessionId) msg.sessionId = opts.sessionId;

    const timeoutMs = opts?.timeoutMs ?? 15_000;
    const out = await new Promise<unknown>((resolve, reject) => {
      const t =
        timeoutMs > 0
          ? setTimeout(() => {
              this.pending.delete(id);
              reject(new Error(`CDP 超时: ${method}`));
            }, timeoutMs)
          : null;
      this.pending.set(id, { resolve, reject, timer: t });
      this.ws.send(JSON.stringify(msg));
    });
    return out as T;
  }

  close(): void {
    try {
      this.ws.close();
    } catch {}
  }
}

/**
 * 查找 Chrome 可执行文件
 */
function findChromeExecutable(): string | null {
  const candidates: string[] = [];

  switch (process.platform) {
    case "darwin":
      candidates.push(
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
      );
      break;
    case "win32":
      candidates.push(
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
      );
      break;
    default:
      candidates.push(
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
      );
      break;
  }

  for (const p of candidates) {
    if (fss.existsSync(p)) return p;
  }
  return null;
}

/**
 * 获取空闲端口
 */
async function getFreePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const srv = net.createServer();
    srv.unref();
    srv.on("error", reject);
    srv.listen(0, "127.0.0.1", () => {
      const addr = srv.address();
      if (!addr || typeof addr === "string") {
        srv.close(() => reject(new Error("无法分配空闲端口")));
        return;
      }
      const port = addr.port;
      srv.close((err) => (err ? reject(err) : resolve(port)));
    });
  });
}

/**
 * 等待 Chrome 调试端口就绪
 */
async function waitForChromeDebugPort(
  port: number,
  timeoutMs: number,
): Promise<string> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/version`, {
        signal: AbortSignal.timeout(5000),
      });
      if (res.ok) {
        const j = (await res.json()) as { webSocketDebuggerUrl?: string };
        if (j.webSocketDebuggerUrl) return j.webSocketDebuggerUrl;
      }
    } catch {}
    await new Promise((r) => setTimeout(r, 200));
  }
  throw new Error("Chrome 调试端口未就绪");
}

/**
 * 启动 Chrome 浏览器
 */
async function launchChrome(
  profileDir: string,
  port: number,
): Promise<ChildProcess> {
  const chrome = findChromeExecutable();
  if (!chrome) {
    throw new Error("未找到 Chrome 浏览器。请安装 Google Chrome。");
  }

  const args = [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${profileDir}`,
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-popup-blocking",
    GEMINI_APP_URL,
  ];

  console.log(`🌐 正在打开 Chrome 浏览器...`);
  return spawn(chrome, args, { stdio: "ignore" });
}

/**
 * 检查 Gemini 会话是否就绪
 */
async function isGeminiSessionReady(cookies: CookieMap): Promise<boolean> {
  if (!cookies["__Secure-1PSID"]) return false;

  try {
    const cookieStr = Object.entries(cookies)
      .map(([k, v]) => `${k}=${v}`)
      .join("; ");

    const res = await fetch(`${GEMINI_ENDPOINT}/app`, {
      headers: {
        Cookie: cookieStr,
        "User-Agent":
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
      },
      signal: AbortSignal.timeout(30000),
    });

    if (!res.ok) return false;

    const text = await res.text();
    return /"SNlM0e":"([^"]+)"/.test(text);
  } catch {
    return false;
  }
}

/**
 * 通过浏览器获取 Cookies
 */
async function fetchCookiesViaBrowser(timeoutMs: number): Promise<CookieMap> {
  await fs.mkdir(PROFILE_DIR, { recursive: true });

  const port = await getFreePort();
  const chrome = await launchChrome(PROFILE_DIR, port);

  let cdp: CdpConnection | null = null;
  try {
    const wsUrl = await waitForChromeDebugPort(port, 30_000);
    cdp = await CdpConnection.connect(wsUrl, 15_000);

    const { targetId } = await cdp.send<{ targetId: string }>(
      "Target.createTarget",
      {
        url: GEMINI_APP_URL,
        newWindow: true,
      },
    );
    const { sessionId } = await cdp.send<{ sessionId: string }>(
      "Target.attachToTarget",
      {
        targetId,
        flatten: true,
      },
    );
    await cdp.send("Network.enable", {}, { sessionId });

    console.log(`
╔═══════════════════════════════════════════════════════╗
║   请在打开的浏览器中登录 Google 账号                  ║
╚═══════════════════════════════════════════════════════╝

⏳ 等待登录... (最多 ${Math.floor(timeoutMs / 1000)} 秒)
`);

    const start = Date.now();
    let last: CookieMap = {};

    while (Date.now() - start < timeoutMs) {
      const { cookies } = await cdp.send<{
        cookies: Array<{ name: string; value: string }>;
      }>(
        "Network.getCookies",
        {
          urls: [
            GEMINI_ENDPOINT,
            "https://accounts.google.com/",
            "https://www.google.com/",
          ],
        },
        { sessionId, timeoutMs: 10_000 },
      );

      const m: CookieMap = {};
      for (const c of cookies) {
        if (c?.name && typeof c.value === "string") m[c.name] = c.value;
      }

      last = m;
      if (await isGeminiSessionReady(m)) {
        console.log("✅ 登录成功！");
        return m;
      }

      await new Promise((r) => setTimeout(r, 1000));
    }

    throw new Error(`登录超时。请确保已登录 Google 账号。`);
  } finally {
    if (cdp) {
      try {
        await cdp.send("Browser.close", {}, { timeoutMs: 5_000 });
      } catch {}
      cdp.close();
    }

    try {
      chrome.kill("SIGTERM");
    } catch {}
    setTimeout(() => {
      if (!chrome.killed) {
        try {
          chrome.kill("SIGKILL");
        } catch {}
      }
    }, 2_000);
  }
}

/**
 * 读取 Cookie 文件
 */
async function readCookieFile(): Promise<CookieMap | null> {
  try {
    const content = await fs.readFile(COOKIE_PATH, "utf-8");
    const cookies: CookieMap = {};

    for (const line of content.split("\n")) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;

      const parts = trimmed.split("\t");
      if (parts.length >= 7) {
        const name = parts[5];
        const value = parts[6];
        if (name && value) {
          cookies[name] = value;
        }
      }
    }

    return Object.keys(cookies).length > 0 ? cookies : null;
  } catch {
    return null;
  }
}

/**
 * 保存 Cookie 文件
 */
async function writeCookieFile(cookies: CookieMap): Promise<void> {
  await fs.mkdir(CONFIG_DIR, { recursive: true });

  const lines = [
    "# Netscape HTTP Cookie File",
    "# Generated by smart-image-generator",
    "",
  ];
  const expires = Math.floor(Date.now() / 1000) + 365 * 24 * 3600;

  for (const [name, value] of Object.entries(cookies)) {
    lines.push(
      `.gemini.google.com\tTRUE\t/\tTRUE\t${expires}\t${name}\t${value}`,
    );
  }

  await fs.writeFile(COOKIE_PATH, lines.join("\n"), "utf-8");
  await fs.chmod(COOKIE_PATH, 0o600);
}

/**
 * 从响应中提取 JSON
 */
function extractJsonFromResponse(text: string): unknown {
  let last: unknown = undefined;
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try {
      last = JSON.parse(trimmed) as unknown;
    } catch {}
  }

  if (last === undefined) {
    throw new Error("响应中未找到有效的 JSON");
  }

  return last;
}

/**
 * 获取嵌套值
 */
function getNestedValue<T = unknown>(
  data: unknown,
  path: number[],
  def?: T,
): T {
  let cur: unknown = data;
  for (const k of path) {
    if (!Array.isArray(cur)) return def as T;
    cur = cur[k];
    if (cur === undefined) return def as T;
  }
  if (cur == null && def !== undefined) return def as T;
  return cur as T;
}

/**
 * 收集字符串
 */
function collectStrings(
  root: unknown,
  accept: (s: string) => boolean,
  limit: number = 20,
): string[] {
  const out: string[] = [];
  const seen = new Set<string>();
  const stack: unknown[] = [root];

  while (stack.length > 0 && out.length < limit) {
    const v = stack.pop();
    if (typeof v === "string") {
      if (accept(v) && !seen.has(v)) {
        seen.add(v);
        out.push(v);
      }
      continue;
    }

    if (Array.isArray(v)) {
      for (const item of v) stack.push(item);
      continue;
    }

    if (v && typeof v === "object") {
      for (const val of Object.values(v as Record<string, unknown>))
        stack.push(val);
    }
  }

  return out;
}

/**
 * 获取 Access Token
 */
async function getAccessToken(cookies: CookieMap): Promise<string> {
  const cookieStr = Object.entries(cookies)
    .map(([k, v]) => `${k}=${v}`)
    .join("; ");

  const res = await fetch(GEMINI_APP_URL, {
    headers: {
      Cookie: cookieStr,
      "User-Agent": GEMINI_HEADERS["User-Agent"],
    },
    signal: AbortSignal.timeout(30000),
  });

  if (!res.ok) {
    throw new Error(`获取 Access Token 失败: ${res.status}`);
  }

  const text = await res.text();
  const match = text.match(/"SNlM0e":"([^"]+)"/);

  if (!match) {
    throw new Error("未找到 Access Token");
  }

  return match[1];
}

/**
 * Gemini Web API 客户端
 */
export class GeminiClient {
  private cookies: CookieMap = {};
  private accessToken: string | null = null;

  /**
   * 初始化客户端，自动处理登录
   * @param maxRetries 最大重试次数（建议设为1，避免重复打开浏览器）
   */
  async init(maxRetries: number = 1): Promise<void> {
    console.log("🔌 初始化 Gemini 客户端...");

    // 1. 尝试读取已保存的 cookies
    let cookies = await readCookieFile();

    // 2. 检查 cookies 是否有效
    if (cookies && (await isGeminiSessionReady(cookies))) {
      console.log("✓ 使用已保存的登录状态");
      this.cookies = cookies;
      await this.refreshAccessToken();
      return;
    }

    // 3. 需要重新登录
    console.log("⚠️  需要登录 Gemini");

    let retries = 0;
    while (retries < maxRetries) {
      try {
        // 打开浏览器获取 cookies（5分钟超时，给用户足够时间登录）
        cookies = await fetchCookiesViaBrowser(300_000);

        // 验证并保存
        if (await isGeminiSessionReady(cookies)) {
          await writeCookieFile(cookies);
          this.cookies = cookies;
          await this.refreshAccessToken();
          console.log("✅ 登录成功并已保存");
          return;
        }
      } catch (err) {
        console.error(
          `❌ 登录失败 (尝试 ${retries + 1}/${maxRetries}): ${err}`,
        );
      }

      retries++;
      if (retries < maxRetries) {
        console.log(`⏳ 5 秒后重试...`);
        await new Promise((r) => setTimeout(r, 5000));
      }
    }

    throw new Error(
      `登录失败，已重试 ${maxRetries} 次。请检查网络或稍后再试。`,
    );
  }

  /**
   * 生成图片
   */
  async generateImage(prompt: string): Promise<GeminiOutput> {
    console.log("🎨 正在生成图片...");
    console.log(`📝 提示词长度: ${prompt.length} 字符`);

    if (!this.accessToken) {
      throw new Error("未初始化 Access Token");
    }

    // 构建请求
    const inner = [[prompt], null, null];
    const fReq = JSON.stringify([null, JSON.stringify(inner)]);
    const body = new URLSearchParams({
      at: this.accessToken,
      "f.req": fReq,
    }).toString();

    // ✅ 明确使用UTF-8编码转换为Uint8Array，避免中文乱码
    const bodyBytes = new TextEncoder().encode(body);

    const cookieStr = Object.entries(this.cookies)
      .map(([k, v]) => `${k}=${v}`)
      .join("; ");

    const headers = {
      ...GEMINI_HEADERS,
      ...GEMINI_MODEL_HEADER,
      Cookie: cookieStr,
    };

    // 发送请求（使用UTF-8编码的字节流）
    const res = await fetch(GENERATE_ENDPOINT, {
      method: "POST",
      headers,
      body: bodyBytes,  // ✅ 使用UTF-8编码的字节流
      signal: AbortSignal.timeout(300000), // 5 分钟超时
    });

    if (!res.ok) {
      throw new Error(`生成失败: ${res.status} ${res.statusText}`);
    }

    // 解析响应
    const text = await res.text();
    const responseJson = extractJsonFromResponse(text) as unknown[];

    // 查找包含图片的响应体
    let bodyJson: unknown[] | null = null;
    let bodyIndex = 0;

    for (let partIndex = 0; partIndex < responseJson.length; partIndex++) {
      const part = responseJson[partIndex];
      if (!Array.isArray(part)) continue;

      const partBody = getNestedValue<string | null>(part, [2], null);
      if (!partBody) continue;

      try {
        const partJson = JSON.parse(partBody) as unknown[];
        if (getNestedValue(partJson, [4], null)) {
          bodyIndex = partIndex;
          bodyJson = partJson;
          break;
        }
      } catch {}
    }

    if (!bodyJson) {
      throw new Error("响应中未找到有效数据");
    }

    // 提取候选结果
    const candidateList = getNestedValue<unknown[]>(bodyJson, [4], []);
    if (candidateList.length === 0) {
      throw new Error("未生成任何内容");
    }

    const candidate = candidateList[0];
    if (!Array.isArray(candidate)) {
      throw new Error("候选结果格式错误");
    }

    // 提取文本
    let text_result = String(getNestedValue(candidate, [1, 0], ""));

    // 提取生成的图片
    const generatedImages: GeminiImage[] = [];
    const wantsGenerated =
      getNestedValue(candidate, [12, 7, 0], null) != null ||
      /http:\/\/googleusercontent\.com\/image_generation_content\/\d+/.test(
        text_result,
      );

    if (wantsGenerated) {
      // 查找图片数据
      let imgBody: unknown[] | null = null;
      for (
        let partIndex = bodyIndex;
        partIndex < responseJson.length;
        partIndex++
      ) {
        const part = responseJson[partIndex];
        if (!Array.isArray(part)) continue;

        const partBody = getNestedValue<string | null>(part, [2], null);
        if (!partBody) continue;

        try {
          const partJson = JSON.parse(partBody) as unknown[];
          const cand = getNestedValue<unknown>(partJson, [4, 0], null);
          if (!cand) continue;

          const urls = collectStrings(
            cand,
            (s) => s.startsWith("https://lh3.googleusercontent.com/gg-dl/"),
            1,
          );
          if (urls.length > 0) {
            imgBody = partJson;
            break;
          }
        } catch {}
      }

      if (!imgBody) {
        throw new Error("未找到生成的图片");
      }

      const imgCandidate = getNestedValue<unknown[]>(imgBody, [4, 0], []);
      const finished = getNestedValue<string | null>(
        imgCandidate,
        [1, 0],
        null,
      );
      if (finished) {
        text_result = finished
          .replace(
            /http:\/\/googleusercontent\.com\/image_generation_content\/\d+/g,
            "",
          )
          .trimEnd();
      }

      const gen = getNestedValue<unknown[]>(imgCandidate, [12, 7, 0], []);
      for (let imgIndex = 0; imgIndex < gen.length; imgIndex++) {
        const g = gen[imgIndex];
        if (!Array.isArray(g)) continue;

        const url = getNestedValue<string | null>(g, [0, 3, 3], null);
        if (!url) continue;

        const imgNum = getNestedValue<number | null>(g, [3, 6], null);
        const title = imgNum ? `生成的图片 ${imgNum}` : "生成的图片";
        const altList = getNestedValue<unknown[]>(g, [3, 5], []);
        const alt =
          typeof altList[imgIndex] === "string"
            ? (altList[imgIndex] as string)
            : typeof altList[0] === "string"
              ? (altList[0] as string)
              : "";

        const cookies = this.cookies;
        generatedImages.push({
          url,
          title,
          alt,
          save: async (
            dir: string,
            filename: string,
            cookieMap?: CookieMap,
          ) => {
            // 生成的图片需要加上 =s2048 后缀获取全尺寸
            const fullUrl = `${url}=s2048`;
            return await downloadImage(
              fullUrl,
              dir,
              filename,
              cookieMap || cookies,
            );
          },
        });
      }

      // 如果没有找到图片，尝试直接搜索 URL
      if (generatedImages.length === 0) {
        const urls = collectStrings(
          imgCandidate,
          (s) => s.startsWith("https://lh3.googleusercontent.com/gg-dl/"),
          4,
        );
        for (const url of urls) {
          const cookies = this.cookies;
          generatedImages.push({
            url,
            title: "生成的图片",
            alt: "",
            save: async (
              dir: string,
              filename: string,
              cookieMap?: CookieMap,
            ) => {
              const fullUrl = `${url}=s2048`;
              return await downloadImage(
                fullUrl,
                dir,
                filename,
                cookieMap || cookies,
              );
            },
          });
        }
      }
    }

    if (generatedImages.length === 0) {
      throw new Error("未找到生成的图片");
    }

    console.log(`✅ 成功生成 ${generatedImages.length} 张图片`);

    return {
      text: text_result,
      images: generatedImages,
      metadata: {
        model: "gemini-pro",
        timestamp: new Date().toISOString(),
      },
    };
  }

  /**
   * 刷新 access token
   */
  private async refreshAccessToken(): Promise<void> {
    try {
      this.accessToken = await getAccessToken(this.cookies);
      console.log("✓ Access Token 已刷新");
    } catch (err) {
      throw new Error(`刷新 Access Token 失败: ${err}`);
    }
  }

  /**
   * 关闭客户端
   */
  async close(): Promise<void> {
    this.accessToken = null;
  }

  /**
   * 获取 cookies（供图片下载使用）
   */
  getCookies(): CookieMap {
    return this.cookies;
  }
}

/**
 * 下载图片
 */
async function downloadImage(
  url: string,
  dir: string,
  filename: string,
  cookies: CookieMap,
): Promise<string> {
  const headers: Record<string, string> = {
    "User-Agent":
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    Accept: "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    Referer: "https://gemini.google.com/",
  };

  // 添加 cookies
  if (cookies && Object.keys(cookies).length > 0) {
    headers["Cookie"] = Object.entries(cookies)
      .map(([k, v]) => `${k}=${v}`)
      .join("; ");
  }

  // 处理重定向（最多 10 次）
  let currentUrl = url;
  let response: Response | null = null;

  for (let i = 0; i < 10; i++) {
    response = await fetch(currentUrl, {
      method: "GET",
      headers,
      redirect: "manual",
      signal: AbortSignal.timeout(30000),
    });

    // 处理重定向
    if (response.status >= 300 && response.status < 400) {
      const location = response.headers.get("location");
      if (!location) break;
      currentUrl = new URL(location, currentUrl).toString();
      continue;
    }

    break;
  }

  if (!response) {
    throw new Error("图片下载失败：无响应");
  }

  if (!response.ok) {
    throw new Error(`图片下载失败: ${response.status} ${response.statusText}`);
  }

  // 检查 Content-Type
  const contentType = response.headers.get("content-type");
  if (contentType && !contentType.includes("image")) {
    console.warn(`⚠️  Content-Type 不是图片类型: ${contentType}`);
  }

  // 下载图片数据
  const arrayBuffer = await response.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);

  // 确保目录存在
  await fs.mkdir(dir, { recursive: true });

  // 保存图片
  const fullPath = path.join(dir, filename);
  await fs.writeFile(fullPath, buffer);

  console.log(
    `✅ 图片已保存: ${fullPath} (${(buffer.length / 1024).toFixed(2)} KB)`,
  );

  return fullPath;
}
