// Central Green Verse Frontend API Client

const API_BASE_URL = window.__GV_API_BASE_URL || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
  ? 'http://127.0.0.1:8000/api' 
  : '/api');

let authToken = localStorage.getItem('gv_token') || null;

export function setAuthToken(token) {
  authToken = token;
  if (token) {
    localStorage.setItem('gv_token', token);
  } else {
    localStorage.removeItem('gv_token');
  }
}

export function getAuthToken() {
  return authToken;
}

async function request(endpoint, options = {}) {
  const ep = endpoint.startsWith('/') ? endpoint : '/' + endpoint;
  const candidateUrls = [
    `${API_BASE_URL}${ep}`,
    `/api${ep}`,
    `http://127.0.0.1:8000/api${ep}`,
    `http://localhost:8000/api${ep}`
  ];
  const uniqueUrls = [...new Set(candidateUrls)];
  const timeoutMs = options.timeout || 9000;
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...(options.headers || {})
  };

  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  let lastErr = null;
  for (const url of uniqueUrls) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, {
        ...options,
        headers,
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (!response.ok) {
        let errDetail = `HTTP ${response.status} ${response.statusText}`;
        try {
          const errJson = await response.json();
          if (errJson && errJson.detail) {
            errDetail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
          }
        } catch (e) {}
        const error = new Error(errDetail);
        error.status = response.status;
        throw error;
      }

      const contentType = response.headers.get('content-type') || '';
      if (contentType.includes('application/pdf') || contentType.includes('octet-stream')) {
        return await response.blob();
      }

      return await response.json();
    } catch (err) {
      clearTimeout(timeoutId);
      lastErr = err;
      if (err.status && err.status >= 400 && err.status < 500 && err.status !== 404) {
        throw err;
      }
    }
  }
  throw lastErr || new Error('Request failed to all Green Verse API targets');
}

export async function apiGet(endpoint, options = {}) {
  return request(endpoint, { ...options, method: 'GET' });
}

export async function apiPost(endpoint, data = {}, options = {}) {
  return request(endpoint, { ...options, method: 'POST', body: JSON.stringify(data) });
}

export async function apiPut(endpoint, data = {}, options = {}) {
  return request(endpoint, { ...options, method: 'PUT', body: JSON.stringify(data) });
}

export async function apiDelete(endpoint, options = {}) {
  return request(endpoint, { ...options, method: 'DELETE' });
}

// Global window object exposure for direct browser script integration
if (typeof window !== 'undefined') {
  window.GreenVerseAPI = {
    BASE_URL: API_BASE_URL,
    get: apiGet,
    post: apiPost,
    put: apiPut,
    delete: apiDelete,
    setToken: setAuthToken,
    getToken: getAuthToken,
    isOnline: false
  };
}
