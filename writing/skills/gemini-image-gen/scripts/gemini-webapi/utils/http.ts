import { execFile } from 'node:child_process';

export function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve) => {
    const t = setTimeout(() => {
      if (signal) signal.removeEventListener('abort', onAbort);
      resolve();
    }, ms);

    const onAbort = () => {
      clearTimeout(t);
      if (signal) signal.removeEventListener('abort', onAbort);
      resolve();
    };

    if (signal) {
      if (signal.aborted) {
        onAbort();
      } else {
        signal.addEventListener('abort', onAbort, { once: true });
      }
    }
  });
}

export function cookie_header(cookies: Record<string, string>): string {
  return Object.entries(cookies)
    .filter(([, v]) => typeof v === 'string' && v.length > 0)
    .map(([k, v]) => `${k}=${v}`)
    .join('; ');
}

export const cookieHeader = cookie_header;

export function extract_set_cookie_value(setCookie: string | null, name: string): string | null {
  if (!setCookie) return null;
  const re = new RegExp(`(?:^|[;,\\s])${name.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&')}=([^;]+)`, 'i');
  const m = setCookie.match(re);
  if (!m) return null;
  return m[1] ?? null;
}

type SimpleHeaders = {
  get(name: string): string | null;
};

type PythonResponsePayload = {
  body_b64: string;
  headers: Record<string, string>;
  reason: string;
  status: number;
  url: string;
};

class SimpleResponse {
  public status: number;
  public statusText: string;
  public url: string;
  public headers: SimpleHeaders;

  private body: Buffer;

  constructor(payload: PythonResponsePayload) {
    this.status = payload.status;
    this.statusText = payload.reason;
    this.url = payload.url;
    this.body = Buffer.from(payload.body_b64, 'base64');

    const normalized = new Map<string, string>();
    for (const [key, value] of Object.entries(payload.headers ?? {})) {
      normalized.set(key.toLowerCase(), value);
    }

    this.headers = {
      get(name: string): string | null {
        return normalized.get(name.toLowerCase()) ?? null;
      },
    };
  }

  get ok(): boolean {
    return this.status >= 200 && this.status < 300;
  }

  async text(): Promise<string> {
    return this.body.toString('utf8');
  }

  async arrayBuffer(): Promise<ArrayBuffer> {
    return this.body.buffer.slice(this.body.byteOffset, this.body.byteOffset + this.body.byteLength) as ArrayBuffer;
  }
}

function should_force_python(url: string, init: RequestInit & { timeout_ms?: number }): boolean {
  if (!/^https:\/\//i.test(url)) return false;
  if (/googleusercontent\.com|usercontent\.google\.com/i.test(url)) return true;
  return init.method === 'POST' && /gemini\.google\.com\/_\/BardChatUi\/data\//i.test(url);
}

function should_fallback_to_python(url: string, error: unknown): boolean {
  if (!/^https:\/\//i.test(url)) return false;

  const message = error instanceof Error ? error.message : String(error);
  return /(ECONNREFUSED|Connect Timeout Error|fetch failed|Unable to connect|ConnectionRefused|AbortError|The operation was aborted)/i.test(message);
}

async function python_fetch(
  url: string,
  init: RequestInit & { timeout_ms?: number } = {},
): Promise<SimpleResponse> {
  const headers = new Headers(init.headers ?? {});
  const bodyText = typeof init.body === 'string' ? init.body : null;
  const payload = JSON.stringify({
    body_b64: bodyText ? Buffer.from(bodyText, 'utf8').toString('base64') : null,
    headers: Object.fromEntries(headers.entries()),
    method: init.method ?? 'GET',
    redirect: init.redirect ?? 'follow',
    timeout_ms: init.timeout_ms ?? 0,
    url,
  });

  const script = String.raw`
import base64
import json
import sys
import urllib.error
import urllib.request

payload = json.loads(sys.stdin.read())
method = payload.get("method") or "GET"
headers = payload.get("headers") or {}
body_b64 = payload.get("body_b64")
data = base64.b64decode(body_b64) if body_b64 else None
redirect = payload.get("redirect") or "follow"
timeout = payload.get("timeout_ms") or 0
if timeout and timeout > 0:
    timeout = timeout / 1000
else:
    timeout = None

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

opener = urllib.request.build_opener(NoRedirectHandler()) if redirect == "manual" else urllib.request.build_opener()
req = urllib.request.Request(payload["url"], data=data, headers=headers, method=method)

try:
    with opener.open(req, timeout=timeout) as resp:
        body = resp.read()
        out = {
            "body_b64": base64.b64encode(body).decode("ascii"),
            "headers": dict(resp.headers.items()),
            "reason": getattr(resp, "reason", "") or "",
            "status": getattr(resp, "status", 200),
            "url": resp.geturl(),
        }
except urllib.error.HTTPError as resp:
    body = resp.read()
    out = {
        "body_b64": base64.b64encode(body).decode("ascii"),
        "headers": dict(resp.headers.items()),
        "reason": getattr(resp, "reason", "") or "",
        "status": getattr(resp, "code", 500),
        "url": resp.geturl(),
    }
except Exception as e:
    print(json.dumps({"error": f"{type(e).__name__}: {e}"}))
    sys.exit(1)

print(json.dumps(out))
`;

  const result = await new Promise<Buffer>((resolve, reject) => {
    const child = execFile(
      'python3',
      ['-c', script],
      { encoding: 'buffer', maxBuffer: 100 * 1024 * 1024, timeout: init.timeout_ms ?? 0 },
      (error, stdout, stderr) => {
        if (error) {
          const msg = stderr.length > 0 ? stderr.toString('utf8') : error.message;
          reject(new Error(msg.trim() || error.message));
          return;
        }
        resolve(stdout);
      },
    );
    child.stdin?.end(payload);
  });

  const parsed = JSON.parse(result.toString('utf8')) as PythonResponsePayload | { error: string };
  if ('error' in parsed) throw new Error(parsed.error);
  return new SimpleResponse(parsed);
}

export async function fetch_with_timeout(
  url: string,
  init: RequestInit & { timeout_ms?: number } = {},
): Promise<Response> {
  if (should_force_python(url, init)) {
    return await python_fetch(url, init) as unknown as Response;
  }

  const { timeout_ms, ...rest } = init;

  try {
    if (!timeout_ms || timeout_ms <= 0) return await fetch(url, rest);

    const ctl = new AbortController();
    const t = setTimeout(() => ctl.abort(), timeout_ms);
    try {
      return await fetch(url, { ...rest, signal: ctl.signal });
    } finally {
      clearTimeout(t);
    }
  } catch (error) {
    if (!should_fallback_to_python(url, error)) throw error;
    return await python_fetch(url, init) as unknown as Response;
  }
}

export const fetchWithTimeout = fetch_with_timeout;
