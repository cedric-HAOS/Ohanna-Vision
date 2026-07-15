"use strict";

/**
 * Controls navigation between the main Ohanna-Vision views.
 */
export class NavigationController {
    constructor({
        navigationSelector = "[data-navigation-target]",
        viewSelector = "[data-view]",
        defaultView = "overview",
    } = {}) {
        this.navigationSelector = navigationSelector;
        this.viewSelector = viewSelector;
        this.defaultView = defaultView;

        this.navigationItems = [];
        this.views = [];
        this.activeView = null;

        this.handleHashChange = this.handleHashChange.bind(this);
    }

    initialize() {
        this.navigationItems = Array.from(
            document.querySelectorAll(this.navigationSelector),
        );

        this.views = Array.from(
            document.querySelectorAll(this.viewSelector),
        );

        this.navigationItems.forEach((navigationItem) => {
            navigationItem.addEventListener("click", () => {
                const target =
                    navigationItem.dataset.navigationTarget;

                this.activate(target);
            });
        });

        window.addEventListener(
            "hashchange",
            this.handleHashChange,
        );

        this.activate(
            this.resolveInitialView(),
            {
                updateHash: false,
            },
        );
    }

    activate(
        viewName,
        {
            updateHash = true,
        } = {},
    ) {
        if (!viewName || !this.hasView(viewName)) {
            return false;
        }

        this.views.forEach((view) => {
            const isActive =
                view.dataset.view === viewName;

            view.hidden = !isActive;
            view.classList.toggle(
                "is-active",
                isActive,
            );
        });

        this.navigationItems.forEach((navigationItem) => {
            const isActive =
                navigationItem.dataset.navigationTarget
                === viewName;

            navigationItem.classList.toggle(
                "is-active",
                isActive,
            );

            if (isActive) {
                navigationItem.setAttribute(
                    "aria-current",
                    "page",
                );
            } else {
                navigationItem.removeAttribute(
                    "aria-current",
                );
            }
        });

        this.activeView = viewName;

        if (updateHash) {
            this.updateLocationHash(viewName);
        }

        this.dispatchNavigationChanged(viewName);

        return true;
    }

    hasView(viewName) {
        return this.views.some(
            (view) => view.dataset.view === viewName,
        );
    }

    resolveInitialView() {
        const hashView =
            window.location.hash.replace(/^#/, "");

        if (hashView && this.hasView(hashView)) {
            return hashView;
        }

        if (this.hasView(this.defaultView)) {
            return this.defaultView;
        }

        return this.views[0]?.dataset.view ?? null;
    }

    handleHashChange() {
        const requestedView =
            window.location.hash.replace(/^#/, "");

        if (!requestedView) {
            this.activate(
                this.defaultView,
                {
                    updateHash: false,
                },
            );

            return;
        }

        if (!this.hasView(requestedView)) {
            this.activate(this.defaultView);
            return;
        }

        this.activate(
            requestedView,
            {
                updateHash: false,
            },
        );
    }

    updateLocationHash(viewName) {
        if (
            window.location.hash
            === `#${viewName}`
        ) {
            return;
        }

        window.location.hash = viewName;
    }

    dispatchNavigationChanged(viewName) {
        document.dispatchEvent(
            new CustomEvent(
                "ohanna:navigation-changed",
                {
                    detail: {
                        view: viewName,
                    },
                },
            ),
        );
    }
}