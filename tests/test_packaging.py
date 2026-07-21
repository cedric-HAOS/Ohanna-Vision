"""Tests for the Ohanna-Vision package configuration."""

from pathlib import Path


def test_pyproject_declares_console_entry_point() -> None:
    """The package must install the ohanna-vision command."""
    pyproject = Path("pyproject.toml").read_text(
        encoding="utf-8",
    )

    assert "[project.scripts]" in pyproject
    assert 'ohanna-vision = "ohanna_vision.main:main"' in pyproject


def test_pyproject_packages_root_static_resources() -> None:
    """Root frontend resources must be included in the package."""
    pyproject = Path("pyproject.toml").read_text(
        encoding="utf-8",
    )

    assert '"web/static/*.html"' in pyproject
    assert '"web/static/*.css"' in pyproject
    assert '"web/static/*.js"' in pyproject


def test_pyproject_packages_modular_stylesheets() -> None:
    """Modular frontend stylesheets must be included."""
    pyproject = Path("pyproject.toml").read_text(
        encoding="utf-8",
    )

    assert '"web/static/styles/*.css"' in pyproject


def test_package_installs_websocket_support() -> None:
    """The production server must include WebSocket support."""
    pyproject = Path("pyproject.toml").read_text(
        encoding="utf-8",
    )

    assert '"uvicorn[standard]"' in pyproject


def test_pyproject_packages_branding_assets() -> None:
    """Branding assets must be included in the package."""
    pyproject = Path("pyproject.toml").read_text(
        encoding="utf-8",
    )

    assert '"web/static/assets/favicons/*.ico"' in pyproject
    assert '"web/static/assets/favicons/*.svg"' in pyproject
    assert '"web/static/assets/favicons/*.png"' in pyproject
    assert '"web/static/*.webmanifest"' in pyproject


def test_static_branding_assets_exist() -> None:
    """Required branding assets must exist."""
    static_directory = Path(
        "src/ohanna_vision/web/static/assets/favicons"
    )

    required_files = [
        "favicon.ico",
        "favicon.svg",
        "apple-touch-icon.png",
        "icon-192.png",
        "icon-512.png",
    ]

    for filename in required_files:
        assert (static_directory / filename).is_file()


def test_index_declares_branding_assets() -> None:
    """The web interface must declare its branding assets."""
    index = Path("src/ohanna_vision/web/static/index.html").read_text(
        encoding="utf-8",
    )

    assert 'href="/ui/assets/favicons/favicon.ico"' in index
    assert 'href="/ui/assets/favicons/favicon.svg"' in index
    assert 'href="/ui/assets/favicons/apple-touch-icon.png"' in index
    assert 'href="/ui/site.webmanifest"' in index
    assert 'content="#18C5E8"' in index
