"use strict";

import {
    escapeHtml,
    formatDate,
    formatLatency,
    healthStatusLabel,
    hideError,
    normalizeHealthStatus,
    showError,
    statusBadge,
} from "./utils.js";

const MAX_OBSERVATIONS = 50;

/**
 * Manage the observations displayed by the frontend.
 */
export class ObservationsController {
    constructor({
        state,
        onObservationsChanged = () => {},
        onDashboardRefresh = () => {},
    }) {
        if (!state) {
            throw new Error(
                "ObservationsController requires application state.",
            );
        }

        this.state = state;
        this.onObservationsChanged =
            onObservationsChanged;
        this.onDashboardRefresh =
            onDashboardRefresh;

        this.elements = {
            error: document.querySelector(
                "#observations-error",
            ),
            body: document.querySelector(
                "#observations-body",
            ),
            count: document.querySelector(
                "#observation-count",
            ),
            recentList: document.querySelector(
                "#recent-observations-list",
            ),
        };
    }

    /**
     * Render observations and update the shared state.
     *
     * @param {Array<object>} observations
     */
    render(observations) {
        const normalizedObservations =
            Array.isArray(observations)
                ? observations
                : [];

        this.state.observations =
            normalizedObservations;

        this.renderRecent(normalizedObservations);
        this.renderTable(normalizedObservations);

        hideError(this.elements.error);

        this.onObservationsChanged(
            normalizedObservations,
        );

        this.onDashboardRefresh();
    }

    /**
     * Display an observations loading error.
     *
     * @param {unknown} message
     */
    showError(message) {
        showError(
            this.elements.error,
            message,
        );
    }

    /**
     * Render the latest observations card.
     *
     * @param {Array<object>} observations
     */
    renderRecent(observations) {
        if (!this.elements.recentList) {
            return;
        }

        const recent = observations
            .slice()
            .sort((first, second) => {
                return (
                    new Date(
                        second.observed_at,
                    ).getTime()
                    - new Date(
                        first.observed_at,
                    ).getTime()
                );
            })
            .slice(0, 6);

        if (recent.length === 0) {
            this.elements.recentList.innerHTML = `
                <p class="side-panel-placeholder">
                    Aucune observation reçue.
                </p>
            `;
            return;
        }

        this.elements.recentList.innerHTML = recent
            .map((observation) => {
                return this.renderRecentItem(
                    observation,
                );
            })
            .join("");
    }

    /**
     * Render one recent observation.
     *
     * @param {object} observation
     * @returns {string}
     */
    renderRecentItem(observation) {
        const status =
            normalizeHealthStatus(
                observation.status,
            );

        return `
            <article
                class="recent-observation
                    recent-observation--${escapeHtml(status)}"
            >
                <span
                    class="recent-observation__indicator"
                    aria-hidden="true"
                ></span>

                <div class="recent-observation__content">
                    <strong>
                        ${escapeHtml(
                            observation.capability_id,
                        )}
                    </strong>

                    <span>
                        ${escapeHtml(
                            observation.node_id,
                        )}
                        ·
                        ${escapeHtml(
                            observation.service_id,
                        )}
                    </span>
                </div>

                <div class="recent-observation__meta">
                    <span>
                        ${escapeHtml(
                            healthStatusLabel(status),
                        )}
                    </span>

                    <time
                        datetime="${escapeHtml(
                            observation.observed_at,
                        )}"
                    >
                        ${escapeHtml(
                            formatDate(
                                observation.observed_at,
                            ),
                        )}
                    </time>
                </div>
            </article>
        `;
    }

    /**
     * Render the observations table.
     *
     * @param {Array<object>} observations
     */
    renderTable(observations) {
        const visibleObservations = observations
            .slice()
            .sort((first, second) => {
                return (
                    new Date(
                        second.observed_at,
                    ).getTime()
                    - new Date(
                        first.observed_at,
                    ).getTime()
                );
            })
            .slice(0, MAX_OBSERVATIONS);

        this.renderCount(
            visibleObservations.length,
            observations.length,
        );

        if (!this.elements.body) {
            return;
        }

        if (visibleObservations.length === 0) {
            this.elements.body.innerHTML = `
                <tr>
                    <td
                        class="empty-table"
                        colspan="6"
                    >
                        Aucune observation enregistrée.
                    </td>
                </tr>
            `;
            return;
        }

        this.elements.body.innerHTML =
            visibleObservations
                .map((observation) => {
                    return this.renderTableRow(
                        observation,
                    );
                })
                .join("");
    }

    /**
     * Render the observations count.
     *
     * @param {number} visibleCount
     * @param {number} totalCount
     */
    renderCount(visibleCount, totalCount) {
        if (!this.elements.count) {
            return;
        }

        this.elements.count.textContent =
            `${visibleCount} observation`
            + (visibleCount > 1 ? "s" : "")
            + (
                totalCount > MAX_OBSERVATIONS
                    ? ` sur ${totalCount}`
                    : ""
            );
    }

    /**
     * Render one observations table row.
     *
     * @param {object} observation
     * @returns {string}
     */
    renderTableRow(observation) {
        return `
            <tr>
                <td>
                    ${escapeHtml(
                        formatDate(
                            observation.observed_at,
                        ),
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        observation.node_id,
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        observation.service_id,
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        observation.capability_id,
                    )}
                </td>

                <td>
                    ${statusBadge(
                        observation.status,
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        formatLatency(
                            observation.latency_ms,
                        ),
                    )}
                </td>
            </tr>
        `;
    }
}