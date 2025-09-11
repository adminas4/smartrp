export type ApiResponse<T> = { data: T };

const BASE = "/api";

async function request<T>(method: "GET" | "POST", path: string, body?: unknown): Promise<ApiResponse<T>> {
  const url = path.startsWith("/") ? `${BASE}${path}` : `${BASE}/${path}`;
  const res = await fetch(url, {
    method,
    headers: { "content-type": "application/json" },
    body: method === "POST" ? JSON.stringify(body ?? {}) : undefined,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`API ${method} ${url} failed: ${res.status} ${text}`);
  }
  const data = (await res.json()) as T;
  return { data };
}

export const api = {
  get:  <T = unknown>(path: string) => request<T>("GET", path),
  post: <T = unknown>(path: string, body?: unknown) => request<T>("POST", path, body),
};
