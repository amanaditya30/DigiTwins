const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://127.0.0.1:8000';

/**
 * Retrieve the active authentication token from localStorage.
 */
export const getToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('placement_twin_token');
  }
  return null;
};

/**
 * Save the authentication token to localStorage.
 */
export const setToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('placement_twin_token', token);
  }
};

/**
 * Remove the authentication token from localStorage.
 */
export const clearToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('placement_twin_token');
  }
};

/**
 * Helper to build authorization headers.
 */
const getHeaders = (isMultipart = false) => {
  const headers: Record<string, string> = {};
  if (!isMultipart) {
    headers['Content-Type'] = 'application/json';
  }
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

/**
 * Perform an authenticated GET request.
 */
export const apiGet = async (endpoint: string) => {
  const url = `${BACKEND_URL}${endpoint}`;
  const response = await fetch(url, {
    method: 'GET',
    headers: getHeaders(),
  });
  if (!response.ok) {
    throw new Error(`GET request failed: ${response.statusText}`);
  }
  return response.json();
};

/**
 * Perform an authenticated POST request.
 */
export const apiPost = async (endpoint: string, data?: any) => {
  const url = `${BACKEND_URL}${endpoint}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: getHeaders(),
    body: data ? JSON.stringify(data) : undefined,
  });
  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || `POST request failed: ${response.statusText}`);
  }
  return response.json();
};

/**
 * Perform an OAuth2 Form-urlencoded POST (used for login endpoint).
 */
export const apiLogin = async (username: string, password: string) => {
  const url = `${BACKEND_URL}/api/auth/login`;
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || 'Incorrect username or password');
  }
  return response.json();
};

/**
 * Perform an authenticated file upload POST request.
 */
export const apiPostFile = async (endpoint: string, file: File) => {
  const url = `${BACKEND_URL}${endpoint}`;
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(url, {
    method: 'POST',
    headers: getHeaders(true),
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`File upload failed: ${response.statusText}`);
  }
  return response.json();
};
