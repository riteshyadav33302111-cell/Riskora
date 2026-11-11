const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Scan a URL for phishing.
 * @param {string} url - The URL to scan
 * @returns {Promise<Object>} The scan result
 */
export async function scanUrl(url) {
  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `Server error: ${response.status}`);
  }

  return response.json();
}

/**
 * Fetch aggregate statistics from the backend.
 * @returns {Promise<Object>}
 */
export async function fetchStatistics() {
  const response = await fetch(`${API_BASE_URL}/statistics`, {
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch statistics: ${response.status}`);
  }

  return response.json();
}

/**
 * Fetch health status.
 * @returns {Promise<Object>}
 */
export async function fetchHealth() {
  const response = await fetch(`${API_BASE_URL}/health`, {
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }

  return response.json();
}
