import { API_BASE_URL } from "../api";

export async function localJsonRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const endpoint = new URL(path, API_BASE_URL).toString();
  const response = await fetch(endpoint, {
    ...options,
    headers: {
      Accept: "application/json",
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers
    },
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Local request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
