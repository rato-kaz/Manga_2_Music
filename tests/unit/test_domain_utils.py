"""
Unit tests for domain utilities.

Example test file to demonstrate testing structure.
"""

import pytest
from src.domain.entities import BoundingBox
from src.domain.utils import calculate_bbox_overlap, calculate_intersection_over_union


def test_bbox_overlap_no_overlap() -> None:
    """Test bbox overlap calculation with no overlap."""
    bbox1 = BoundingBox(x1=0, y1=0, x2=10, y2=10)
    bbox2 = BoundingBox(x1=20, y1=20, x2=30, y2=30)
    
    overlap = calculate_bbox_overlap(bbox1, bbox2)
    assert overlap == 0.0


def test_bbox_overlap_partial_overlap() -> None:
    """Test bbox overlap calculation with partial overlap."""
    bbox1 = BoundingBox(x1=0, y1=0, x2=10, y2=10)
    bbox2 = BoundingBox(x1=5, y1=5, x2=15, y2=15)
    
    overlap = calculate_bbox_overlap(bbox1, bbox2)
    assert overlap == 25.0  # 5x5 overlap


def test_iou_calculation() -> None:
    """Test Intersection over Union calculation."""
    bbox1 = BoundingBox(x1=0, y1=0, x2=10, y2=10)
    bbox2 = BoundingBox(x1=5, y1=5, x2=15, y2=15)
    
    iou = calculate_intersection_over_union(bbox1, bbox2)
    assert 0.0 < iou < 1.0

