"""
Infrastructure Image Utilities: Helper functions for image processing operations.

These utilities handle common image processing tasks like cropping and conversions.
"""

from __future__ import annotations

from typing import Optional, Tuple

import cv2
import numpy as np


def crop_and_convert_to_grayscale(
    image: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """
    Crop image and convert to grayscale for edge detection.

    Args:
        image: Input image array (RGB or grayscale)
        x1: Left x coordinate
        y1: Top y coordinate
        x2: Right x coordinate
        y2: Bottom y coordinate

    Returns:
        Tuple of (cropped_image, grayscale_image) or None if invalid crop
    """
    # Validate crop bounds
    if x2 <= x1 or y2 <= y1:
        return None

    # Crop image
    crop = image[y1:y2, x1:x2]

    # Convert to grayscale if needed
    if len(crop.shape) == 3:
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    else:
        gray = crop

    return crop, gray


def detect_edges(gray_image: np.ndarray, threshold1: int = 50, threshold2: int = 150) -> np.ndarray:
    """
    Detect edges in a grayscale image using Canny edge detection.

    Args:
        gray_image: Grayscale image
        threshold1: First threshold for the hysteresis procedure
        threshold2: Second threshold for the hysteresis procedure

    Returns:
        Edge detected image
    """
    return cv2.Canny(gray_image, threshold1, threshold2)


def safe_bbox_bounds(
    bbox: Tuple[int, int, int, int],
    image_width: int,
    image_height: int,
) -> Tuple[int, int, int, int]:
    """
    Ensure bounding box coordinates are within image bounds.

    Args:
        bbox: Bounding box (x1, y1, x2, y2)
        image_width: Image width
        image_height: Image height

    Returns:
        Validated bounding box coordinates
    """
    x1, y1, x2, y2 = bbox

    x1 = max(0, min(x1, image_width))
    y1 = max(0, min(y1, image_height))
    x2 = max(0, min(x2, image_width))
    y2 = max(0, min(y2, image_height))

    return x1, y1, x2, y2
