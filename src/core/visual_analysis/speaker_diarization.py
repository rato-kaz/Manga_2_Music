"""
Improved Speaker Diarization for Manga Speech Bubbles.

This module improves speaker assignment using:
1. Tail detection (most accurate)
2. Geometric heuristics (distance-based)
3. LLM-based context inference (fallback)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import cv2
import numpy as np
from PIL import Image

from src.infrastructure.image_utils import crop_and_convert_to_grayscale, detect_edges

BBOX = List[float]  # [x1, y1, x2, y2]


@dataclass
class SpeechBubble:
    """Represents a speech bubble."""

    bbox: BBOX
    text: str
    bubble_id: int
    panel_idx: int
    tail_points: Optional[List[Tuple[float, float]]] = None
    speaker_character_id: Optional[int] = None
    speaker_method: Optional[str] = None  # 'tail', 'geometric', 'llm', 'narrator'
    confidence: float = 0.0


@dataclass
class Character:
    """Represents a character in a panel."""

    bbox: BBOX
    character_id: int
    character_name: Optional[str] = None


def bbox_center(bbox: BBOX) -> Tuple[float, float]:
    """Get center point of bounding box."""
    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0


def euclidean_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def detect_speech_bubble_tail(
    image: np.ndarray,
    bubble_bbox: BBOX,
) -> Optional[List[Tuple[float, float]]]:
    """
    Detect the tail (pointer) of a speech bubble.

    The tail points toward the speaker character.

    Args:
        image: Panel image as numpy array
        bubble_bbox: Speech bubble bounding box [x1, y1, x2, y2]

    Returns:
        List of tail points [(x1, y1), (x2, y2), ...] or None
    """
    x1, y1, x2, y2 = [int(coord) for coord in bubble_bbox]
    h, w = image.shape[:2]

    # Crop bubble region with padding
    padding = 20
    crop_x1 = max(0, x1 - padding)
    crop_y1 = max(0, y1 - padding)
    crop_x2 = min(w, x2 + padding)
    crop_y2 = min(h, y2 + padding)

    # Use utility function for common operations
    result = crop_and_convert_to_grayscale(image, crop_x1, crop_y1, crop_x2, crop_y2)
    if result is None:
        return None

    crop, gray = result

    # Edge detection
    edges = detect_edges(gray)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Find the main bubble contour (largest)
    main_contour = max(contours, key=cv2.contourArea)

    # Approximate contour to reduce points
    epsilon = 0.02 * cv2.arcLength(main_contour, True)
    approx = cv2.approxPolyDP(main_contour, epsilon, True)

    # Find tail: look for protrusions from the main bubble
    # Tail is typically a small triangle or line extending outward
    bubble_center = (crop.shape[1] // 2, crop.shape[0] // 2)

    # Find points far from center (potential tail)
    tail_points: List[Tuple[float, float]] = []

    for point in approx:
        x, y = point[0]
        # Adjust coordinates back to original image space
        abs_x = x + crop_x1
        abs_y = y + crop_y1

        # Check if point is on the edge of the bubble
        dist_from_center = euclidean_distance((x, y), bubble_center)
        if dist_from_center > min(crop.shape[0], crop.shape[1]) * 0.3:
            tail_points.append((abs_x, abs_y))

    if len(tail_points) >= 2:
        # Sort by distance from bubble center
        bubble_center_abs = ((x1 + x2) / 2, (y1 + y2) / 2)
        tail_points.sort(key=lambda p: euclidean_distance(p, bubble_center_abs), reverse=True)
        return tail_points[:3]  # Return up to 3 tail points

    return None


def find_nearest_character_geometric(
    bubble_bbox: BBOX,
    characters: List[Character],
) -> Optional[int]:
    """
    Find nearest character to speech bubble using geometric distance.

    Args:
        bubble_bbox: Speech bubble bounding box
        characters: List of characters in the panel

    Returns:
        Character ID of nearest character, or None
    """
    if not characters:
        return None

    bubble_center = bbox_center(bubble_bbox)

    min_distance = float("inf")
    nearest_char_id = None

    for char in characters:
        char_center = bbox_center(char.bbox)
        distance = euclidean_distance(bubble_center, char_center)

        if distance < min_distance:
            min_distance = distance
            nearest_char_id = char.character_id

    return nearest_char_id


def find_character_by_tail_direction(
    tail_points: List[Tuple[float, float]],
    bubble_bbox: BBOX,
    characters: List[Character],
) -> Optional[int]:
    """
    Find character that the tail points to.

    Args:
        tail_points: List of tail point coordinates
        bubble_bbox: Speech bubble bounding box
        characters: List of characters in the panel

    Returns:
        Character ID that tail points to, or None
    """
    if not tail_points or not characters:
        return None

    # Calculate tail direction vector
    bubble_center = bbox_center(bubble_bbox)

    # Use the furthest tail point
    tail_point = tail_points[0]
    tail_vector = (tail_point[0] - bubble_center[0], tail_point[1] - bubble_center[1])

    # Normalize vector
    tail_length = np.sqrt(tail_vector[0] ** 2 + tail_vector[1] ** 2)
    if tail_length == 0:
        return None

    tail_vector = (tail_vector[0] / tail_length, tail_vector[1] / tail_length)

    # Find character in tail direction
    best_char_id = None
    best_score = -1.0

    for char in characters:
        char_center = bbox_center(char.bbox)

        # Vector from bubble to character
        char_vector = (char_center[0] - bubble_center[0], char_center[1] - bubble_center[1])
        char_length = np.sqrt(char_vector[0] ** 2 + char_vector[1] ** 2)

        if char_length == 0:
            continue

        char_vector = (char_vector[0] / char_length, char_vector[1] / char_length)

        # Dot product indicates alignment
        alignment = tail_vector[0] * char_vector[0] + tail_vector[1] * char_vector[1]

        # Also consider distance (closer is better)
        distance = euclidean_distance(bubble_center, char_center)
        distance_score = 1.0 / (1.0 + distance / 100.0)  # Normalize

        # Combined score
        score = alignment * 0.7 + distance_score * 0.3

        if score > best_score:
            best_score = score
            best_char_id = char.character_id

    return best_char_id


def infer_speaker_with_llm(
    bubble_text: str,
    panel_texts: List[str],
    characters: List[Character],
    conversation_history: List[Dict],
    llm_client=None,
) -> Optional[int]:
    """
    Infer speaker using LLM-based context analysis.

    Args:
        bubble_text: Text in the current speech bubble
        panel_texts: All texts in the panel
        characters: List of characters in the panel
        conversation_history: Previous conversation context
        llm_client: LLM client (OpenAI, etc.)

    Returns:
        Character ID of inferred speaker, or None
    """
    if not llm_client or not characters:
        return None

    # Build prompt
    character_names = [
        char.character_name or f"Character_{char.character_id}" for char in characters
    ]

    prompt = f"""You are analyzing a manga panel dialogue. Determine who is speaking.

Characters in the panel: {', '.join(character_names)}

Current dialogue: "{bubble_text}"

Previous context:
"""

    for i, hist in enumerate(conversation_history[-3:]):  # Last 3 exchanges
        prompt += f"- {hist.get('speaker', 'Unknown')}: {hist.get('text', '')}\n"

    prompt += f"""
Based on the dialogue content and context, which character is most likely speaking?
Respond with only the character name or "narrator" if it's narration.
"""

    try:
        # This is a placeholder - actual implementation depends on LLM client
        # For now, return None to indicate LLM inference is not available
        # In production, this would call the LLM API
        return None
    except Exception:
        return None


def assign_speaker_to_bubble(
    bubble: SpeechBubble,
    characters: List[Character],
    panel_image: Optional[np.ndarray] = None,
    conversation_history: Optional[List[Dict]] = None,
    llm_client=None,
) -> SpeechBubble:
    """
    Assign speaker to speech bubble using multiple methods.

    Priority:
    1. Tail detection (most accurate)
    2. Geometric distance (heuristic)
    3. LLM inference (context-based)
    4. Narrator (fallback)

    Args:
        bubble: Speech bubble to assign speaker to
        characters: List of characters in the panel
        panel_image: Panel image for tail detection
        conversation_history: Previous conversation context
        llm_client: LLM client for inference

    Returns:
        Updated speech bubble with speaker assignment
    """
    # Method 1: Tail detection (most accurate)
    if panel_image is not None:
        tail_points = detect_speech_bubble_tail(panel_image, bubble.bbox)
        if tail_points:
            bubble.tail_points = tail_points
            char_id = find_character_by_tail_direction(tail_points, bubble.bbox, characters)
            if char_id is not None:
                bubble.speaker_character_id = char_id
                bubble.speaker_method = "tail"
                bubble.confidence = 0.9
                return bubble

    # Method 2: Geometric distance
    char_id = find_nearest_character_geometric(bubble.bbox, characters)
    if char_id is not None:
        bubble.speaker_character_id = char_id
        bubble.speaker_method = "geometric"
        bubble.confidence = 0.6
        return bubble

    # Method 3: LLM inference (if available)
    if llm_client is not None and conversation_history is not None:
        panel_texts = [bubble.text]  # Simplified
        char_id = infer_speaker_with_llm(
            bubble.text,
            panel_texts,
            characters,
            conversation_history,
            llm_client,
        )
        if char_id is not None:
            bubble.speaker_character_id = char_id
            bubble.speaker_method = "llm"
            bubble.confidence = 0.7
            return bubble

    # Method 4: Narrator (fallback)
    bubble.speaker_character_id = None
    bubble.speaker_method = "narrator"
    bubble.confidence = 0.3
    return bubble


def diarize_speakers_in_panel(
    bubbles: List[SpeechBubble],
    characters: List[Character],
    panel_image: Optional[np.ndarray] = None,
    conversation_history: Optional[List[Dict]] = None,
    llm_client=None,
) -> List[SpeechBubble]:
    """
    Perform speaker diarization for all bubbles in a panel.

    Args:
        bubbles: List of speech bubbles
        characters: List of characters in the panel
        panel_image: Panel image for tail detection
        conversation_history: Previous conversation context
        llm_client: LLM client for inference

    Returns:
        List of bubbles with speaker assignments
    """
    updated_bubbles: List[SpeechBubble] = []

    for bubble in bubbles:
        updated_bubble = assign_speaker_to_bubble(
            bubble,
            characters,
            panel_image,
            conversation_history,
            llm_client,
        )
        updated_bubbles.append(updated_bubble)

        # Update conversation history
        if conversation_history is not None:
            conversation_history.append(
                {
                    "speaker": updated_bubble.speaker_character_id,
                    "text": updated_bubble.text,
                }
            )

    return updated_bubbles
