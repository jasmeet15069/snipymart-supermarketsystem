"use client";

import axios from "axios";

const configuredApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

function resolveApiBaseUrl() {
  if (typeof window !== "undefined") {
    const isLocalFrontend = ["localhost", "127.0.0.1", "::1"].includes(window.location.hostname);
    const isLocalApi =
      !configuredApiBaseUrl ||
      configuredApiBaseUrl.includes("localhost:8000") ||
      configuredApiBaseUrl.includes("127.0.0.1:8000");

    if (isLocalFrontend && isLocalApi) {
      return "http://127.0.0.1:8000/api/v1";
    }
  }

  return configuredApiBaseUrl ?? (process.env.NODE_ENV === "production" ? "/_/backend/api/v1" : "http://127.0.0.1:8000/api/v1");
}

const API_BASE_URL = resolveApiBaseUrl();

type ApiErrorPayload = {
  detail?: unknown;
};

function detailToMessage(detail: unknown): string | null {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    const messages = detail
      .map((entry) => {
        if (typeof entry === "string") return entry;
        if (entry && typeof entry === "object" && "msg" in entry && typeof entry.msg === "string") return entry.msg;
        return null;
      })
      .filter(Boolean);
    return messages.length ? messages.join(", ") : null;
  }
  return null;
}

export function apiErrorMessage(error: unknown, fallback: string) {
  if (axios.isAxiosError<ApiErrorPayload>(error)) {
    return detailToMessage(error.response?.data?.detail) ?? error.response?.statusText ?? error.message ?? fallback;
  }
  return fallback;
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000
});

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

const ACCESS_KEY = "snipymart_access";
const REFRESH_KEY = "snipymart_refresh";

export function getStoredTokens() {
  if (typeof window === "undefined") return null;
  const access = window.localStorage.getItem(ACCESS_KEY);
  const refresh = window.localStorage.getItem(REFRESH_KEY);
  if (!access || !refresh) return null;
  return { access, refresh };
}

export function storeTokens(tokens: TokenPair) {
  window.localStorage.setItem(ACCESS_KEY, tokens.access_token);
  window.localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
}

export function clearTokens() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACCESS_KEY);
  window.localStorage.removeItem(REFRESH_KEY);
}

api.interceptors.request.use((config) => {
  const tokens = getStoredTokens();
  if (tokens) {
    config.headers.Authorization = `Bearer ${tokens.access}`;
  }
  return config;
});

let refreshPromise: Promise<TokenPair> | null = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const tokens = getStoredTokens();
    if (error.response?.status === 401 && tokens?.refresh && !original?._retry) {
      original._retry = true;
      refreshPromise ??= api
        .post<TokenPair>("/auth/refresh", { refresh_token: tokens.refresh })
        .then((response) => response.data)
        .finally(() => {
          refreshPromise = null;
        });
      const newTokens = await refreshPromise;
      storeTokens(newTokens);
      original.headers.Authorization = `Bearer ${newTokens.access_token}`;
      return api(original);
    }
    return Promise.reject(error);
  }
);
