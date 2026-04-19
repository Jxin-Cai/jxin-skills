import { logger } from './logger.js';

function is_rpc_payload(value: unknown): value is unknown[] {
  return Array.isArray(value)
    && value.some((part) => Array.isArray(part) && part[0] === 'wrb.fr' && typeof part[2] === 'string');
}

export function get_nested_value<T = unknown>(data: unknown, path: number[], def?: T): T {
  let cur: unknown = data;
  for (let i = 0; i < path.length; i++) {
    const k = path[i]!;
    if (!Array.isArray(cur)) {
      logger.debug(`Safe navigation: path ${JSON.stringify(path)} ended at index ${i} (key '${k}'), returning default.`);
      return def as T;
    }
    cur = cur[k];
    if (cur === undefined) {
      logger.debug(`Safe navigation: path ${JSON.stringify(path)} ended at index ${i} (key '${k}'), returning default.`);
      return def as T;
    }
  }

  if (cur == null && def !== undefined) return def as T;
  return cur as T;
}

export function extract_json_from_response(text: string): unknown {
  if (typeof text !== 'string') {
    throw new TypeError(`Input text is expected to be a string, got ${typeof text} instead.`);
  }

  const parsed: unknown[] = [];
  for (const line of text.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try {
      parsed.push(JSON.parse(trimmed) as unknown);
    } catch {}
  }

  for (let i = parsed.length - 1; i >= 0; i--) {
    const value = parsed[i];
    if (is_rpc_payload(value)) return value;
  }

  if (parsed.length === 0) {
    throw new Error('Could not find a valid JSON object or array in the response.');
  }

  return parsed[parsed.length - 1];
}

export const extractJsonFromResponse = extract_json_from_response;
export const getNestedValue = get_nested_value;
