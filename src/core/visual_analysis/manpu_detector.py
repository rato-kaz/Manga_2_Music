"""
Manpu (Manga Emotion Symbols) Detection Module.

Detects visual emotion symbols in manga panels and maps them to emotion tags.
"""

from __future__ import annotations

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import cv2

BBOX = List[float]  # [x1, y1, x2, y2]


@dataclass
class ManpuDetection:
    """Represents a detected manpu symbol."""
    bbox: BBOX
    manpu_type: str  # 'vein', 'sweat', 'sparkles', 'steam', 'vertical_lines', etc.
    confidence: float
    emotion_tags: List[str]  # Mapped emotion tags


# Manpu type to emotion mapping
MANPU_EMOTION_MAP: Dict[str, List[str]] = {
    'vein': ['anger', 'irritation', 'tense', 'frustrated'],
    'sweat': ['nervous', 'awkward', 'comedy', 'anxious', 'embarrassed'],
    'sparkles': ['joy', 'admiration', 'dreamy', 'excited', 'happy'],
    'steam': ['rage', 'exertion', 'hot', 'angry', 'furious'],
    'vertical_lines': ['shock', 'surprise', 'tension', 'dramatic'],
    'cross_mark': ['anger', 'frustration', 'annoyed'],
    'lightbulb': ['idea', 'realization', 'inspiration'],
    'question_mark': ['confusion', 'curiosity', 'wondering'],
    'exclamation_mark': ['surprise', 'shock', 'alarm'],
    'tears': ['sad', 'crying', 'emotional'],
    'heart': ['love', 'affection', 'romance'],
    'z': ['sleep', 'tired', 'exhausted'],
}


def detect_vein_marks(image: np.ndarray, bbox: BBOX) -> List[ManpuDetection]:
    """
    Detect vein marks (💢) - typically vertical lines on forehead.
    
    Vein marks are usually dark vertical lines in the upper part of faces.
    """
    x1, y1, x2, y2 = [int(coord) for coord in bbox]
    h, w = image.shape[:2]
    
    # Crop region (usually upper part of face)
    crop_x1 = max(0, x1)
    crop_y1 = max(0, y1)
    crop_x2 = min(w, x2)
    crop_y2 = min(h, y1 + (y2 - y1) * 0.4)  # Upper 40% of bbox
    
    if crop_x2 <= crop_x1 or crop_y2 <= crop_y1:
        return []
    
    crop = image[crop_y1:crop_y2, crop_x1:crop_x2]
    
    # Convert to grayscale
    if len(crop.shape) == 3:
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    else:
        gray = crop
    
    # Detect vertical lines
    edges = cv2.Canny(gray, 50, 150)
    
    # HoughLines for vertical lines
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=20, minLineLength=10, maxLineGap=5)
    
    detections: List[ManpuDetection] = []
    
    if lines is not None:
        vertical_lines = []
        for line in lines:
            x1_l, y1_l, x2_l, y2_l = line[0]
            # Check if line is roughly vertical
            if abs(x2_l - x1_l) < 5:  # Vertical line
                vertical_lines.append(line[0])
        
        if len(vertical_lines) >= 2:  # Multiple vertical lines = vein marks
            # Calculate bounding box of all lines
            all_x = [x1 for x1, y1, x2, y2 in vertical_lines] + [x2 for x1, y1, x2, y2 in vertical_lines]
            all_y = [y1 for x1, y1, x2, y2 in vertical_lines] + [y2 for x1, y1, x2, y2 in vertical_lines]
            
            if all_x and all_y:
                manpu_bbox = [
                    crop_x1 + min(all_x),
                    crop_y1 + min(all_y),
                    crop_x1 + max(all_x),
                    crop_y1 + max(all_y),
                ]
                detections.append(ManpuDetection(
                    bbox=manpu_bbox,
                    manpu_type='vein',
                    confidence=0.7,
                    emotion_tags=MANPU_EMOTION_MAP['vein'],
                ))
    
    return detections


def detect_sweat_drops(image: np.ndarray, bbox: BBOX) -> List[ManpuDetection]:
    """
    Detect sweat drops (💧) - typically circular/teardrop shapes.
    """
    x1, y1, x2, y2 = [int(coord) for coord in bbox]
    h, w = image.shape[:2]
    
    crop_x1 = max(0, x1)
    crop_y1 = max(0, y1)
    crop_x2 = min(w, x2)
    crop_y2 = min(h, y2)
    
    if crop_x2 <= crop_x1 or crop_y2 <= crop_y1:
        return []
    
    crop = image[crop_y1:crop_y2, crop_x1:crop_x2]
    
    if len(crop.shape) == 3:
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    else:
        gray = crop
    
    # Detect circles (sweat drops are often circular)
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=50,
        param2=30,
        minRadius=5,
        maxRadius=30,
    )
    
    detections: List[ManpuDetection] = []
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            manpu_bbox = [
                crop_x1 + x - r,
                crop_y1 + y - r,
                crop_x1 + x + r,
                crop_y1 + y + r,
            ]
            detections.append(ManpuDetection(
                bbox=manpu_bbox,
                manpu_type='sweat',
                confidence=0.6,
                emotion_tags=MANPU_EMOTION_MAP['sweat'],
            ))
    
    return detections


def detect_sparkles(image: np.ndarray, bbox: BBOX) -> List[ManpuDetection]:
    """
    Detect sparkles (✨) - typically star-like or cross patterns.
    """
    x1, y1, x2, y2 = [int(coord) for coord in bbox]
    h, w = image.shape[:2]
    
    crop_x1 = max(0, x1)
    crop_y1 = max(0, y1)
    crop_x2 = min(w, x2)
    crop_y2 = min(h, y2)
    
    if crop_x2 <= crop_x1 or crop_y2 <= crop_y1:
        return []
    
    crop = image[crop_y1:crop_y2, crop_x1:crop_x2]
    
    if len(crop.shape) == 3:
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    else:
        gray = crop
    
    # Sparkles are bright spots with cross patterns
    # Use corner detection
    corners = cv2.goodFeaturesToTrack(gray, maxCorners=50, qualityLevel=0.01, minDistance=10)
    
    detections: List[ManpuDetection] = []
    
    if corners is not None:
        # Group nearby corners (sparkles often have multiple points)
        for corner in corners:
            x, y = corner.ravel()
            manpu_bbox = [
                crop_x1 + int(x) - 10,
                crop_y1 + int(y) - 10,
                crop_x1 + int(x) + 10,
                crop_y1 + int(y) + 10,
            ]
            detections.append(ManpuDetection(
                bbox=manpu_bbox,
                manpu_type='sparkles',
                confidence=0.5,
                emotion_tags=MANPU_EMOTION_MAP['sparkles'],
            ))
    
    return detections


def detect_steam(image: np.ndarray, bbox: BBOX) -> List[ManpuDetection]:
    """
    Detect steam/puff marks (💨) - typically wavy lines.
    """
    x1, y1, x2, y2 = [int(coord) for coord in bbox]
    h, w = image.shape[:2]
    
    crop_x1 = max(0, x1)
    crop_y1 = max(0, y1)
    crop_x2 = min(w, x2)
    crop_y2 = min(h, y2)
    
    if crop_x2 <= crop_x1 or crop_y2 <= crop_y1:
        return []
    
    crop = image[crop_y1:crop_y2, crop_x1:crop_x2]
    
    if len(crop.shape) == 3:
        gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY)
    else:
        gray = crop
    
    # Detect wavy lines (steam)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=15, minLineLength=10, maxLineGap=5)
    
    detections: List[ManpuDetection] = []
    
    if lines is not None:
        wavy_lines = []
        for line in lines:
            x1_l, y1_l, x2_l, y2_l = line[0]
            # Wavy lines have varying angles
            angle = np.arctan2(y2_l - y1_l, x2_l - x1_l) * 180 / np.pi
            if -45 < angle < 45:  # Roughly horizontal
                wavy_lines.append(line[0])
        
        if len(wavy_lines) >= 3:  # Multiple wavy lines = steam
            all_x = [x1 for x1, y1, x2, y2 in wavy_lines] + [x2 for x1, y1, x2, y2 in wavy_lines]
            all_y = [y1 for x1, y1, x2, y2 in wavy_lines] + [y2 for x1, y1, x2, y2 in wavy_lines]
            
            if all_x and all_y:
                manpu_bbox = [
                    crop_x1 + min(all_x),
                    crop_y1 + min(all_y),
                    crop_x1 + max(all_x),
                    crop_y1 + max(all_y),
                ]
                detections.append(ManpuDetection(
                    bbox=manpu_bbox,
                    manpu_type='steam',
                    confidence=0.6,
                    emotion_tags=MANPU_EMOTION_MAP['steam'],
                ))
    
    return detections


def detect_manpu_in_panel(
    panel_image: np.ndarray,
    character_bboxes: List[BBOX],
) -> List[ManpuDetection]:
    """
    Detect all manpu symbols in a panel.
    
    Args:
        panel_image: Panel image as numpy array
        character_bboxes: List of character bounding boxes
    
    Returns:
        List of detected manpu symbols
    """
    all_detections: List[ManpuDetection] = []
    
    # Detect manpu around each character
    for char_bbox in character_bboxes:
        # Vein marks
        all_detections.extend(detect_vein_marks(panel_image, char_bbox))
        
        # Sweat drops
        all_detections.extend(detect_sweat_drops(panel_image, char_bbox))
        
        # Sparkles
        all_detections.extend(detect_sparkles(panel_image, char_bbox))
        
        # Steam
        all_detections.extend(detect_steam(panel_image, char_bbox))
    
    # Remove duplicates (overlapping detections)
    filtered_detections: List[ManpuDetection] = []
    for det in all_detections:
        is_duplicate = False
        for existing in filtered_detections:
            # Check overlap
            overlap = bbox_overlap(det.bbox, existing.bbox)
            area_det = bbox_area(det.bbox)
            area_existing = bbox_area(existing.bbox)
            
            if overlap > 0.5 * min(area_det, area_existing):
                is_duplicate = True
                # Keep the one with higher confidence
                if det.confidence > existing.confidence:
                    filtered_detections.remove(existing)
                    filtered_detections.append(det)
                break
        
        if not is_duplicate:
            filtered_detections.append(det)
    
    return filtered_detections


def aggregate_emotions(manpu_detections: List[ManpuDetection]) -> List[str]:
    """
    Aggregate emotion tags from multiple manpu detections.
    
    Returns unique list of emotion tags.
    """
    all_emotions: List[str] = []
    for det in manpu_detections:
        all_emotions.extend(det.emotion_tags)
    
    # Return unique emotions, sorted by frequency
    from collections import Counter
    emotion_counts = Counter(all_emotions)
    return [emotion for emotion, _ in emotion_counts.most_common()]


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

