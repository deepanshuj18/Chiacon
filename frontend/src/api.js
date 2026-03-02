const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Maps any error (network, API, or unexpected) to a clean user-safe message.
 * Raw Gemini / server details are never surfaced.
 */
function toSafeError(err, fallback) {
    if (!err) return fallback;
    const msg = typeof err === 'string' ? err : err.message || '';

    // Backend already returns safe messages — pass them through if they are clean
    if (
        msg.includes('rate limit') ||
        msg.includes('temporarily unavailable') ||
        msg.includes('Unable to generate') ||
        msg.includes('structured response')
    ) {
        return msg;
    }

    // Network failure (backend not running, CORS, etc.)
    if (msg.includes('Failed to fetch') || msg.includes('NetworkError') || msg.includes('ERR_')) {
        return 'Could not reach the server. Please check your connection and try again.';
    }

    // Anything else → generic safe message
    return fallback;
}

/**
 * Generate automation use-case analysis.
 * @param {{ industry: string, problem: string, role?: string }} payload
 */
export async function generateAutomation(payload) {
    try {
        const res = await fetch(`${BASE_URL}/api/generate-automation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(toSafeError(err.detail, 'Unable to generate response. Please try again.'));
        }
        return res.json();
    } catch (err) {
        throw new Error(toSafeError(err, 'Unable to generate response. Please try again.'));
    }
}

/**
 * Generate outreach email (standalone or context-aware).
 * @param {{ company_name: string, industry: string, role: string, context_summary?: string|null }} payload
 */
export async function generateEmail(payload) {
    try {
        const res = await fetch(`${BASE_URL}/api/generate-email`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(toSafeError(err.detail, 'Unable to generate response. Please try again.'));
        }
        return res.json();
    } catch (err) {
        throw new Error(toSafeError(err, 'Unable to generate response. Please try again.'));
    }
}
