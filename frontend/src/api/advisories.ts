import type { AdvisoryResponse } from "../types";

// 生產模式標記 - 在 GitHub Pages 等靜態環境中使用
const IS_PRODUCTION = import.meta.env.PROD || import.meta.env.MODE === 'production';

async function request<T>(input: RequestInfo, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }
  return (await response.json()) as T;
}

// 生產模式的靜態數據實現
async function fetchAdvisoriesFromStatic(): Promise<AdvisoryResponse> {
  try {
    const response = await fetch('/data/advisories.json');
    const items = await response.json();
    return { items };
  } catch (error) {
    console.error('Failed to load static data:', error);
    return { items: [] };
  }
}

async function triggerRefreshStatic(): Promise<AdvisoryResponse> {
  // 在生產模式下，模擬刷新但實際返回相同數據
  console.log('Demo mode: Refresh simulated');
  return fetchAdvisoriesFromStatic();
}

async function downloadJsonStatic(): Promise<void> {
  try {
    const response = await fetch('/data/advisories.json');
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "psirt_advisories_demo.json";
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Failed to download static data:', error);
    throw new Error('Download failed in demo mode');
  }
}

// 根據環境選擇實現
export const fetchAdvisories = IS_PRODUCTION ? fetchAdvisoriesFromStatic : async (refresh = false): Promise<AdvisoryResponse> => {
  const params = new URLSearchParams();
  if (refresh) {
    params.set("refresh", "true");
  }
  const query = params.toString();
  const url = query ? `/api/advisories?${query}` : "/api/advisories";
  return request<AdvisoryResponse>(url);
};

export const triggerRefresh = IS_PRODUCTION ? triggerRefreshStatic : (): Promise<AdvisoryResponse> => {
  return request<AdvisoryResponse>("/api/advisories/refresh", { method: "POST" });
};

export const downloadJson = IS_PRODUCTION ? downloadJsonStatic : async (): Promise<void> => {
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
};
