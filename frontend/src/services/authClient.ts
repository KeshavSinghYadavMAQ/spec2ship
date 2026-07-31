import { ApiError } from "./apiClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/v1";

export type LoginRequest = {
  identifier: string;
  password: string;
};

export type LoginResponse = {
  status: string;
};

export type LogoutResponse = {
  status: string;
};

export type SessionSummary = {
  authenticated: boolean;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    credentials: "include",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail ?? body.title ?? detail;
    } catch {
      // Non-JSON response body.
    }
    throw new ApiError(response.status, detail);
  }

  return (await response.json()) as T;
}

export const authClient = {
  login: (body: LoginRequest) =>
    request<LoginResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  logout: () => request<LogoutResponse>("/auth/logout", { method: "POST" }),
  getSession: () => request<SessionSummary>("/auth/session", { method: "GET" }),
};
