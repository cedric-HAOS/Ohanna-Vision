"use strict";

/**
 * Escape a value before inserting it into generated HTML.
 *
 * @param {unknown} value
 * @returns {string}
 */
export function escapeHtml(value) {
    const element = document.createElement("div");

    element.textContent = String(value ?? "");

    return element.innerHTML;
}

/**
 * Format an ISO date using the French locale.
 *
 * @param {unknown} value
 * @returns {string}
 */
export function formatDate(value) {
    if (!value) {
        return "—";
    }

    const date = new Date(String(value));

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return new Intl.DateTimeFormat("fr-FR", {
        dateStyle: "short",
        timeStyle: "medium",
    }).format(date);
}

/**
 * Format a latency value.
 *
 * @param {unknown} value
 * @returns {string}
 */
export function formatLatency(value) {
    if (value === null || value === undefined) {
        return "—";
    }

    const latency = Number(value);

    if (!Number.isFinite(latency)) {
        return "—";
    }

    return `${latency.toFixed(2)} ms`;
}

/**
 * Return the normalized health status used by the UI.
 *
 * @param {unknown} status
 * @returns {string}
 */
export function normalizeHealthStatus(status) {
    const normalized = String(
        status ?? "unknown",
    ).toLowerCase();

    if (normalized === "unavailable") {
        return "unhealthy";
    }

    const supportedStatuses = new Set([
        "healthy",
        "degraded",
        "unhealthy",
        "unknown",
    ]);

    return supportedStatuses.has(normalized)
        ? normalized
        : "unknown";
}

/**
 * Return a human-readable health label.
 *
 * @param {unknown} status
 * @returns {string}
 */
export function healthStatusLabel(status) {
    const labels = {
        healthy: "Sain",
        degraded: "Dégradé",
        unhealthy: "Indisponible",
        unknown: "Inconnu",
    };

    const normalized =
        normalizeHealthStatus(status);

    return labels[normalized] ?? labels.unknown;
}

/**
 * Build the CSS class for a status badge.
 *
 * @param {unknown} status
 * @returns {string}
 */
export function statusClass(status) {
    return (
        "status-badge "
        + `status-badge--${normalizeHealthStatus(status)}`
    );
}

/**
 * Build the HTML representation of a status badge.
 *
 * @param {unknown} status
 * @returns {string}
 */
export function statusBadge(status) {
    const normalized =
        normalizeHealthStatus(status);

    return `
        <span class="${statusClass(normalized)}">
            ${escapeHtml(normalized)}
        </span>
    `;
}

/**
 * Return the unique non-empty values from an iterable.
 *
 * @param {Iterable<unknown>} values
 * @returns {Set<unknown>}
 */
export function uniqueValues(values) {
    return new Set(
        Array.from(values).filter((value) => {
            return (
                value !== null
                && value !== undefined
                && value !== ""
            );
        }),
    );
}

/**
 * Show an error message.
 *
 * @param {HTMLElement | null} element
 * @param {unknown} message
 */
export function showError(element, message) {
    if (!element) {
        return;
    }

    element.textContent = String(message);
    element.classList.remove("hidden");
}

/**
 * Hide an error message.
 *
 * @param {HTMLElement | null} element
 */
export function hideError(element) {
    if (!element) {
        return;
    }

    element.textContent = "";
    element.classList.add("hidden");
}