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
            periodCount: document.querySelector(
                "#timeline-period-count",
            ),
            rangeButtons: document.querySelectorAll(
                "[data-timeline-hours]",
            ),
        };
        this.periodGroups = [];
    }

    /**
     * Synchronize node periods from the shared timeline.
     */
    updatePeriods() {
        const nodes =
            Array.isArray(
                this.state.timeline?.nodes,
            )
                ? this.state.timeline.nodes
                : [];

        this.periodGroups =
            nodes.map((node) => {
                const periods =
                    Array.isArray(node.periods)
                        ? node.periods
                        : [];

                return {
                    nodeId:
                        node.node_id
                        ?? "unknown",
                    periods:
                        periods.map(
                            (period) =>
                                TimelinePeriod
                                    .fromPayload(
                                        period,
                                    ),
                        ),
                };
            });
    }

    /**
     * Bind timeline interactions and render its initial state.
     */
    initialize() {
        this.bindRangeButtons();
        this.render();
    }

    /**
     * Return all loaded periods.
     *
     * @returns {TimelinePeriod[]}
     */
    getPeriods() {
        return this.periodGroups.flatMap(
            (group) => group.periods,
        );
    }

    /**
     * Render the timeline from node periods.
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

        const groups =
            this.periodGroups.filter(
                (group) => {
                    return group.periods.some(
                        (period) =>
                            period.overlaps(
                                startedAt,
                                endedAt,
                            ),
                    );
                },
            );

        const visiblePeriodCount =
            groups.reduce(
                (count, group) => {
                    return count
                        + group.periods.filter(
                            (period) =>
                                period.overlaps(
                                    startedAt,
                                    endedAt,
                                ),
                        ).length;
                },
                0,
            );

        this.renderPeriodCount(
            visiblePeriodCount,
        );

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
                        return this.renderPeriodRow(
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

    renderPeriodCount(count) {
        if (!this.elements.periodCount) {
            return;
        }

        this.elements.periodCount.textContent =
            `${count} période`
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
                Aucune période disponible durant les
                ${escapeHtml(hours)}
                dernières heures.
            </p>
        `;
    }

    /**
     * Render a timeline loading error.
     *
     * @param {string} message
     */
    renderError(message) {
        if (!this.elements.content) {
            return;
        }

        this.renderPeriodCount(0);

        this.elements.content.innerHTML = `
            <p
                class="timeline-empty
                    timeline-empty--error"
                role="alert"
            >
                ${escapeHtml(message)}
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

    /**
     * Render one node row from timeline periods.
     *
     * @param {{
     *     nodeId: string,
     *     periods: TimelinePeriod[],
     * }} group
     * @param {Date} startedAt
     * @param {Date} endedAt
     * @returns {string}
     */
    renderPeriodRow(
        group,
        startedAt,
        endedAt,
    ) {
        const visiblePeriods =
            group.periods.filter(
                (period) =>
                    period.overlaps(
                        startedAt,
                        endedAt,
                    ),
            );

        const latest =
            visiblePeriods.at(-1)
            ?? group.periods.at(-1);

        const latestStatus =
            normalizeHealthStatus(
                latest?.status,
            );

        const periods =
            visiblePeriods
                .map((period) => {
                    return this.renderPeriod(
                        group.nodeId,
                        period,
                        startedAt,
                        endedAt,
                    );
                })
                .join("");

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

                    ${periods}
                </div>
            </div>
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
        const visiblePeriod =
            period.clippedTo(
                startedAt,
                endedAt,
            );

        if (!visiblePeriod) {
            return "";
        }

        const left =
            this.timelinePosition(
                visiblePeriod.startedAt,
                startedAt,
                endedAt,
            );

        const right =
            this.timelinePosition(
                visiblePeriod.endedAt,
                startedAt,
                endedAt,
            );

        const width =
            Math.max(
                right - left,
                0.5,
            );

        const classes = [
            "timeline-period",
            `timeline-period--${period.status}`,
        ];

        if (period.isOpen) {
            classes.push(
                "timeline-period--open",
            );
        }

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
                class="${classes.join(" ")}"
                type="button"
                style="
                    left: ${left}%;
                    width: ${width}%;
                "
                title="${escapeHtml(title)}"
                aria-label="${escapeHtml(title)}"
                data-node-id="${escapeHtml(nodeId)}"
            >
                <span></span>
            </button>
        `;
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