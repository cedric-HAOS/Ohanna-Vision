"use strict";

import {
    normalizeHealthStatus,
} from "./utils.js";

/**
 * Represent one continuous infrastructure health period.
 */
export class TimelinePeriod {
    /**
     * Create one timeline period.
     *
     * @param {object} values
     * @param {string} values.status
     * @param {string|Date} values.startedAt
     * @param {string|Date|null} [values.endedAt]
     * @param {number|null} [values.durationSeconds]
     * @param {boolean} [values.isOpen]
     */
    constructor({
        status,
        startedAt,
        endedAt = null,
        durationSeconds = null,
        isOpen = endedAt === null,
    }) {
        this.status =
            normalizeHealthStatus(status);

        this.startedAt =
            TimelinePeriod.parseDate(
                startedAt,
                "startedAt",
            );

        this.endedAt =
            endedAt === null
                ? null
                : TimelinePeriod.parseDate(
                    endedAt,
                    "endedAt",
                );

        if (
            this.endedAt !== null
            && this.endedAt < this.startedAt
        ) {
            throw new Error(
                "TimelinePeriod endedAt "
                + "must not precede startedAt.",
            );
        }

        this.durationSeconds =
            TimelinePeriod.parseDuration(
                durationSeconds,
            );

        this.isOpen = Boolean(isOpen);

        if (
            this.isOpen
            && this.endedAt !== null
        ) {
            throw new Error(
                "An open TimelinePeriod "
                + "must not define endedAt.",
            );
        }

        if (
            !this.isOpen
            && this.endedAt === null
        ) {
            throw new Error(
                "A closed TimelinePeriod "
                + "must define endedAt.",
            );
        }
    }

    /**
     * Create a period from the timeline API payload.
     *
     * @param {object} payload
     * @returns {TimelinePeriod}
     */
    static fromPayload(payload) {
        if (
            !payload
            || typeof payload !== "object"
            || Array.isArray(payload)
        ) {
            throw new TypeError(
                "TimelinePeriod payload "
                + "must be an object.",
            );
        }

        return new TimelinePeriod({
            status: payload.status,
            startedAt: payload.started_at,
            endedAt: payload.ended_at ?? null,
            durationSeconds:
                payload.duration_seconds ?? null,
            isOpen:
                payload.is_open
                ?? payload.ended_at === null,
        });
    }

    /**
     * Parse a date value.
     *
     * @param {string|Date} value
     * @param {string} fieldName
     * @returns {Date}
     */
    static parseDate(
        value,
        fieldName,
    ) {
        const parsed =
            value instanceof Date
                ? new Date(value.getTime())
                : new Date(value);

        if (
            Number.isNaN(
                parsed.getTime(),
            )
        ) {
            throw new TypeError(
                `TimelinePeriod ${fieldName} `
                + "must be a valid date.",
            );
        }

        return parsed;
    }

    /**
     * Validate the optional duration.
     *
     * @param {number|null} value
     * @returns {number|null}
     */
    static parseDuration(value) {
        if (value === null) {
            return null;
        }

        const duration = Number(value);

        if (
            !Number.isFinite(duration)
            || duration < 0
        ) {
            throw new TypeError(
                "TimelinePeriod durationSeconds "
                + "must be a positive number or null.",
            );
        }

        return duration;
    }

    /**
     * Return the effective end of the period.
     *
     * Open periods end at the supplied reference date.
     *
     * @param {string|Date} referenceDate
     * @returns {Date}
     */
    effectiveEnd(referenceDate) {
        if (this.endedAt !== null) {
            return new Date(
                this.endedAt.getTime(),
            );
        }

        return TimelinePeriod.parseDate(
            referenceDate,
            "referenceDate",
        );
    }

    /**
     * Return whether the period intersects a time window.
     *
     * @param {string|Date} windowStartedAt
     * @param {string|Date} windowEndedAt
     * @returns {boolean}
     */
    overlaps(
        windowStartedAt,
        windowEndedAt,
    ) {
        const start =
            TimelinePeriod.parseDate(
                windowStartedAt,
                "windowStartedAt",
            );

        const end =
            TimelinePeriod.parseDate(
                windowEndedAt,
                "windowEndedAt",
            );

        if (end < start) {
            throw new Error(
                "Timeline window end "
                + "must not precede its start.",
            );
        }

        const effectiveEnd =
            this.effectiveEnd(end);

        return (
            this.startedAt <= end
            && effectiveEnd >= start
        );
    }

    /**
     * Return the portion of the period visible in a window.
     *
     * @param {string|Date} windowStartedAt
     * @param {string|Date} windowEndedAt
     * @returns {{
     *     startedAt: Date,
     *     endedAt: Date,
     * }|null}
     */
    clippedTo(
        windowStartedAt,
        windowEndedAt,
    ) {
        const start =
            TimelinePeriod.parseDate(
                windowStartedAt,
                "windowStartedAt",
            );

        const end =
            TimelinePeriod.parseDate(
                windowEndedAt,
                "windowEndedAt",
            );

        if (!this.overlaps(start, end)) {
            return null;
        }

        const effectiveEnd =
            this.effectiveEnd(end);

        return {
            startedAt: new Date(
                Math.max(
                    this.startedAt.getTime(),
                    start.getTime(),
                ),
            ),
            endedAt: new Date(
                Math.min(
                    effectiveEnd.getTime(),
                    end.getTime(),
                ),
            ),
        };
    }
}