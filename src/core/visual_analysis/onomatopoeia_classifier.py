"""
Onomatopoeia Classification Module for Manga.

Classifies visual onomatopoeia (sound effects) into Giongo (actual sounds)
and Gitaigo (states/feelings), and maps them to SFX keywords.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

BBOX = List[float]  # [x1, y1, x2, y2]


@dataclass
class OnomatopoeiaDetection:
    """Represents a detected onomatopoeia."""

    bbox: BBOX
    visual_form: str  # Katakana characters or description
    type: str  # 'giongo' (actual sound) or 'gitaigo' (state)
    audio_keywords: List[str]  # Mapped audio keywords for SFX generation
    confidence: float


# Onomatopoeia database mapping
# This should be expanded with a comprehensive database
ONOMATOPOEIA_DATABASE: Dict[str, Dict[str, any]] = {
    # Giongo (actual sounds)
    "ドン": {"type": "giongo", "keywords": ["explosion", "heavy_impact", "boom", "thud"]},
    "ゴゴゴ": {"type": "giongo", "keywords": ["rumble", "earthquake", "low_frequency", "tension"]},
    "バン": {"type": "giongo", "keywords": ["gunshot", "bang", "pop"]},
    "ガチャ": {"type": "giongo", "keywords": ["click", "mechanical", "lock"]},
    "ドキドキ": {"type": "giongo", "keywords": ["heartbeat", "pulse", "nervous"]},
    "ガラガラ": {"type": "giongo", "keywords": ["rattle", "shake", "noise"]},
    "ピカ": {"type": "giongo", "keywords": ["flash", "spark", "light"]},
    "ザーザー": {"type": "giongo", "keywords": ["rain", "pouring", "water"]},
    "ワンワン": {"type": "giongo", "keywords": ["dog_bark", "barking"]},
    "ニャー": {"type": "giongo", "keywords": ["cat_meow", "meow"]},
    # Gitaigo (states/feelings)
    "シーン": {"type": "gitaigo", "keywords": ["silence", "quiet", "stillness"]},
    "キラキラ": {"type": "gitaigo", "keywords": ["sparkle", "shine", "glitter"]},
    "ドキドキ": {"type": "gitaigo", "keywords": ["nervous", "excited", "heartbeat"]},
    "ワクワク": {"type": "gitaigo", "keywords": ["excited", "anticipation", "thrilled"]},
    "イライラ": {"type": "gitaigo", "keywords": ["irritated", "frustrated", "annoyed"]},
    "ビクビク": {"type": "gitaigo", "keywords": ["trembling", "shaking", "nervous"]},
    "フワフワ": {"type": "gitaigo", "keywords": ["soft", "fluffy", "light"]},
    "キラッ": {"type": "gitaigo", "keywords": ["sparkle", "glint", "shine"]},
}


def detect_text_regions(image: np.ndarray) -> List[BBOX]:
    """
    Detect text regions in image (potential onomatopoeia).

    Uses simple contour detection for text-like regions.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image

    # Threshold to get text regions
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    text_regions: List[BBOX] = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        # Filter by aspect ratio and size (text-like regions)
        aspect_ratio = w / h if h > 0 else 0
        area = w * h

        # Onomatopoeia are often larger and more stylized than regular text
        if 0.3 < aspect_ratio < 10 and area > 100:
            text_regions.append([float(x), float(y), float(x + w), float(y + h)])

    return text_regions


def classify_onomatopoeia_type(
    visual_form: str,
    bbox: BBOX,
    image: np.ndarray,
) -> Tuple[str, List[str], float]:
    """
    Classify onomatopoeia type and map to audio keywords.

    Args:
        visual_form: Detected text/visual form
        bbox: Bounding box of onomatopoeia
        image: Image region

    Returns:
        Tuple of (type, audio_keywords, confidence)
    """
    # Check database first
    if visual_form in ONOMATOPOEIA_DATABASE:
        entry = ONOMATOPOEIA_DATABASE[visual_form]
        return entry["type"], entry["keywords"], 0.9

    # Heuristic classification based on visual characteristics
    x1, y1, x2, y2 = bbox
    width = x2 - x1
    height = y2 - y1

    # Large, bold text often indicates Giongo (sound effects)
    # Small, subtle text often indicates Gitaigo (states)

    # Analyze visual style
    crop = image[int(y1) : int(y2), int(x1) : int(x2)]
    if len(crop.shape) == 3:
        gray_crop = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    else:
        gray_crop = crop

    # Calculate "boldness" (stroke width)
    edges = cv2.Canny(gray_crop, 50, 150)
    edge_density = np.sum(edges > 0) / (width * height) if width * height > 0 else 0

    # Large, bold = Giongo
    if width > 100 or height > 50 or edge_density > 0.1:
        # Common Giongo patterns
        keywords = ["impact", "sound_effect", "action"]
        return "giongo", keywords, 0.6
    else:
        # Common Gitaigo patterns
        keywords = ["ambient", "atmosphere", "mood"]
        return "gitaigo", keywords, 0.6


def detect_onomatopoeia_in_panel(
    panel_image: np.ndarray,
    exclude_speech_bubbles: Optional[List[BBOX]] = None,
) -> List[OnomatopoeiaDetection]:
    """
    Detect and classify onomatopoeia in a panel.

    Args:
        panel_image: Panel image as numpy array
        exclude_speech_bubbles: List of speech bubble bboxes to exclude

    Returns:
        List of detected onomatopoeia
    """
    if exclude_speech_bubbles is None:
        exclude_speech_bubbles = []

    # Detect text regions
    text_regions = detect_text_regions(panel_image)

    detections: List[OnomatopoeiaDetection] = []

    for bbox in text_regions:
        # Skip if overlaps with speech bubble
        is_speech_bubble = False
        for speech_bbox in exclude_speech_bubbles:
            if bbox_overlap(bbox, speech_bbox) > 0.3 * bbox_area(bbox):
                is_speech_bubble = True
                break

        if is_speech_bubble:
            continue

        # Extract visual form (simplified - would need OCR in production)
        # For now, use placeholder
        visual_form = "detected_text"  # Would be OCR result

        # Classify
        type, keywords, confidence = classify_onomatopoeia_type(
            visual_form,
            bbox,
            panel_image,
        )

        detections.append(
            OnomatopoeiaDetection(
                bbox=bbox,
                visual_form=visual_form,
                type=type,
                audio_keywords=keywords,
                confidence=confidence,
            )
        )

    return detections


def load_onomatopoeia_database(db_path: Optional[Path] = None) -> Dict[str, Dict[str, any]]:
    """
    Load onomatopoeia database from JSON file.

    Args:
        db_path: Path to JSON database file

    Returns:
        Database dictionary
    """
    if db_path is None:
        return ONOMATOPOEIA_DATABASE

    if db_path.exists():
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)

    return ONOMATOPOEIA_DATABASE


def save_onomatopoeia_database(
    database: Dict[str, Dict[str, any]],
    db_path: Path,
) -> None:
    """Save onomatopoeia database to JSON file."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=2, ensure_ascii=False)


def bbox_area(bbox: BBOX) -> float:
    """Calculate area of bounding box."""
    x1, y1, x2, y2 = bbox
    return max(0, (x2 - x1) * (y2 - y1))


def bbox_overlap(a: BBOX, b: BBOX) -> float:
    """Calculate overlap area between two bounding boxes."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
        return 0.0

    return (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
