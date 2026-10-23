export const API_BASE = import.meta.env.VITE_API_URL || "";

export function getPosterUrl(url) {
  if (!url) return "";
  if (url.startsWith("http://") || url.startsWith("https://") || url.startsWith("data:")) return url;
  return `${API_BASE}${url.startsWith("/") ? "" : "/"}${url}`;
}

export async function fetchGames({ page = 1, pageSize = 24, search = "", category = "", sort = "latest" } = {}) {
  const qs = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  if (search) qs.set("search", search);
  if (category) qs.set("category", category);
  if (sort) qs.set("sort", sort);
  const res = await fetch(`${API_BASE}/games?${qs}`, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchGame(id) {
  const res = await fetch(`${API_BASE}/games/${id}`, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchCategories() {
  try {
    const res = await fetch(`${API_BASE}/games/categories`);
    if (!res.ok) return [];
    return await res.json();
  } catch (e) {
    return [];
  }
}

export async function fetchRandomGame() {
  const res = await fetch(`${API_BASE}/games/random`);
  if (!res.ok) throw new Error("No random game available");
  return res.json();
}

export function downloadUrl(id, fileId) {
  const base = API_BASE || window.location.origin;
  const url = new URL(`${base}/download/${id}`, window.location.origin);
  if (fileId !== undefined && fileId !== null) {
    url.searchParams.set("file_id", String(fileId));
  }
  return url.toString();
}