import type { AdvisoryResponse } from "../types";

async function request<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function fetchAdvisories(refresh = false): Promise<AdvisoryResponse> {
  const params = new URLSearchParams();
  if (refresh) {
    params.set("refresh", "true");
  }
  const query = params.toString();
  const url = query ? `/api/advisories?${query}` : "/api/advisories";
  return request<AdvisoryResponse>(url);
}

export async function triggerRefresh(): Promise<AdvisoryResponse> {
  return request<AdvisoryResponse>("/api/advisories/refresh", { method: "POST" });
}

export async function downloadJson(): Promise<void> {
  const response = await fetch("/api/advisories/export");
  if (!response.ok) {
    throw new Error(`Download failed with status ${response.status}`);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "psirt_advisories.json";
  link.click();
  URL.revokeObjectURL(url);
}
