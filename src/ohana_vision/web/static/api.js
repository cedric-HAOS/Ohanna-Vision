"use strict";

export const API = Object.freeze({
    runtime: "/api/runtime",
    observations: "/api/observations",
    timeline: "/api/timeline",
    topology: "/api/topology",
});

/**
 * Fetch a JSON document from the Ohana-Vision backend.
 *
 * @param {string} url
 * @returns {Promise<unknown>}
 */
export async function fetchJson(url) {
    const response = await fetch(url, {
        headers: {
            Accept: "application/json",
        },
    });

    if (!response.ok) {
        let detail =
            `${response.status} ${response.statusText}`;

        try {
            const payload = await response.json();

            if (
                payload
                && typeof payload === "object"
                && "detail" in payload
                && payload.detail
            ) {
                detail = String(payload.detail);
            }
        } catch {
            // Keep the generic HTTP error message.
        }

        throw new Error(detail);
    }

    return response.json();
}