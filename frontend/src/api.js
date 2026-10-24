export const API_BASE = (
  import.meta.env.VITE_API_URL ||
  (typeof window !== "undefined" && window.localStorage?.getItem("VITE_API_URL")) ||
  ""
).replace(/\/+$/, "");

export function getPosterUrl(url) {
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("data:")) return url;
  return `${API_BASE}${url.startsWith("/") ? "" : "/"}${url}`;
}

async function parseJsonResponse(res) {
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const contentType = res.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    const text = await res.text();
    if (text.trim().startsWith("<!DOCTYPE") || text.trim().startsWith("<html")) {
      throw new Error(
        "Backend unreachable (received HTML instead of JSON). Please set VITE_API_URL in your Vercel Environment Variables to your Render backend URL (e.g., https://your-backend.onrender.com) and Redeploy."
      );
    }
    throw new Error(`Expected JSON but received: ${text.slice(0, 100)}`);
  }
  return res.json();
}

export async function fetchGames({ page = 1, pageSize = 24, search = "", category = "", sort = "latest" } = {}) {
  const qs = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (search) qs.set("search", search);
  if (category) qs.set("category", category);
  if (sort) qs.set("sort", sort);
  const res = await fetch(`${API_BASE}/games?${qs}`, {
    headers: { Accept: "application/json" },
  });
  return parseJsonResponse(res);
}

export async function fetchGame(id) {
  const res = await fetch(`${API_BASE}/games/${id}`, {
    headers: { Accept: "application/json" },
  });
  return parseJsonResponse(res);
}

export async function fetchCategories() {
  try {
    const res = await fetch(`${API_BASE}/games/categories`, {
      headers: { Accept: "application/json" },
    });
    return await parseJsonResponse(res);
  } catch (e) {
    return [];
  }
}

export async function fetchRandomGame() {
  const res = await fetch(`${API_BASE}/games/random`, {
    headers: { Accept: "application/json" },
  });
  return parseJsonResponse(res);
}

export function downloadUrl(id, fileId) {
  const base = API_BASE || window.location.origin;
  const url = new URL(`${base}/download/${id}`, window.location.origin);
  if (fileId !== undefined && fileId !== null) {
    url.searchParams.set("file_id", String(fileId));
  }
  return url.toString();
}