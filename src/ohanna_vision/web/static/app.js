"use strict";

const API = {
    runtime: "/api/runtime",
    observations: "/api/observations",
    timeline: "/api/timeline",
    topology: "/api/topology",
};

const MAX_OBSERVATIONS = 50;
const WEBSOCKET_RECONNECT_DELAY_MS = 3000;

const elements = {

    topologyZoomIn: document.querySelector(
        "#topology-zoom-in",
    ),
    topologyZoomOut: document.querySelector(
        "#topology-zoom-out",
    ),
    topologyResetView: document.querySelector(
        "#topology-reset-view",
    ),

    refreshButton: document.querySelector("#refresh-button"),
    lastRefresh: document.querySelector("#last-refresh"),

    websocketStatus: document.querySelector(
        "#websocket-status",
    ),
    websocketStatusLabel: document.querySelector(
        "#websocket-status-label",
    ),

    runtimeError: document.querySelector("#runtime-error"),

    observationsReceived: document.querySelector(
        "#observations-received",
    ),
    observationsAccepted: document.querySelector(
        "#observations-accepted",
    ),
    observationsRejected: document.querySelector(
        "#observations-rejected",
    ),
    runtimeErrors: document.querySelector("#runtime-errors"),

    topologyError: document.querySelector(
        "#topology-error",
    ),
    topologyContainer: document.querySelector(
        "#topology-container",
    ),
    topologyLayoutLabel: document.querySelector(
        "#topology-layout-label",
    ),

    observationsError: document.querySelector(
        "#observations-error",
    ),
    observationsBody: document.querySelector(
        "#observations-body",
    ),
    observationCount: document.querySelector(
        "#observation-count",
    ),
    deviceDetails: document.querySelector(
        "#device-details",
    ),
    deviceDetailsClose: document.querySelector(
        "#device-details-close",
    ),
    deviceDetailsTitle: document.querySelector(
        "#device-details-title",
    ),
    deviceDetailsKind: document.querySelector(
        "#device-details-kind",
    ),
    deviceDetailsHealth: document.querySelector(
        "#device-details-health",
    ),
    deviceDetailsHealthLabel: document.querySelector(
        "#device-details-health-label",
    ),
    deviceDetailsId: document.querySelector(
        "#device-details-id",
    ),
    deviceDetailsNode: document.querySelector(
        "#device-details-node",
    ),
    deviceDetailsAddress: document.querySelector(
        "#device-details-address",
    ),
    deviceDetailsRole: document.querySelector(
        "#device-details-role",
    ),
    deviceDetailsModel: document.querySelector(
        "#device-details-model",
    ),
    deviceLinksCount: document.querySelector(
        "#device-links-count",
    ),
    deviceLinksList: document.querySelector(
        "#device-links-list",
    ),
    deviceDetailsIcon: document.querySelector(
        "#device-details-icon",
    ),
    deviceDetailsPrimary: document.querySelector(
        "#device-details-primary",
    ),
    deviceDetailsSupervision: document.querySelector(
        "#device-details-supervision",
    ),
    deviceDetailsManufacturer: document.querySelector(
        "#device-details-manufacturer",
    ),
    availabilityValue: document.querySelector(
        "#availability-value",
    ),
    availabilityProgress: document.querySelector(
        "#availability-progress",
    ),
    availabilityTrend: document.querySelector(
        "#availability-trend",
    ),
    devicesCount: document.querySelector(
        "#devices-count",
    ),
    healthyDevicesCount: document.querySelector(
        "#healthy-devices-count",
    ),
    servicesCount: document.querySelector(
        "#services-count",
    ),
    capabilitiesCount: document.querySelector(
        "#capabilities-count",
    ),
    alertsKpi: document.querySelector(
        "#alerts-kpi",
    ),
    alertsCount: document.querySelector(
        "#alerts-count",
    ),
    alertsKpiStatus: document.querySelector(
        "#alerts-kpi-status",
    ),
    activityCount: document.querySelector(
        "#activity-count",
    ),
    topologyHealthIndicator: document.querySelector(
        "#topology-health-indicator",
    ),
    topologyHealthLabel: document.querySelector(
        "#topology-health-label",
    ),
    activeAlertsCount: document.querySelector(
        "#active-alerts-count",
    ),
    activeAlertsList: document.querySelector(
        "#active-alerts-list",
    ),
    recentObservationsList: document.querySelector(
        "#recent-observations-list",
    ),
    acceptanceRate: document.querySelector(
        "#acceptance-rate",
    ),
    acceptanceRateProgress: document.querySelector(
        "#acceptance-rate-progress",
    ),
    timelineContent: document.querySelector(
        "#timeline-content",
    ),
    timelineEventCount: document.querySelector(
        "#timeline-event-count",
    ),
    timelineRangeButtons: document.querySelectorAll(
        "[data-timeline-hours]",
    ),
};

let currentTopology = null;
let currentDeviceHealth = {};
let selectedDeviceId = null;
let currentRuntime = null;
let currentObservations = [];
let currentTimelineRangeHours = 6;

function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = String(value ?? "");

    return element.innerHTML;
}

function formatDate(value) {
    if (!value) {
        return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return new Intl.DateTimeFormat("fr-FR", {
        dateStyle: "short",
        timeStyle: "medium",
    }).format(date);
}

function formatLatency(value) {
    if (value === null || value === undefined) {
        return "—";
    }

    const latency = Number(value);

    if (!Number.isFinite(latency)) {
        return "—";
    }

    return `${latency.toFixed(2)} ms`;
}

function statusClass(status) {
    const normalized = String(
        status ?? "unknown",
    ).toLowerCase();

    return `status-badge status-badge--${normalized}`;
}

function statusBadge(status) {
    const normalized = String(status ?? "unknown");

    return `
        <span class="${statusClass(normalized)}">
            ${escapeHtml(normalized)}
        </span>
    `;
}

function showError(element, message) {
    element.textContent = message;
    element.classList.remove("hidden");
}

function hideError(element) {
    element.textContent = "";
    element.classList.add("hidden");
}

const topologyCanvas = new window.TopologyCanvas({
    container: elements.topologyContainer,
    layoutLabel: elements.topologyLayoutLabel,
    showError: (message) => {
        showError(
            elements.topologyError,
            message,
        );
    },
    hideError: () => {
        hideError(elements.topologyError);
    },
    onDeviceSelected: (deviceId) => {
        selectDevice(deviceId);
    },
});

function normalizeTimelineStatus(status) {
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

function timelineRange() {
    const endedAt = new Date();
    const startedAt = new Date(
        endedAt.getTime()
        - currentTimelineRangeHours
        * 60
        * 60
        * 1000,
    );

    return {
        startedAt,
        endedAt,
    };
}

function timelinePosition(
    observedAt,
    startedAt,
    endedAt,
) {
    const timestamp = new Date(observedAt).getTime();
    const start = startedAt.getTime();
    const end = endedAt.getTime();
    const duration = end - start;

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
            (timestamp - start) / duration * 100,
        ),
    );
}

function groupObservationsByNode(observations) {
    const groups = new Map();

    for (const observation of observations) {
        const nodeId =
            observation.node_id ?? "unknown";

        if (!groups.has(nodeId)) {
            groups.set(nodeId, []);
        }

        groups.get(nodeId).push(observation);
    }

    return Array.from(groups.entries())
        .map(([nodeId, nodeObservations]) => {
            return {
                nodeId,
                observations: nodeObservations.sort(
                    (first, second) => {
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
        })
        .sort((first, second) => {
            return first.nodeId.localeCompare(
                second.nodeId,
            );
        });
}

function renderTimelineAxis(
    startedAt,
    endedAt,
) {
    const ticks = 5;

    const labels = Array.from(
        {
            length: ticks,
        },
        (_, index) => {
            const ratio = index / (ticks - 1);

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
                        timelineTimeLabel(date),
                    )}
                </span>
            `;
        },
    ).join("");

    return `
        <div class="timeline-axis">
            <span class="timeline-axis__spacer"></span>

            <div class="timeline-axis__labels">
                ${labels}
            </div>
        </div>
    `;
}

function renderTimelineRow(
    group,
    startedAt,
    endedAt,
) {
    const visibleObservations =
        group.observations.filter(
            (observation) => {
                const observedAt = new Date(
                    observation.observed_at,
                );

                return (
                    observedAt >= startedAt
                    && observedAt <= endedAt
                );
            },
        );

    const events = visibleObservations
        .map((observation) => {
            const status =
                normalizeTimelineStatus(
                    observation.status,
                );

            const position = timelinePosition(
                observation.observed_at,
                startedAt,
                endedAt,
            );

            const title = [
                observation.capability_id,
                observation.service_id,
                formatDate(observation.observed_at),
                observationStatusLabel(status),
            ].join(" · ");

            return `
                <button
                    class="timeline-event
                        timeline-event--${status}"
                    type="button"
                    style="left: ${position}%"
                    title="${escapeHtml(title)}"
                    aria-label="${escapeHtml(title)}"
                    data-node-id="${escapeHtml(
                        group.nodeId,
                    )}"
                >
                    <span></span>
                </button>
            `;
        })
        .join("");

    const latest =
        visibleObservations.at(-1)
        ?? group.observations.at(-1);

    const latestStatus =
        normalizeTimelineStatus(
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
                    ${escapeHtml(group.nodeId)}
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

function renderInfrastructureTimeline() {
    const {
        startedAt,
        endedAt,
    } = timelineRange();

    const visibleObservations =
        currentObservations.filter(
            (observation) => {
                const observedAt = new Date(
                    observation.observed_at,
                );

                return (
                    observedAt >= startedAt
                    && observedAt <= endedAt
                );
            },
        );

    elements.timelineEventCount.textContent =
        `${visibleObservations.length} événement`
        + (
            visibleObservations.length > 1
                ? "s"
                : ""
        );

    const groups = groupObservationsByNode(
        currentObservations,
    ).filter((group) => {
        return group.observations.some(
            (observation) => {
                const observedAt = new Date(
                    observation.observed_at,
                );

                return (
                    observedAt >= startedAt
                    && observedAt <= endedAt
                );
            },
        );
    });

    if (groups.length === 0) {
        elements.timelineContent.innerHTML = `
            ${renderTimelineAxis(
                startedAt,
                endedAt,
            )}

            <p class="timeline-empty">
                Aucune observation durant les
                ${currentTimelineRangeHours} dernières heures.
            </p>
        `;
        return;
    }

    elements.timelineContent.innerHTML = `
        ${renderTimelineAxis(
            startedAt,
            endedAt,
        )}

        <div class="timeline-rows">
            ${groups
                .map((group) => {
                    return renderTimelineRow(
                        group,
                        startedAt,
                        endedAt,
                    );
                })
                .join("")}
        </div>
    `;

    attachTimelineInteractions();
}

function selectTopologyDeviceByNode(nodeId) {
    if (!currentTopology) {
        return;
    }

    const device = (
        currentTopology.devices ?? []
    ).find((candidate) => {
        return candidate.node_id === nodeId;
    });

    if (device) {
        selectDevice(device.device_id);
    }
}

function attachTimelineInteractions() {
    const nodeButtons =
        elements.timelineContent.querySelectorAll(
            "[data-timeline-node]",
        );

    for (const button of nodeButtons) {
        button.addEventListener("click", () => {
            selectTopologyDeviceByNode(
                button.dataset.timelineNode,
            );
        });
    }

    const eventButtons =
        elements.timelineContent.querySelectorAll(
            "[data-node-id]",
        );

    for (const button of eventButtons) {
        button.addEventListener("click", () => {
            selectTopologyDeviceByNode(
                button.dataset.nodeId,
            );
        });
    }
}

function timelineTimeLabel(date) {
    return new Intl.DateTimeFormat("fr-FR", {
        hour: "2-digit",
        minute: "2-digit",
    }).format(date);
}

async function fetchJson(url) {
    const response = await fetch(url, {
        headers: {
            Accept: "application/json",
        },
    });

    if (!response.ok) {
        let detail = `${response.status} ${response.statusText}`;

        try {
            const payload = await response.json();

            if (payload.detail) {
                detail = payload.detail;
            }
        } catch {
            // Conserver le message HTTP générique.
        }

        throw new Error(detail);
    }

    return response.json();
}

function uniqueValues(values) {
    return new Set(
        values.filter(
            (value) => value !== null
                && value !== undefined
                && value !== "",
        ),
    );
}

function deviceHealthStatistics(
    topology,
    deviceHealth,
) {
    const devices = topology?.devices ?? [];

    const supervisedDevices = devices.filter(
        (device) => device.node_id,
    );

    const statuses = supervisedDevices.map(
        (device) => {
            return deviceHealth[device.device_id]
                ?? "unknown";
        },
    );

    return {
        total: devices.length,
        supervised: supervisedDevices.length,
        healthy: statuses.filter(
            (status) => status === "healthy",
        ).length,
        degraded: statuses.filter(
            (status) => status === "degraded",
        ).length,
        unhealthy: statuses.filter(
            (status) => status === "unhealthy",
        ).length,
        unknown: statuses.filter(
            (status) => status === "unknown",
        ).length,
    };
}

function globalTopologyHealth(statistics) {
    if (statistics.unhealthy > 0) {
        return "unhealthy";
    }

    if (statistics.degraded > 0) {
        return "degraded";
    }

    if (statistics.healthy > 0) {
        return "healthy";
    }

    return "unknown";
}

function formatGlobalTopologyHealth(status) {
    const labels = {
        healthy: "Infrastructure saine",
        degraded: "Infrastructure dégradée",
        unhealthy: "Incident actif",
        unknown: "État inconnu",
    };

    return labels[status] ?? labels.unknown;
}

function availabilityPercentage(statistics) {
    const knownDevices =
        statistics.healthy
        + statistics.degraded
        + statistics.unhealthy;

    if (knownDevices === 0) {
        return null;
    }

    return (
        statistics.healthy
        / knownDevices
        * 100
    );
}

function alertSeverity(status) {
    if (status === "unhealthy") {
        return 2;
    }

    if (status === "degraded") {
        return 1;
    }

    return 0;
}

function alertStatusLabel(status) {
    const labels = {
        degraded: "Dégradé",
        unhealthy: "Indisponible",
    };

    return labels[status] ?? "Inconnu";
}

function deviceDetailLabel(device) {
    return (
        device.address
        ?? device.node_id
        ?? device.metadata?.model
        ?? device.device_id
    );

}

function renderActiveAlerts() {
    const devices = currentTopology?.devices ?? [];

    const alerts = devices
        .map((device) => {
            return {
                device,
                status:
                    currentDeviceHealth[device.device_id]
                    ?? "unknown",
            };
        })
        .filter(({ status }) => {
            return (
                status === "degraded"
                || status === "unhealthy"
            );
        })
        .sort((first, second) => {
            return (
                alertSeverity(second.status)
                - alertSeverity(first.status)
            );
        });

    elements.activeAlertsCount.textContent =
        String(alerts.length);

    if (alerts.length === 0) {
        elements.activeAlertsList.innerHTML = `
            <div class="active-alerts__empty">
                <span aria-hidden="true">✓</span>

                <div>
                    <strong>Infrastructure stable</strong>
                    <p>Aucune alerte active.</p>
                </div>
            </div>
        `;
        return;
    }

    elements.activeAlertsList.innerHTML = alerts
        .map(({ device, status }) => {
            return `
                <button
                    class="active-alert
                        active-alert--${escapeHtml(status)}"
                    type="button"
                    data-device-id="${escapeHtml(
                        device.device_id,
                    )}"
                >
                    <span
                        class="active-alert__indicator"
                        aria-hidden="true"
                    ></span>

                    <span class="active-alert__content">
                        <strong>
                            ${escapeHtml(device.label)}
                        </strong>

                        <small>
                            ${escapeHtml(
                                deviceDetailLabel(device),
                            )}
                        </small>
                    </span>

                    <span class="active-alert__status">
                        ${escapeHtml(
                            alertStatusLabel(status),
                        )}
                    </span>
                </button>
            `;
        })
        .join("");

    const alertButtons =
        elements.activeAlertsList.querySelectorAll(
            "[data-device-id]",
        );

    for (const button of alertButtons) {
        button.addEventListener("click", () => {
            selectDevice(button.dataset.deviceId);
        });
    }
}

function observationStatusLabel(status) {
    const labels = {
        healthy: "Sain",
        degraded: "Dégradé",
        unhealthy: "Indisponible",
        unknown: "Inconnu",
    };

    return labels[status] ?? String(status ?? "Inconnu");
}

function renderRecentObservations(observations) {
    const recent = observations
        .slice()
        .sort((first, second) => {
            return (
                new Date(second.observed_at).getTime()
                - new Date(first.observed_at).getTime()
            );
        })
        .slice(0, 6);

    if (recent.length === 0) {
        elements.recentObservationsList.innerHTML = `
            <p class="side-panel-placeholder">
                Aucune observation reçue.
            </p>
        `;
        return;
    }

    elements.recentObservationsList.innerHTML = recent
        .map((observation) => {
            const status =
                String(
                    observation.status ?? "unknown",
                ).toLowerCase();

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
                                observationStatusLabel(status),
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
        })
        .join("");
}

function renderAcceptanceRate(statistics) {
    const received = Number(
        statistics.observations_received ?? 0,
    );
    const accepted = Number(
        statistics.observations_accepted ?? 0,
    );

    if (received === 0) {
        elements.acceptanceRate.textContent = "—";
        elements.acceptanceRateProgress.style.width = "0%";
        return;
    }

    const rate = Math.min(
        100,
        Math.max(
            0,
            accepted / received * 100,
        ),
    );

    elements.acceptanceRate.textContent =
        `${rate.toFixed(1)} %`;

    elements.acceptanceRateProgress.style.width =
        `${rate}%`;
}

function renderDashboardKpis() {
    const health = deviceHealthStatistics(
        currentTopology,
        currentDeviceHealth,
    );

    const globalHealth =
        globalTopologyHealth(health);

    elements.topologyHealthIndicator.className =
        "topology-heading-status__indicator "
        + `topology-heading-status__indicator--${globalHealth}`;

    elements.topologyHealthLabel.textContent =
        formatGlobalTopologyHealth(globalHealth);

    const availability =
        availabilityPercentage(health);

    if (availability === null) {
        updateAnimatedText(
            elements.availabilityValue,
            "—",
        );
        elements.availabilityProgress.style.width = "0%";
        elements.availabilityTrend.textContent =
            "En attente de données";
    } else {
        updateAnimatedText(
            elements.availabilityValue,
            `${availability.toFixed(1)} %`,
        );

        elements.availabilityProgress.style.width =
            `${availability}%`;

        elements.availabilityTrend.textContent =
            availability === 100
                ? "Infrastructure saine"
                : "Attention requise";
    }

    updateAnimatedText(
        elements.devicesCount,
        health.total,
    );

    elements.healthyDevicesCount.textContent =
        `${health.healthy} sain`
        + (health.healthy > 1 ? "s" : "");

    const observedServices = uniqueValues(
        currentObservations.map(
            (observation) => observation.service_id,
        ),
    ).size;

    const runtimeServices = Number(
        currentRuntime?.service_timelines ?? 0,
    );

    updateAnimatedText(
        elements.servicesCount,
        Math.max(
            observedServices,
            runtimeServices,
        ),
    );

    const capabilities = uniqueValues(
        currentObservations.map(
            (observation) => observation.capability_id,
        ),
    ).size;

    updateAnimatedText(
        elements.capabilitiesCount,
        capabilities,
    );

    const alerts =
        health.degraded + health.unhealthy;

    updateAnimatedText(
        elements.alertsCount,
        alerts,
    );

    elements.alertsKpi.classList.toggle(
        "dashboard-kpi--warning",
        health.degraded > 0 && health.unhealthy === 0,
    );

    elements.alertsKpi.classList.toggle(
        "dashboard-kpi--critical",
        health.unhealthy > 0,
    );

    if (health.unhealthy > 0) {
        elements.alertsKpiStatus.textContent =
            `${health.unhealthy} indisponible`
            + (health.unhealthy > 1 ? "s" : "");
    } else if (health.degraded > 0) {
        elements.alertsKpiStatus.textContent =
            `${health.degraded} dégradé`
            + (health.degraded > 1 ? "s" : "");
    } else {
        elements.alertsKpiStatus.textContent =
            "Aucun incident";
    }

    updateAnimatedText(
        elements.activityCount,
        currentRuntime
            ?.statistics
            ?.observations_received
        ?? currentObservations.length,
    );;
}

function updateAnimatedText(element, value) {
    const normalizedValue = String(value);

    if (element.textContent === normalizedValue) {
        return;
    }

    element.textContent = normalizedValue;
    animateKpi(element);
}

function renderRuntime(runtime) {
    const statistics = runtime.statistics ?? {};

    currentRuntime = runtime;

    elements.observationsReceived.textContent =
        statistics.observations_received ?? 0;
    elements.observationsAccepted.textContent =
        statistics.observations_accepted ?? 0;
    elements.observationsRejected.textContent =
        statistics.observations_rejected ?? 0;
    elements.runtimeErrors.textContent =
        statistics.errors ?? 0;

    renderAcceptanceRate(statistics);
    renderDashboardKpis();
    hideError(elements.runtimeError);
}

function renderObservations(observations) {
    currentObservations = observations;
    renderInfrastructureTimeline();
    renderRecentObservations(observations);
    const visibleObservations = observations
        .slice()
        .sort((first, second) => {
            return (
                new Date(second.observed_at).getTime()
                - new Date(first.observed_at).getTime()
            );
        })
        .slice(0, MAX_OBSERVATIONS);

    elements.observationCount.textContent =
        `${visibleObservations.length} observation`
        + (visibleObservations.length > 1 ? "s" : "")
        + (
            observations.length > MAX_OBSERVATIONS
                ? ` sur ${observations.length}`
                : ""
        );

    if (visibleObservations.length === 0) {
        elements.observationsBody.innerHTML = `
            <tr>
                <td class="empty-table" colspan="6">
                    Aucune observation enregistrée.
                </td>
            </tr>
        `;

        hideError(elements.observationsError);
        renderDashboardKpis();
        return;
    }

    elements.observationsBody.innerHTML =
        visibleObservations
            .map((observation) => {
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
            })
            .join("");

    hideError(elements.observationsError);
    renderDashboardKpis();
    
}

function currentPeriod(periods) {
    if (!Array.isArray(periods) || periods.length === 0) {
        return null;
    }

    const openPeriod = periods.find(
        (period) => !period.ended_at,
    );

    if (openPeriod) {
        return openPeriod;
    }

    return periods
        .slice()
        .sort((first, second) => {
            return (
                new Date(second.started_at).getTime()
                - new Date(first.started_at).getTime()
            );
        })[0];
}

function currentStatus(periods) {
    return currentPeriod(periods)?.status ?? "unknown";
}

function buildNodeHealthIndex(timeline) {
    const nodes = timeline.nodes ?? {};

    if (Array.isArray(nodes)) {
        return Object.fromEntries(
            nodes.map((node) => [
                node.node_id,
                currentStatus(node.periods),
            ]),
        );
    }

    return Object.fromEntries(
        Object.entries(nodes).map(
            ([nodeId, node]) => [
                nodeId,
                currentStatus(node.periods),
            ],
        ),
    );
}

function buildDeviceHealth(topology, timeline) {
    const nodeHealth = buildNodeHealthIndex(timeline);

    return Object.fromEntries(
        (topology.devices ?? []).map((device) => {
            const status = device.node_id
                ? nodeHealth[device.node_id] ?? "unknown"
                : "unknown";

            return [
                device.device_id,
                status,
            ];
        }),
    );
}

async function loadRuntime() {
    try {
        const runtime = await fetchJson(API.runtime);

        renderRuntime(runtime);
    } catch (error) {
        showError(
            elements.runtimeError,
            `Runtime indisponible : ${error.message}`,
        );
    }
}

async function loadObservations() {
    try {
        const observations = await fetchJson(
            API.observations,
        );

        renderObservations(observations);
    } catch (error) {
        showError(
            elements.observationsError,
            `Observations indisponibles : ${error.message}`,
        );
    }
}

function formatDeviceKind(kind) {
    const labels = {
        internet: "Internet",
        router: "Passerelle",
        switch: "Switch",
        access_point: "Point d’accès",
        server: "Serveur",
        raspberry_pi: "Raspberry Pi",
        home_assistant: "Home Assistant",
        camera: "Caméra",
        smart_device: "Objet connecté",
        solar: "Solaire",
        computer: "Ordinateur",
        storage: "Stockage",
        other: "Équipement",
    };

    return labels[kind] ?? String(kind ?? "Équipement");
}

function formatHealthStatus(status) {
    const labels = {
        healthy: "Sain",
        degraded: "Dégradé",
        unhealthy: "Indisponible",
        unknown: "Inconnu",
    };

    return labels[status] ?? labels.unknown;
}

function metadataValue(device, key) {
    return device.metadata?.[key] ?? "—";
}

function linksForDevice(topology, deviceId) {
    return (topology.links ?? []).filter((link) => {
        return (
            link.source_device_id === deviceId
            || link.target_device_id === deviceId
        );
    });
}

function neighborForLink(link, deviceId) {
    if (link.source_device_id === deviceId) {
        return link.target_device_id;
    }

    return link.source_device_id;
}

function deviceById(topology, deviceId) {
    return (topology.devices ?? []).find(
        (device) => device.device_id === deviceId,
    );
}

function renderDeviceLinks(device) {
    const links = linksForDevice(
        currentTopology,
        device.device_id,
    );

    elements.deviceLinksCount.textContent =
        String(links.length);

    if (links.length === 0) {
        elements.deviceLinksList.innerHTML = `
            <li class="device-details__empty">
                Aucune connexion déclarée.
            </li>
        `;
        return;
    }

    elements.deviceLinksList.innerHTML = links
        .map((link) => {
            const neighborId = neighborForLink(
                link,
                device.device_id,
            );
            const neighbor = deviceById(
                currentTopology,
                neighborId,
            );
            const neighborLabel =
                neighbor?.label ?? neighborId;
            const neighborKind =
                formatDeviceKind(
                    neighbor?.kind ?? "other",
                );
            const linkLabel =
                link.label
                ?? formatDeviceKind(link.kind);
            const direction =
                link.source_device_id
                    === device.device_id
                    ? "sortant"
                    : "entrant";

            return `
                <li class="device-details__link">
                    <div
                        class="device-details__link-icon "
                        data-kind="${escapeHtml(
                            neighbor?.kind ?? "other",
                        )}"
                    >
                        ${deviceIconMarkup(
                            neighbor?.kind ?? "other",
                        )}
                    </div>

                    <div class="device-details__link-content">
                        <strong>
                            ${escapeHtml(neighborLabel)}
                        </strong>

                        <span>
                            ${escapeHtml(neighborKind)}
                        </span>
                    </div>

                    <div class="device-details__link-meta">
                        <span>
                            ${escapeHtml(linkLabel)}
                        </span>

                        <small>
                            ${escapeHtml(direction)}
                        </small>
                    </div>
                </li>
            `;
        })
        .join("");
}

function deviceIconMarkup(kind) {
    const icons = {
        internet: `
            <svg viewBox="0 0 32 32" aria-hidden="true">
                <circle cx="16" cy="16" r="12"></circle>
                <path d="M16 4c-5 5-5 19 0 24"></path>
                <path d="M16 4c5 5 5 19 0 24"></path>
                <path d="M5 11h22"></path>
                <path d="M5 21h22"></path>
            </svg>
        `,
        router: `
            <svg viewBox="0 0 32 32" aria-hidden="true">
                <rect
                    x="4"
                    y="12"
                    width="24"
                    height="13"
                    rx="3"
                ></rect>
                <path d="M9 12V5"></path>
                <path d="M23 12V5"></path>
                <circle cx="11" cy="19" r="1.5"></circle>
                <circle cx="17" cy="19" r="1.5"></circle>
            </svg>
        `,
        switch: `
            <svg viewBox="0 0 32 32" aria-hidden="true">
                <rect
                    x="3"
                    y="8"
                    width="26"
                    height="17"
                    rx="3"
                ></rect>
                <rect x="7" y="14" width="3" height="4"></rect>
                <rect x="12" y="14" width="3" height="4"></rect>
                <rect x="17" y="14" width="3" height="4"></rect>
                <rect x="22" y="14" width="3" height="4"></rect>
            </svg>
        `,
        access_point: `
            <svg viewBox="0 0 32 32" aria-hidden="true">
                <circle cx="16" cy="25" r="2"></circle>
                <path d="M11 21a7 7 0 0 1 10 0"></path>
                <path d="M7 17a12 12 0 0 1 18 0"></path>
                <path d="M3 13a18 18 0 0 1 26 0"></path>
            </svg>
        `,
        raspberry_pi: `
            <svg viewBox="0 0 32 32" aria-hidden="true">
                <rect
                    x="5"
                    y="5"
                    width="22"
                    height="22"
                    rx="4"
                ></rect>
                <path d="M10 10h12v12H10z"></path>
                <path d="M2 9h3M2 16h3M2 23h3"></path>
                <path d="M27 9h3M27 16h3M27 23h3"></path>
            </svg>
        `,
        home_assistant: `
            <svg viewBox="0 0 32 32" aria-hidden="true">
                <path
                    d="M4 15 16 5l12 10v13h-8v-8h-8v8H4z"
                ></path>
            </svg>
        `,
        camera: `
            <svg viewBox="0 0 32 32" aria-hidden="true">
                <rect
                    x="4"
                    y="9"
                    width="24"
                    height="16"
                    rx="3"
                ></rect>
                <circle cx="16" cy="17" r="5"></circle>
                <path d="M12 25v3h8"></path>
            </svg>
        `,
        storage: `
            <svg viewBox="0 0 32 32" aria-hidden="true">
                <path
                    d="M5 8c0-5 22-5 22 0v16
                    c0 5-22 5-22 0z"
                ></path>
                <path d="M5 8c0 5 22 5 22 0"></path>
                <path d="M5 16c0 5 22 5 22 0"></path>
            </svg>
        `,
        solar: `
            <svg viewBox="0 0 32 32" aria-hidden="true">
                <circle cx="16" cy="16" r="6"></circle>
                <path d="M16 3v5M16 24v5"></path>
                <path d="M3 16h5M24 16h5"></path>
                <path d="m7 7 4 4M21 21l4 4"></path>
                <path d="m25 7-4 4M11 21l-4 4"></path>
            </svg>
        `,
    };

    return (
        icons[kind]
        ?? `
            <svg viewBox="0 0 32 32" aria-hidden="true">
                <rect
                    x="5"
                    y="5"
                    width="22"
                    height="22"
                    rx="5"
                ></rect>
            </svg>
        `
    );
}

function primaryDeviceDetail(device) {
    if (device.address) {
        return device.address;
    }

    if (device.node_id) {
        return device.node_id;
    }

    if (device.metadata?.model) {
        return device.metadata.model;
    }

    return device.device_id;
}

function selectDevice(deviceId) {
    if (!currentTopology) {
        return;
    }

    const device = deviceById(
        currentTopology,
        deviceId,
    );

    if (!device) {
        closeDeviceDetails();
        return;
    }

    selectedDeviceId = deviceId;

    const health =
        currentDeviceHealth[deviceId]
        ?? "unknown";
    
    topologyCanvas.setSelectedDevice(deviceId);
    
    elements.deviceDetailsIcon.className =
        "device-details__icon "
        + `device-details__icon--${device.kind}`;

    elements.deviceDetailsIcon.innerHTML =
        deviceIconMarkup(device.kind);
    
    elements.deviceDetailsPrimary.textContent =
        primaryDeviceDetail(device);

    elements.deviceDetailsSupervision.textContent =
        device.node_id
            ? "Supervisé"
            : "Non supervisé";

    elements.deviceDetailsSupervision.className =
        "device-details__supervision "
        + (
            device.node_id
                ? "device-details__supervision--active"
                : "device-details__supervision--inactive"
        );

    elements.deviceDetailsManufacturer.textContent =
        metadataValue(device, "manufacturer");

    elements.deviceDetailsTitle.textContent =
        device.label;
    elements.deviceDetailsKind.textContent =
        formatDeviceKind(device.kind);
    elements.deviceDetailsId.textContent =
        device.device_id;
    elements.deviceDetailsNode.textContent =
        device.node_id ?? "Non supervisé";
    elements.deviceDetailsAddress.textContent =
        device.address ?? "—";
    elements.deviceDetailsRole.textContent =
        metadataValue(device, "role");
    elements.deviceDetailsModel.textContent =
        metadataValue(device, "model");

    elements.deviceDetailsHealth.className =
        "device-details__health "
        + `device-details__health--${health}`;

    elements.deviceDetailsHealthLabel.textContent =
        formatHealthStatus(health);

    renderDeviceLinks(device);

    elements.deviceDetails.classList.remove("hidden");
    elements.deviceDetails.setAttribute(
        "aria-hidden",
        "false",
    );
}

function closeDeviceDetails() {
    selectedDeviceId = null;

    topologyCanvas.setSelectedDevice(null);

    elements.deviceDetails.classList.add("hidden");
    elements.deviceDetails.setAttribute(
        "aria-hidden",
        "true",
    );
}

async function loadInfrastructureMap() {
    try {
        const [
            topology,
            timeline,
        ] = await Promise.all([
            fetchJson(API.topology),
            fetchJson(API.timeline),
        ]);

        const deviceHealth = buildDeviceHealth(
            topology,
            timeline,
        );

        currentTopology = topology;
        currentDeviceHealth = deviceHealth;
        renderActiveAlerts();
        renderDashboardKpis();

        topologyCanvas.render(
            topology,
            deviceHealth,
        );

        if (selectedDeviceId) {
            selectDevice(selectedDeviceId);
        }
    } catch (error) {
        topologyCanvas.renderError(
            `Carte indisponible : ${error.message}`,
        );
    }
}

async function refreshDashboard() {
    elements.refreshButton.disabled = true;

    await Promise.allSettled([
        loadRuntime(),
        loadObservations(),
        loadInfrastructureMap(),
    ]);

    elements.lastRefresh.textContent =
        `Dernière actualisation : ${formatDate(
            new Date().toISOString(),
        )}`;

    elements.refreshButton.disabled = false;
}

function setWebSocketStatus(status, label) {
    elements.websocketStatus.className =
        `connection-status connection-status--${status}`;

    elements.websocketStatusLabel.textContent = label;
}

function websocketUrl() {
    const protocol =
        window.location.protocol === "https:"
            ? "wss:"
            : "ws:";

    return `${protocol}//${window.location.host}/ws`;
}

function connectWebSocket() {
    setWebSocketStatus(
        "connecting",
        "Connexion temps réel…",
    );

    const socket = new WebSocket(websocketUrl());

    socket.addEventListener("open", () => {
        setWebSocketStatus(
            "online",
            "Temps réel connecté",
        );
    });

    socket.addEventListener("message", (event) => {
        let message;

        try {
            message = JSON.parse(event.data);
        } catch {
            return;
        }

        console.debug("WebSocket message:", message);

        if (message.type !== "connected") {
            void refreshDashboard();
        }
    });

    socket.addEventListener("close", () => {
        setWebSocketStatus(
            "offline",
            "Temps réel déconnecté",
        );

        window.setTimeout(
            connectWebSocket,
            WEBSOCKET_RECONNECT_DELAY_MS,
        );
    });

    socket.addEventListener("error", () => {
        socket.close();
    });
}

elements.refreshButton.addEventListener(
    "click",
    () => void refreshDashboard(),
);

elements.deviceDetailsClose.addEventListener(
    "click",
    closeDeviceDetails,
);

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        closeDeviceDetails();
    }
});

elements.topologyZoomIn.addEventListener(
    "click",
    () => {
        topologyCanvas.zoomIn();
    },
);

elements.topologyZoomOut.addEventListener(
    "click",
    () => {
        topologyCanvas.zoomOut();
    },
);

elements.topologyResetView.addEventListener(
    "click",
    () => {
        topologyCanvas.resetView();
    },
);

for (
    const button
    of elements.timelineRangeButtons
) {
    button.addEventListener("click", () => {
        const hours = Number(
            button.dataset.timelineHours,
        );

        if (!Number.isFinite(hours)) {
            return;
        }

        currentTimelineRangeHours = hours;

        for (
            const candidate
            of elements.timelineRangeButtons
        ) {
            candidate.classList.toggle(
                "timeline-range__button--active",
                candidate === button,
            );
        }

        renderInfrastructureTimeline();
    });
}

function animateKpi(element) {
    const card = element?.closest(
        ".dashboard-kpi",
    );

    if (!card) {
        return;
    }

    card.classList.remove(
        "dashboard-kpi--updating",
    );

    window.requestAnimationFrame(() => {
        card.classList.add(
            "dashboard-kpi--updating",
        );
    });

    window.setTimeout(() => {
        card.classList.remove(
            "dashboard-kpi--updating",
        );
    }, 260);
}



void refreshDashboard();
connectWebSocket();