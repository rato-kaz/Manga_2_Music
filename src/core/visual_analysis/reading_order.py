"""
Reading Order Resolution for Manga Panels using Kovanen Algorithm.

This module implements the reading order estimation algorithm based on
recursive gutter-based page division, following the approach described
in the manga109 panel-order-estimator.

Manga reading order: Right-to-Left, Top-to-Bottom
"""

from __future__ import annotations

import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

BBOX = List[float]  # [x1, y1, x2, y2]


@dataclass
class Gutter:
    """Represents a gutter (white space) that divides panels."""
    orientation: str  # 'horizontal' or 'vertical'
    position: float  # x position for vertical, y position for horizontal
    start: float
    end: float


@dataclass
class PanelNode:
    """Node in the recursive division tree."""
    bbox: BBOX
    children: List[PanelNode]
    is_leaf: bool


def bbox_center(bbox: BBOX) -> Tuple[float, float]:
    """Get center point of bounding box."""
    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0


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


def detect_gutters(
    panels: List[BBOX],
    page_width: float,
    page_height: float,
    min_gutter_size: float = 10.0,
) -> Tuple[List[Gutter], List[Gutter]]:
    """
    Detect horizontal and vertical gutters (white spaces) between panels.
    
    Args:
        panels: List of panel bounding boxes
        page_width: Width of the page
        page_height: Height of the page
        min_gutter_size: Minimum size for a gutter to be considered
    
    Returns:
        Tuple of (horizontal_gutters, vertical_gutters)
    """
    horizontal_gutters: List[Gutter] = []
    vertical_gutters: List[Gutter] = []
    
    # Detect horizontal gutters (divide top-bottom)
    # Look for gaps in y-coordinates
    panel_y_ranges = [(bbox[1], bbox[3]) for bbox in panels]
    panel_y_ranges.sort(key=lambda r: r[0])
    
    for i in range(len(panel_y_ranges) - 1):
        bottom = panel_y_ranges[i][1]
        top = panel_y_ranges[i + 1][0]
        
        if top - bottom >= min_gutter_size:
            # Check if this gutter spans horizontally
            # Find min x and max x of panels that could be separated
            left_x = min(bbox[0] for bbox in panels if bbox[3] <= bottom + min_gutter_size)
            right_x = max(bbox[2] for bbox in panels if bbox[1] >= top - min_gutter_size)
            
            gutter = Gutter(
                orientation='horizontal',
                position=(top + bottom) / 2.0,
                start=left_x,
                end=right_x,
            )
            horizontal_gutters.append(gutter)
    
    # Detect vertical gutters (divide left-right)
    # Look for gaps in x-coordinates
    panel_x_ranges = [(bbox[0], bbox[2]) for bbox in panels]
    panel_x_ranges.sort(key=lambda r: r[0])
    
    for i in range(len(panel_x_ranges) - 1):
        right = panel_x_ranges[i][2]
        left = panel_x_ranges[i + 1][0]
        
        if left - right >= min_gutter_size:
            # Check if this gutter spans vertically
            top_y = min(bbox[1] for bbox in panels if bbox[2] <= right + min_gutter_size)
            bottom_y = max(bbox[3] for bbox in panels if bbox[0] >= left - min_gutter_size)
            
            gutter = Gutter(
                orientation='vertical',
                position=(left + right) / 2.0,
                start=top_y,
                end=bottom_y,
            )
            vertical_gutters.append(gutter)
    
    return horizontal_gutters, vertical_gutters


def select_best_gutter(
    horizontal_gutters: List[Gutter],
    vertical_gutters: List[Gutter],
    panels: List[BBOX],
) -> Optional[Gutter]:
    """
    Select the best gutter to use for division.
    Prefer gutters that divide panels more evenly.
    """
    all_gutters: List[Tuple[Gutter, float]] = []
    
    for gutter in horizontal_gutters:
        # Count panels on each side
        top_count = sum(1 for bbox in panels if bbox_center(bbox)[1] < gutter.position)
        bottom_count = sum(1 for bbox in panels if bbox_center(bbox)[1] >= gutter.position)
        
        if top_count > 0 and bottom_count > 0:
            # Score: prefer gutters that divide more evenly
            imbalance = abs(top_count - bottom_count) / len(panels)
            all_gutters.append((gutter, imbalance))
    
    for gutter in vertical_gutters:
        # Count panels on each side
        left_count = sum(1 for bbox in panels if bbox_center(bbox)[0] < gutter.position)
        right_count = sum(1 for bbox in panels if bbox_center(bbox)[0] >= gutter.position)
        
        if left_count > 0 and right_count > 0:
            imbalance = abs(left_count - right_count) / len(panels)
            all_gutters.append((gutter, imbalance))
    
    if not all_gutters:
        return None
    
    # Return gutter with lowest imbalance (most balanced division)
    all_gutters.sort(key=lambda x: x[1])
    return all_gutters[0][0]


def divide_panels_by_gutter(
    panels: List[BBOX],
    gutter: Gutter,
) -> Tuple[List[BBOX], List[BBOX]]:
    """Divide panels into two groups based on gutter position."""
    group1: List[BBOX] = []
    group2: List[BBOX] = []
    
    if gutter.orientation == 'horizontal':
        # Divide top and bottom
        for bbox in panels:
            center_y = bbox_center(bbox)[1]
            if center_y < gutter.position:
                group1.append(bbox)
            else:
                group2.append(bbox)
    else:  # vertical
        # Divide left and right (for RTL reading, right comes first)
        for bbox in panels:
            center_x = bbox_center(bbox)[0]
            if center_x >= gutter.position:
                group1.append(bbox)  # Right side (read first in RTL)
            else:
                group2.append(bbox)  # Left side (read second in RTL)
    
    return group1, group2


def build_division_tree(
    panels: List[BBOX],
    page_width: float,
    page_height: float,
    min_gutter_size: float = 10.0,
    max_depth: int = 10,
) -> PanelNode:
    """
    Recursively build a division tree by splitting panels with gutters.
    
    This implements the core of the Kovanen algorithm.
    """
    if len(panels) <= 1 or max_depth <= 0:
        # Leaf node: single panel or no more division possible
        if len(panels) == 1:
            return PanelNode(bbox=panels[0], children=[], is_leaf=True)
        else:
            # Fallback: create a container node
            if panels:
                # Calculate bounding box of all panels
                x1 = min(bbox[0] for bbox in panels)
                y1 = min(bbox[1] for bbox in panels)
                x2 = max(bbox[2] for bbox in panels)
                y2 = max(bbox[3] for bbox in panels)
                return PanelNode(bbox=[x1, y1, x2, y2], children=[], is_leaf=True)
            return PanelNode(bbox=[0, 0, page_width, page_height], children=[], is_leaf=True)
    
    # Detect gutters
    horizontal_gutters, vertical_gutters = detect_gutters(
        panels, page_width, page_height, min_gutter_size
    )
    
    # Select best gutter
    best_gutter = select_best_gutter(horizontal_gutters, vertical_gutters, panels)
    
    if best_gutter is None:
        # No suitable gutter found, sort panels directly
        # For RTL: sort by x descending, then y ascending
        sorted_panels = sorted(panels, key=lambda b: (-bbox_center(b)[0], bbox_center(b)[1]))
        if len(sorted_panels) == 1:
            return PanelNode(bbox=sorted_panels[0], children=[], is_leaf=True)
        # Create a container node
        x1 = min(bbox[0] for bbox in sorted_panels)
        y1 = min(bbox[1] for bbox in sorted_panels)
        x2 = max(bbox[2] for bbox in sorted_panels)
        y2 = max(bbox[3] for bbox in sorted_panels)
        return PanelNode(bbox=[x1, y1, x2, y2], children=[], is_leaf=True)
    
    # Divide panels
    group1, group2 = divide_panels_by_gutter(panels, best_gutter)
    
    if not group1 or not group2:
        # Division failed, sort directly
        sorted_panels = sorted(panels, key=lambda b: (-bbox_center(b)[0], bbox_center(b)[1]))
        if len(sorted_panels) == 1:
            return PanelNode(bbox=sorted_panels[0], children=[], is_leaf=True)
        x1 = min(bbox[0] for bbox in sorted_panels)
        y1 = min(bbox[1] for bbox in sorted_panels)
        x2 = max(bbox[2] for bbox in sorted_panels)
        y2 = max(bbox[3] for bbox in sorted_panels)
        return PanelNode(bbox=[x1, y1, x2, y2], children=[], is_leaf=True)
    
    # Recursively process each group
    child1 = build_division_tree(group1, page_width, page_height, min_gutter_size, max_depth - 1)
    child2 = build_division_tree(group2, page_width, page_height, min_gutter_size, max_depth - 1)
    
    # Determine order: for RTL, right group (group1 if vertical) comes first
    if best_gutter.orientation == 'vertical':
        # Right (group1) comes first in RTL
        children = [child1, child2]
    else:
        # Top (group1) comes first
        children = [child1, child2]
    
    # Calculate bounding box
    x1 = min(bbox[0] for bbox in panels)
    y1 = min(bbox[1] for bbox in panels)
    x2 = max(bbox[2] for bbox in panels)
    y2 = max(bbox[3] for bbox in panels)
    
    return PanelNode(bbox=[x1, y1, x2, y2], children=children, is_leaf=False)


def traverse_tree_rtl(node: PanelNode) -> List[BBOX]:
    """
    Traverse the division tree in Right-to-Left, Top-to-Bottom order.
    
    Returns list of panel bounding boxes in reading order.
    """
    if node.is_leaf:
        return [node.bbox]
    
    result: List[BBOX] = []
    for child in node.children:
        result.extend(traverse_tree_rtl(child))
    
    return result


def detect_4koma_layout(panels: List[BBOX], page_width: float, page_height: float) -> bool:
    """
    Detect if the page uses 4-koma layout (4 vertical panels).
    
    Returns True if likely 4-koma layout.
    """
    if len(panels) != 4:
        return False
    
    # Check if panels are roughly equal width and stacked vertically
    panel_widths = [bbox[2] - bbox[0] for bbox in panels]
    avg_width = sum(panel_widths) / len(panel_widths)
    
    # In 4-koma, panels should be roughly full width
    if avg_width < page_width * 0.8:
        return False
    
    # Check vertical stacking
    panel_centers_y = [bbox_center(bbox)[1] for bbox in panels]
    panel_centers_y.sort()
    
    # Check if panels are evenly spaced vertically
    if len(panel_centers_y) >= 2:
        gaps = [panel_centers_y[i+1] - panel_centers_y[i] for i in range(len(panel_centers_y) - 1)]
        avg_gap = sum(gaps) / len(gaps)
        if all(abs(gap - avg_gap) < avg_gap * 0.3 for gap in gaps):
            return True
    
    return False


def estimate_reading_order(
    panels: List[BBOX],
    page_width: float,
    page_height: float,
    is_4koma: Optional[bool] = None,
    min_gutter_size: float = 10.0,
) -> List[int]:
    """
    Estimate reading order for manga panels using Kovanen algorithm.
    
    Args:
        panels: List of panel bounding boxes [x1, y1, x2, y2]
        page_width: Width of the page
        page_height: Height of the page
        is_4koma: Whether this is a 4-koma layout (auto-detected if None)
        min_gutter_size: Minimum gutter size to consider
    
    Returns:
        List of panel indices in reading order (0-indexed)
    """
    if not panels:
        return []
    
    if len(panels) == 1:
        return [0]
    
    # Auto-detect 4-koma if not specified
    if is_4koma is None:
        is_4koma = detect_4koma_layout(panels, page_width, page_height)
    
    if is_4koma:
        # 4-koma: strict top-to-bottom order
        panel_centers_y = [(i, bbox_center(bbox)[1]) for i, bbox in enumerate(panels)]
        panel_centers_y.sort(key=lambda x: x[1])
        return [idx for idx, _ in panel_centers_y]
    
    # Build division tree
    tree = build_division_tree(panels, page_width, page_height, min_gutter_size)
    
    # Traverse tree to get reading order
    ordered_bboxes = traverse_tree_rtl(tree)
    
    # Map back to original indices
    order_map: Dict[Tuple[float, float, float, float], int] = {}
    for idx, bbox in enumerate(panels):
        # Use center point as key (with tolerance)
        center = bbox_center(bbox)
        order_map[center] = idx
    
    # Find original indices for ordered bboxes
    reading_order: List[int] = []
    used_indices = set()
    
    for ordered_bbox in ordered_bboxes:
        ordered_center = bbox_center(ordered_bbox)
        best_idx = None
        best_distance = float('inf')
        
        for idx, orig_bbox in enumerate(panels):
            if idx in used_indices:
                continue
            
            orig_center = bbox_center(orig_bbox)
            # Calculate distance
            dist = np.sqrt(
                (ordered_center[0] - orig_center[0])**2 +
                (ordered_center[1] - orig_center[1])**2
            )
            
            # Also check overlap
            overlap = bbox_overlap(ordered_bbox, orig_bbox)
            if overlap > 0:
                dist = 0  # Perfect match
            
            if dist < best_distance:
                best_distance = dist
                best_idx = idx
        
        if best_idx is not None:
            reading_order.append(best_idx)
            used_indices.add(best_idx)
    
    # Add any remaining panels (fallback)
    for idx in range(len(panels)):
        if idx not in used_indices:
            reading_order.append(idx)
    
    return reading_order


def reorder_panels_by_reading_order(
    panels: List[BBOX],
    reading_order: List[int],
) -> List[BBOX]:
    """Reorder panels according to reading order."""
    return [panels[idx] for idx in reading_order]

