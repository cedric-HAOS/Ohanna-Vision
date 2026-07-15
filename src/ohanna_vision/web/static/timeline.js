"use strict";

import {
    escapeHtml,
    formatDate,
    healthStatusLabel,
    normalizeHealthStatus,
} from "./utils.js";

import {
    TimelinePeriod,
} from "./timeline_period.js";

/**
 * Controls the infrastructure timeline.
 */
export class TimelineController {
    constructor({
        state,
        onNodeSelected = () => {},
    }) {
        if (!state) {
            throw new Error(
                "TimelineController requires application state.",
            );
        }

        this.state = state;
        this.onNodeSelected = onNodeSelected;

        this.elements = {
            content: document.querySelector(
                "#timeline-content",
            ),
            eventCount: document.querySelector(
                "#timeline-event-count",
            ),
            rangeButtons: document.querySelectorAll(
                "[data-timeline-hours]",
            ),
        };
        this.periods = [];
    }

    /**
     * Synchronize timeline periods from the shared application state.
     */
    updatePeriods() {
        const timeline =
            this.state.timeline;

        if (
            !timeline
            || !Array.isArray(
                timeline.periods,
            )
        ) {
            this.periods = [];

            return;
        }

        this.periods =
            timeline.periods.map(
                (period) =>
                    TimelinePeriod.fromPayload(
                        period,
                    ),
            );
    }

    /**
     * Bind timeline interactions and render its initial state.
     */
    initialize() {
        this.bindRangeButtons();
        this.render();
    }

    /**
     * Return the currently loaded periods.
     *
     * @returns {TimelinePeriod[]}
     */
    getPeriods() {
        return [
            ...this.periods,
        ];
    }

    /**
     * Render the timeline from the shared observations.
     */
    render() {
        this.updatePeriods();
        if (!this.elements.content) {
            return;
        }

        const {
            startedAt,
            endedAt,
        } = this.timelineRange();

        const observations =
            Array.isArray(this.state.observations)
                ? this.state.observations
                : [];

        const visibleObservations =
            observations.filter((observation) => {
                return this.isObservationVisible(
                    observation,
                    startedAt,
                    endedAt,
                );
            });

        this.renderEventCount(
            visibleObservations.length,
        );

        const groups =
            this.groupObservationsByNode(
                observations,
            ).filter((group) => {
                return group.observations.some(
                    (observation) => {
                        return this.isObservationVisible(
                            observation,
                            startedAt,
                            endedAt,
                        );
                    },
                );
            });

        if (groups.length === 0) {
            this.renderEmpty(
                startedAt,
                endedAt,
            );
            return;
        }

        this.elements.content.innerHTML = `
            ${this.renderAxis(
                startedAt,
                endedAt,
            )}

            <div class="timeline-rows">
                ${groups
                    .map((group) => {
                        return this.renderRow(
                            group,
                            startedAt,
                            endedAt,
                        );
                    })
                    .join("")}
            </div>
        `;

        this.bindTimelineInteractions();
    }

    /**
     * Return the active timeline range.
     *
     * @returns {{
     *     startedAt: Date,
     *     endedAt: Date,
     * }}
     */
    timelineRange() {
        const endedAt = new Date();

        const hours = Number(
            this.state.timelineRangeHours ?? 6,
        );

        const startedAt = new Date(
            endedAt.getTime()
            - hours
            * 60
            * 60
            * 1000,
        );

        return {
            startedAt,
            endedAt,
        };
    }

    /**
     * Change the active timeline range.
     *
     * @param {number} hours
     */
    setRange(hours) {
        if (
            !Number.isFinite(hours)
            || hours <= 0
        ) {
            return;
        }

        this.state.timelineRangeHours = hours;

        for (
            const button
            of this.elements.rangeButtons
        ) {
            const buttonHours = Number(
                button.dataset.timelineHours,
            );

            button.classList.toggle(
                "timeline-range__button--active",
                buttonHours === hours,
            );
        }

        this.render();
    }

    bindRangeButtons() {
        for (
            const button
            of this.elements.rangeButtons
        ) {
            button.addEventListener(
                "click",
                () => {
                    const hours = Number(
                        button.dataset.timelineHours,
                    );

                    this.setRange(hours);
                },
            );
        }
    }

    bindTimelineInteractions() {
        const nodeButtons =
            this.elements.content.querySelectorAll(
                "[data-timeline-node]",
            );

        for (const button of nodeButtons) {
            button.addEventListener(
                "click",
                () => {
                    this.onNodeSelected(
                        button.dataset.timelineNode,
                    );
                },
            );
        }

        const eventButtons =
            this.elements.content.querySelectorAll(
                "[data-node-id]",
            );

        for (const button of eventButtons) {
            button.addEventListener(
                "click",
                () => {
                    this.onNodeSelected(
                        button.dataset.nodeId,
                    );
                },
            );
        }
    }

    renderEventCount(count) {
        if (!this.elements.eventCount) {
            return;
        }

        this.elements.eventCount.textContent =
            `${count} événement`
            + (count > 1 ? "s" : "");
    }

    renderEmpty(
        startedAt,
        endedAt,
    ) {
        const hours =
            this.state.timelineRangeHours ?? 6;

        this.elements.content.innerHTML = `
            ${this.renderAxis(
                startedAt,
                endedAt,
            )}

            <p class="timeline-empty">
                Aucune observation durant les
                ${escapeHtml(hours)}
                dernières heures.
            </p>
        `;
    }

    renderAxis(
        startedAt,
        endedAt,
    ) {
        const ticks = 5;

        const labels = Array.from(
            {
                length: ticks,
            },
            (_, index) => {
                const ratio =
                    index / (ticks - 1);

                const date = new Date(
                    startedAt.getTime()
                    + (
                        endedAt.getTime()
                        - startedAt.getTime()
                    )
                    * ratio,
                );

                return `
                    <span>
                        ${escapeHtml(
                            this.timelineTimeLabel(
                                date,
                            ),
                        )}
                    </span>
                `;
            },
        ).join("");

        return `
            <div class="timeline-axis">
                <span
                    class="timeline-axis__spacer"
                ></span>

                <div class="timeline-axis__labels">
                    ${labels}
                </div>
            </div>
        `;
    }

    renderRow(
        group,
        startedAt,
        endedAt,
    ) {
        const visibleObservations =
            group.observations.filter(
                (observation) => {
                    return this.isObservationVisible(
                        observation,
                        startedAt,
                        endedAt,
                    );
                },
            );

        const events = visibleObservations
            .map((observation) => {
                return this.renderEvent(
                    group.nodeId,
                    observation,
                    startedAt,
                    endedAt,
                );
            })
            .join("");

        const latest =
            visibleObservations.at(-1)
            ?? group.observations.at(-1);

        const latestStatus =
            normalizeHealthStatus(
                latest?.status,
            );

        return `
            <div class="timeline-row">
                <button
                    class="timeline-row__node"
                    type="button"
                    data-timeline-node="${escapeHtml(
                        group.nodeId,
                    )}"
                    title="Sélectionner ${escapeHtml(
                        group.nodeId,
                    )}"
                >
                    <span
                        class="timeline-row__status
                            timeline-row__status--${latestStatus}"
                    ></span>

                    <span>
                        ${escapeHtml(
                            group.nodeId,
                        )}
                    </span>
                </button>

                <div class="timeline-row__track">
                    <span
                        class="timeline-row__current
                            timeline-row__current--${latestStatus}"
                    ></span>

                    ${events}
                </div>
            </div>
        `;
    }

    renderEvent(
        nodeId,
        observation,
        startedAt,
        endedAt,
    ) {
        const status =
            normalizeHealthStatus(
                observation.status,
            );

        const position =
            this.timelinePosition(
                observation.observed_at,
                startedAt,
                endedAt,
            );

        const title = [
            observation.capability_id,
            observation.service_id,
            formatDate(
                observation.observed_at,
            ),
            healthStatusLabel(status),
        ].join(" · ");

        return `
            <button
                class="timeline-event
                    timeline-event--${status}"
                type="button"
                style="left: ${position}%"
                title="${escapeHtml(title)}"
                aria-label="${escapeHtml(title)}"
                data-node-id="${escapeHtml(nodeId)}"
            >
                <span></span>
            </button>
        `;
    }

    /**
     * Render one timeline period.
     *
     * @param {string} nodeId
     * @param {TimelinePeriod} period
     * @param {Date} startedAt
     * @param {Date} endedAt
     * @returns {string}
     */
    renderPeriod(
        nodeId,
        period,
        startedAt,
        endedAt,
    ) {
        const position =
            this.timelinePosition(
                period.startedAt,
                startedAt,
                endedAt,
            );

        const title = [
            formatDate(
                period.startedAt,
            ),
            period.endedAt
                ? formatDate(
                    period.endedAt,
                )
                : "En cours",
            healthStatusLabel(
                period.status,
            ),
        ].join(" · ");

        return `
            <button
                class="timeline-period
                    timeline-period--${period.status}"
                type="button"
                style="left: ${position}%"
                title="${escapeHtml(title)}"
                aria-label="${escapeHtml(title)}"
                data-node-id="${escapeHtml(nodeId)}"
            >
                <span></span>
            </button>
        `;
    }

    groupObservationsByNode(observations) {
        const groups = new Map();

        for (const observation of observations) {
            const nodeId =
                observation.node_id
                ?? "unknown";

            if (!groups.has(nodeId)) {
                groups.set(nodeId, []);
            }

            groups
                .get(nodeId)
                .push(observation);
        }

        return Array.from(
            groups.entries(),
        )
            .map(
                ([
                    nodeId,
                    nodeObservations,
                ]) => {
                    return {
                        nodeId,
                        observations:
                            nodeObservations.sort(
                                (
                                    first,
                                    second,
                                ) => {
                                    return (
                                        new Date(
                                            first.observed_at,
                                        ).getTime()
                                        - new Date(
                                            second.observed_at,
                                        ).getTime()
                                    );
                                },
                            ),
                    };
                },
            )
            .sort((first, second) => {
                return first.nodeId.localeCompare(
                    second.nodeId,
                );
            });
    }

    /**
     * Group timeline periods by node.
     *
     * @returns {Array<{
     *     nodeId: string,
     *     periods: TimelinePeriod[],
     * }>}
     */
    groupPeriodsByNode() {
        const groups = new Map();

        for (const period of this.periods) {
            const nodeId =
                period.nodeId
                ?? "infrastructure";

            if (!groups.has(nodeId)) {
                groups.set(
                    nodeId,
                    [],
                );
            }

            groups
                .get(nodeId)
                .push(period);
        }

        return Array.from(
            groups.entries(),
        )
            .map(
                ([
                    nodeId,
                    periods,
                ]) => ({
                    nodeId,
                    periods: periods.sort(
                        (
                            first,
                            second,
                        ) =>
                            first.startedAt
                                .getTime()
                            - second.startedAt
                                .getTime(),
                    ),
                }),
            )
            .sort(
                (first, second) =>
                    first.nodeId.localeCompare(
                        second.nodeId,
                    ),
            );
    }
    isObservationVisible(
        observation,
        startedAt,
        endedAt,
    ) {
        const observedAt = new Date(
            observation.observed_at,
        );

        if (
            Number.isNaN(
                observedAt.getTime(),
            )
        ) {
            return false;
        }

        return (
            observedAt >= startedAt
            && observedAt <= endedAt
        );
    }

    timelinePosition(
        observedAt,
        startedAt,
        endedAt,
    ) {
        const timestamp =
            new Date(observedAt).getTime();

        const start =
            startedAt.getTime();

        const end =
            endedAt.getTime();

        const duration =
            end - start;

        if (
            !Number.isFinite(timestamp)
            || duration <= 0
        ) {
            return 0;
        }

        return Math.min(
            100,
            Math.max(
                0,
                (
                    timestamp - start
                )
                / duration
                * 100,
            ),
        );
    }

    timelineTimeLabel(date) {
        return new Intl.DateTimeFormat(
            "fr-FR",
            {
                hour: "2-digit",
                minute: "2-digit",
            },
        ).format(date);
    }
}