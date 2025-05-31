"""Unit tests for ColorPsychologyAnalyzer.

These tests use small synthetic colour arrays so we don't need actual image
assets checked into the repository.  Real integration tests with artwork
images will be added later in the E2E test suite.
"""

from pathlib import Path

import numpy as np
from PIL import Image

from vivid_mas.ai_system.color_psychology import (
    ColorPsychologyAnalyzer,
    _closest_colour_name,  # pylint: disable=protected-access
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_solid_image(colour_rgb: tuple[int, int, int], path: Path, size: int = 32) -> None:
    """Create a temporary solid-colour PNG file for testing."""
    img_array = np.full((size, size, 3), colour_rgb, dtype=np.uint8)
    img = Image.fromarray(img_array, mode="RGB")
    img.save(path)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_palette_extraction_and_effect_mapping(tmp_path: Path) -> None:
    """Colour palette extraction should identify dominant colour and map effect."""
    red_png = tmp_path / "red.png"
    _create_solid_image((255, 0, 0), red_png)

    analyzer = ColorPsychologyAnalyzer(n_clusters=3)
    result = analyzer.analyze_image(red_png)

    # Palette should contain red-ish tones
    palette = result["palette"]
    assert any(r > 200 and g < 50 and b < 50 for r, g, b in palette)

    # Effect list should include energizing (mapped from red)
    effect_names = [e.name for e in result["effects"]]
    assert "energizing" in effect_names


def test_closest_colour_name() -> None:
    """Internal helper should map RGB to expected simple names."""
    assert _closest_colour_name((250, 0, 0)) == "red"
    assert _closest_colour_name((0, 250, 0)) == "green"
    assert _closest_colour_name((0, 0, 250)) == "blue" 