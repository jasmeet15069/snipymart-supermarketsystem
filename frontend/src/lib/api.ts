"use client";

import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

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
