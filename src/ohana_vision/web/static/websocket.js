"use strict";

const DEFAULT_RECONNECT_DELAY_MS = 3000;

/**
 * Controls the Ohana-Vision realtime connection.
 */
export class WebSocketController {
    constructor({
        onMessage = () => {},
        reconnectDelayMs =
            DEFAULT_RECONNECT_DELAY_MS,
    } = {}) {
        this.onMessage = onMessage;
        this.reconnectDelayMs =
            reconnectDelayMs;

        this.socket = null;
        this.reconnectTimer = null;
        this.isStopped = false;

        this.elements = {
            status: document.querySelector(
                "#websocket-status",
            ),
            statusLabel: document.querySelector(
                "#websocket-status-label",
            ),
        };
    }

    /**
     * Start the realtime connection.
     */
    initialize() {
        this.isStopped = false;
        this.connect();
    }

    /**
     * Stop the connection and disable reconnection.
     */
    stop() {
        this.isStopped = true;

        if (this.reconnectTimer) {
            window.clearTimeout(
                this.reconnectTimer,
            );

            this.reconnectTimer = null;
        }

        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }

        this.setStatus(
            "offline",
            "Temps réel déconnecté",
        );
    }

    /**
     * Open a WebSocket connection.
     */
    connect() {
        if (this.isStopped) {
            return;
        }

        this.clearReconnectTimer();

        this.setStatus(
            "connecting",
            "Connexion temps réel…",
        );

        const socket = new WebSocket(
            this.websocketUrl(),
        );

        this.socket = socket;

        socket.addEventListener(
            "open",
            () => {
                this.handleOpen(socket);
            },
        );

        socket.addEventListener(
            "message",
            (event) => {
                this.handleMessage(
                    socket,
                    event,
                );
            },
        );

        socket.addEventListener(
            "close",
            () => {
                this.handleClose(socket);
            },
        );

        socket.addEventListener(
            "error",
            () => {
                this.handleError(socket);
            },
        );
    }

    /**
     * Return the backend WebSocket URL.
     *
     * @returns {string}
     */
    websocketUrl() {
        const protocol =
            window.location.protocol
            === "https:"
                ? "wss:"
                : "ws:";

        return (
            `${protocol}//`
            + `${window.location.host}/ws`
        );
    }

    handleOpen(socket) {
        if (socket !== this.socket) {
            return;
        }

        this.setStatus(
            "online",
            "Temps réel connecté",
        );
    }

    handleMessage(socket, event) {
        if (socket !== this.socket) {
            return;
        }

        let message;

        try {
            message = JSON.parse(
                event.data,
            );
        } catch {
            return;
        }

        if (
            !message
            || typeof message !== "object"
        ) {
            return;
        }

        if (message.type === "connected") {
            return;
        }

        this.onMessage(message);
    }

    handleClose(socket) {
        if (socket !== this.socket) {
            return;
        }

        this.socket = null;

        this.setStatus(
            "offline",
            "Temps réel déconnecté",
        );

        if (!this.isStopped) {
            this.scheduleReconnect();
        }
    }

    handleError(socket) {
        if (socket !== this.socket) {
            return;
        }

        socket.close();
    }

    scheduleReconnect() {
        this.clearReconnectTimer();

        this.reconnectTimer =
            window.setTimeout(
                () => {
                    this.reconnectTimer = null;
                    this.connect();
                },
                this.reconnectDelayMs,
            );
    }

    clearReconnectTimer() {
        if (!this.reconnectTimer) {
            return;
        }

        window.clearTimeout(
            this.reconnectTimer,
        );

        this.reconnectTimer = null;
    }

    setStatus(status, label) {
        if (this.elements.status) {
            this.elements.status.className =
                "connection-status "
                + (
                    "connection-status"
                    + `--${status}`
                );
        }

        if (this.elements.statusLabel) {
            this.elements
                .statusLabel
                .textContent = label;
        }
    }
}