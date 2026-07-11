"use strict";

const API = {
    runtime: "/api/runtime",
    observations: "/api/observations",
    timeline: "/api/timeline",
};

const MAX_OBSERVATIONS = 50;
const WEBSOCKET_RECONNECT_DELAY_MS = 3000;

const elements = {
    refreshButton: document.querySelector("#refresh-button"),
    lastRefresh: document.querySelector("#last-refresh"),

    websocketStatus: document.querySelector("#websocket-status"),
    websocketStatusLabel: document.querySelector(
        "#websocket-status-label",
    ),

    runtimeError: document.querySelector("#runtime-error"),
    runtimeState: document.querySelector("#runtime-state"),
    observationsStored: document.querySelector(
        "#observations-stored",
    ),
    serviceTimelines: document.querySelector(
        "#service-timelines",
    ),
    nodeTimelines: document.querySelector("#node-timelines"),

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

    timelineError: document.querySelector("#timeline-error"),
    timelineContent: document.querySelector("#timeline-content"),
    timelineGeneratedAt: document.querySelector(
        "#timeline-generated-at",
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
};

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

    return `${Number(value).toFixed(2)} ms`;
}

function statusClass(status) {
    const normalized = String(status ?? "unknown").toLowerCase();

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

function renderRuntime(runtime) {
    const statistics = runtime.statistics ?? {};

    elements.runtimeState.innerHTML = statusBadge(runtime.state);
    elements.observationsStored.textContent =
        runtime.observations_stored ?? 0;
    elements.serviceTimelines.textContent =
        runtime.service_timelines ?? 0;
    elements.nodeTimelines.textContent =
        runtime.node_timelines ?? 0;

    elements.observationsReceived.textContent =
        statistics.observations_received ?? 0;
    elements.observationsAccepted.textContent =
        statistics.observations_accepted ?? 0;
    elements.observationsRejected.textContent =
        statistics.observations_rejected ?? 0;
    elements.runtimeErrors.textContent =
        statistics.errors ?? 0;

    hideError(elements.runtimeError);
}

function renderObservations(observations) {
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
        `${observations.length} observation`
        + (observations.length > 1 ? "s" : "");

    if (visibleObservations.length === 0) {
        elements.observationsBody.innerHTML = `
            <tr>
                <td class="empty-table" colspan="6">
                    Aucune observation enregistrée.
                </td>
            </tr>
        `;

        hideError(elements.observationsError);
        return;
    }

    elements.observationsBody.innerHTML = visibleObservations
        .map((observation) => {
            return `
                <tr>
                    <td>
                        ${escapeHtml(
                            formatDate(observation.observed_at),
                        )}
                    </td>
                    <td>${escapeHtml(observation.node_id)}</td>
                    <td>${escapeHtml(observation.service_id)}</td>
                    <td>
                        ${escapeHtml(observation.capability_id)}
                    </td>
                    <td>${statusBadge(observation.status)}</td>
                    <td>
                        ${escapeHtml(
                            formatLatency(observation.latency_ms),
                        )}
                    </td>
                </tr>
            `;
        })
        .join("");

    hideError(elements.observationsError);
}

function extractCurrentStatus(periods) {
    if (!Array.isArray(periods) || periods.length === 0) {
        return "unknown";
    }

    return periods[periods.length - 1].status ?? "unknown";
}

function renderCapability(capability) {
    const status = extractCurrentStatus(capability.periods);

    return `
        <li class="capability-item">
            ${escapeHtml(capability.capability_id)}
            ${statusBadge(status)}
        </li>
    `;
}

function renderService(service) {
    const status = extractCurrentStatus(service.periods);
    const capabilities = service.capabilities ?? [];

    return `
        <article class="service-card">
            <div class="service-card__header">
                <h4>${escapeHtml(service.service_id)}</h4>
                ${statusBadge(status)}
            </div>

            ${
                capabilities.length > 0
                    ? `
                        <ul class="capability-list">
                            ${capabilities
                                .map(renderCapability)
                                .join("")}
                        </ul>
                    `
                    : `
                        <p class="empty-state">
                            Aucune capacité.
                        </p>
                    `
            }
        </article>
    `;
}

function renderNode(node) {
    const status = extractCurrentStatus(node.periods);
    const services = node.services ?? [];

    return `
        <article class="node-card">
            <div class="node-card__header">
                <h3>${escapeHtml(node.node_id)}</h3>
                ${statusBadge(status)}
            </div>

            <div class="service-grid">
                ${
                    services.length > 0
                        ? services.map(renderService).join("")
                        : `
                            <p class="empty-state">
                                Aucun service.
                            </p>
                        `
                }
            </div>
        </article>
    `;
}

function renderTimeline(timeline) {
    const nodes = timeline.nodes ?? [];

    if (nodes.length === 0) {
        elements.timelineContent.innerHTML = `
            <p class="empty-state">
                Aucune timeline disponible.
            </p>
        `;
    } else {
        elements.timelineContent.innerHTML =
            nodes.map(renderNode).join("");
    }

    elements.timelineGeneratedAt.textContent =
        `Actualisée ${formatDate(new Date().toISOString())}`;

    hideError(elements.timelineError);
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
        const observations = await fetchJson(API.observations);
        renderObservations(observations);
    } catch (error) {
        showError(
            elements.observationsError,
            `Observations indisponibles : ${error.message}`,
        );
    }
}

async function loadTimeline() {
    try {
        const timeline = await fetchJson(API.timeline);
        renderTimeline(timeline);
    } catch (error) {
        showError(
            elements.timelineError,
            `Timeline indisponible : ${error.message}`,
        );
    }
}

async function refreshDashboard() {
    elements.refreshButton.disabled = true;

    await Promise.allSettled([
        loadRuntime(),
        loadObservations(),
        loadTimeline(),
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
        window.location.protocol === "https:" ? "wss:" : "ws:";

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

        if (message.type === "connected") {
            return;
        }

        if (
            message.type === "observation.received"
            || message.type === "runtime.updated"
            || message.type === "timeline.updated"
        ) {
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

void refreshDashboard();
connectWebSocket();