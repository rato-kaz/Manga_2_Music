"""
Domain Utilities: Helper functions for domain operations.

These are pure functions that operate on domain entities.
"""

from __future__ import annotations

from typing import List, Tuple
from src.domain.entities import BoundingBox


def calculate_bbox_overlap(bbox1: BoundingBox, bbox2: BoundingBox) -> float:
    """
    Calculate overlap area between two bounding boxes.
    
    Args:
        bbox1: First bounding box
        bbox2: Second bounding box
        
    Returns:
        Overlap area (0.0 if no overlap)
    """
    inter_x1 = max(bbox1.x1, bbox2.x1)
    inter_y1 = max(bbox1.y1, bbox2.y1)
    inter_x2 = min(bbox1.x2, bbox2.x2)
    inter_y2 = min(bbox1.y2, bbox2.y2)
    
    if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
        return 0.0
    
    return (inter_x2 - inter_x1) * (inter_y2 - inter_y1)


def calculate_intersection_over_union(bbox1: BoundingBox, bbox2: BoundingBox) -> float:
    """
    Calculate Intersection over Union (IoU) of two bounding boxes.
    
    Args:
        bbox1: First bounding box
        bbox2: Second bounding box
        
    Returns:
        IoU value between 0.0 and 1.0
    """
    overlap = calculate_bbox_overlap(bbox1, bbox2)
    union = bbox1.area + bbox2.area - overlap
    
    if union == 0.0:
        return 0.0
    
    return overlap / union


def is_point_inside_bbox(point: Tuple[float, float], bbox: BoundingBox) -> bool:
    """
    Check if a point is inside a bounding box.
    
    Args:
        point: Point coordinates (x, y)
        bbox: Bounding box
        
    Returns:
        True if point is inside bbox
    """
    x, y = point
    return bbox.x1 <= x <= bbox.x2 and bbox.y1 <= y <= bbox.y2


def find_bbox_containing_point(
    point: Tuple[float, float],
    bboxes: List[BoundingBox],
) -> int:
    """
    Find index of bounding box containing point.
    
    Args:
        point: Point coordinates (x, y)
        bboxes: List of bounding boxes
        
    Returns:
        Index of containing bbox, or -1 if not found
    """
    for idx, bbox in enumerate(bboxes):
        if is_point_inside_bbox(point, bbox):
            return idx
    return -1


def calculate_euclidean_distance(
    point1: Tuple[float, float],
    point2: Tuple[float, float],
) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
        
    Returns:
        Euclidean distance
    """
    import math
    dx = point1[0] - point2[0]
    dy = point1[1] - point2[1]
    return math.sqrt(dx * dx + dy * dy)

