"""
Color Psychology Analysis Engine

This module provides utilities to extract dominant colour palettes from images and
associate those palettes with psychological effects based on established colour-
psychology research.

Key features:
1. Palette extraction using k-means clustering (via scikit-learn).
2. Simple colour→effect lookup database (can be extended from CSV / DB later).
3. Basic colour-harmony checks (complementary, analogous, triadic, etc.).

The implementation is deliberately lightweight but fully unit-testable so that we
can iterate quickly as the broader VividWalls AI Agent matures.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Any

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

# ---------------------------------------------------------------------------
# Logging set-up
# ---------------------------------------------------------------------------
# NOTE: In the JavaScript side of this project we use Winston.  For the Python
#       modules we mimic a similar API style using the built-in `logging` lib
#       so that log output remains consistent across the stack.
# ---------------------------------------------------------------------------

_LOG_FORMAT = "% (asctime)s | %(levelname)8s | ColorPsychology | %(message)s"
logging.basicConfig(format=_LOG_FORMAT, level=logging.INFO)
logger = logging.getLogger("vividwalls.color_psychology")

# ---------------------------------------------------------------------------
# Helper types
# ---------------------------------------------------------------------------

ColourRGB = Tuple[int, int, int]  # 0-255 each channel
Palette = List[ColourRGB]


@dataclass(slots=True)
class ColourEffect:
    """Dataclass representing a psychological effect for a given colour."""

    name: str            # e.g. "calming"
    description: str      # detailed text


# ---------------------------------------------------------------------------
# Static colour-psychology database (VERY small initial seed — extend later)
# ---------------------------------------------------------------------------

_COLOUR_EFFECTS: Dict[str, ColourEffect] = {
    "red": ColourEffect(
        name="energizing",
        description="Red is associated with energy, passion and attention-grabbing"
    ),
    "orange": ColourEffect(
        name="playful",
        description="Orange conveys enthusiasm, creativity and warmth"
    ),
    "yellow": ColourEffect(
        name="uplifting",
        description="Yellow evokes happiness and optimism"
    ),
    "green": ColourEffect(
        name="natural",
        description="Green symbolises nature, growth and balance"
    ),
    "blue": ColourEffect(
        name="calming",
        description="Blue promotes calmness, trust and serenity"
    ),
    "purple": ColourEffect(
        name="mysterious",
        description="Purple suggests luxury, spirituality and mystery"
    ),
    "pink": ColourEffect(
        name="romantic",
        description="Pink conveys softness, compassion and romance"
    ),
    "brown": ColourEffect(
        name="grounded",
        description="Brown represents stability, reliability and comfort"
    ),
    "black": ColourEffect(
        name="dramatic",
        description="Black is powerful, elegant and sophisticated"
    ),
    "white": ColourEffect(
        name="pure",
        description="White symbolises purity, cleanliness and simplicity"
    ),
}


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def _rgb_to_hsv(colour: ColourRGB) -> Tuple[float, float, float]:
    """Convert RGB (0-255) to HSV (0-1 floats)."""
    r, g, b = [c / 255.0 for c in colour]
    mx, mn = max(r, g, b), min(r, g, b)
    diff = mx - mn
    if diff == 0:
        h = 0.0
    elif mx == r:
        h = (60 * ((g - b) / diff) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    else:
        h = (60 * ((r - g) / diff) + 240) % 360
    s = 0.0 if mx == 0 else diff / mx
    v = mx
    return h, s, v


def _closest_colour_name(colour: ColourRGB) -> str:
    """Return a simple colour name for an RGB triple (coarse mapping)."""
    # Simplistic mapping by hue angle only – good enough for initial prototype.
    h, _, _ = _rgb_to_hsv(colour)
    if h < 15 or h >= 345:
        return "red"
    if 15 <= h < 45:
        return "orange"
    if 45 <= h < 75:
        return "yellow"
    if 75 <= h < 165:
        return "green"
    if 165 <= h < 255:
        return "blue"
    if 255 <= h < 285:
        return "purple"
    if 285 <= h < 330:
        return "pink"
    return "red"  # default fallback


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class ColorPsychologyAnalyzer:
    """Extracts colour information from images & maps to psychological effects."""

    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        logger.debug("Initialized ColorPsychologyAnalyzer with %s clusters", n_clusters)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_image(self, image_path: str | Path) -> Dict[str, Any]:
        """End-to-end helper. Returns palette, harmony and psychological summary.

        Parameters
        ----------
        image_path : str | Path
            Path to the image to analyze.

        Returns
        -------
        dict
            {
              "palette": [(r, g, b), ...],
              "harmony": "complementary" | "analogous" | ... | None,
              "effects": [ColourEffect, ...]
            }
        """
        logger.info("Analyzing image %s", image_path)
        palette = self.extract_palette(image_path)
        harmony = self.detect_harmony(palette)
        effects = self.map_palette_to_effects(palette)
        return {
            "palette": palette,
            "harmony": harmony,
            "effects": effects,
        }

    # ------------------------------------------------------------------
    # Palette extraction
    # ------------------------------------------------------------------

    def extract_palette(self, image_path: str | Path) -> Palette:
        """Return the dominant colours in the image using k-means clustering."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(path)
        img = Image.open(path).convert("RGB")
        img_array = np.array(img) / 255.0  # normalise 0-1 for clustering
        flat_pixels = img_array.reshape(-1, 3)
        logger.debug("Running k-means on %s pixels", len(flat_pixels))
        kmeans = KMeans(n_clusters=self.n_clusters, n_init="auto", random_state=self.random_state)
        kmeans.fit(flat_pixels)
        centroids = (kmeans.cluster_centers_ * 255).astype(int)
        palette = [tuple(map(int, c)) for c in centroids]
        logger.info("Extracted palette: %s", palette)
        return palette

    # ------------------------------------------------------------------
    # Harmony detection (simplified)
    # ------------------------------------------------------------------

    def detect_harmony(self, palette: Palette) -> str | None:
        """Detect a crude colour harmony type from first two colours."""
        if len(palette) < 2:
            return None
        # Compare hue difference of first two colours
        h1, _, _ = _rgb_to_hsv(palette[0])
        h2, _, _ = _rgb_to_hsv(palette[1])
        diff = abs(h1 - h2)
        diff = diff if diff <= 180 else 360 - diff
        logger.debug("Hue diff between first two colours: %s", diff)
        if math.isclose(diff, 180, abs_tol=15):
            return "complementary"
        if diff <= 30:
            return "analogous"
        if math.isclose(diff, 120, abs_tol=15):
            return "triadic"
        return None

    # ------------------------------------------------------------------
    # Psychology mapping
    # ------------------------------------------------------------------

    def map_palette_to_effects(self, palette: Palette) -> List[ColourEffect]:
        """Translate palette colours to associated psychological effects."""
        effects: List[ColourEffect] = []
        seen_names = set()
        for colour in palette:
            name = _closest_colour_name(colour)
            if name in _COLOUR_EFFECTS and name not in seen_names:
                effects.append(_COLOUR_EFFECTS[name])
                seen_names.add(name)
        logger.debug("Mapped palette to effects: %s", [e.name for e in effects])
        return effects 