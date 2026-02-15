const API_BASE = "/api";

// ---------------------------------------------------------------------------
// Token helpers
// ---------------------------------------------------------------------------
let authToken: string | null = null;

export function setAuthToken(token: string | null) {
  authToken = token;
}

export function getAuthToken() {
  return authToken;
}

// ---------------------------------------------------------------------------
// Generic request helper
// ---------------------------------------------------------------------------
export class ApiError extends Error {
  public status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: "Request failed" }));
    throw new ApiError(response.status, body.detail || "Request failed");
  }

  return response.json();
}

// ---------------------------------------------------------------------------
// User / Auth types
// ---------------------------------------------------------------------------
export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
  profile?: string;
}

export interface UserResponse {
  id: string;
  full_name: string;
  email: string;
  profile: string | null;
  is_active: boolean;
  last_login: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  user: UserResponse;
}

// ---------------------------------------------------------------------------
// User / Auth API calls
// ---------------------------------------------------------------------------
export function register(data: RegisterRequest): Promise<UserResponse> {
  return request("/users/", { method: "POST", body: JSON.stringify(data) });
}

export function login(data: LoginRequest): Promise<LoginResponse> {
  return request("/users/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// ---------------------------------------------------------------------------
// Chat types
// ---------------------------------------------------------------------------
export interface ChatInteractionRequest {
  session_id: string;
  message: string;
}

export interface ChatInteractionResponse {
  session_id: string;
  order: number | null;
  question: string | null;
  options: string[] | null;
  question_type: string | null;
  completed: boolean;
}

export interface ChatHistoryItem {
  question: string;
  answer: string;
  order: number;
  question_type?: string | null;
  options?: string[] | null;
}

export interface ChatHistoryResponse {
  session_id: string;
  title: string;
  status: string;
  history: ChatHistoryItem[];
}

// ---------------------------------------------------------------------------
// Chat API calls
// ---------------------------------------------------------------------------
export function chatInteraction(
  data: ChatInteractionRequest,
): Promise<ChatInteractionResponse> {
  return request("/chats/", { method: "POST", body: JSON.stringify(data) });
}

export function getChatHistory(
  sessionId: string,
): Promise<ChatHistoryResponse> {
  return request(`/chats/${sessionId}/history`);
}
