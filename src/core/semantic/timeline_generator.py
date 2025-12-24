"""
Timeline Generation Module for Manga Reading.

This module generates temporal timeline with timestamps for each panel,
estimating reading time based on text length, image complexity, and other factors.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class TimelineEntry:
    """Represents a timeline entry for a panel."""

    panel_id: int
    start_time: float  # Seconds
    end_time: float  # Seconds
    duration: float  # Seconds
    reading_time: float  # Estimated reading time
    viewing_time: float  # Estimated viewing time (for images)


# Reading speed constants
WORDS_PER_MINUTE = 200  # Average reading speed
CHARACTERS_PER_MINUTE = 1000  # For Japanese/Chinese characters
MIN_PANEL_TIME = 2.0  # Minimum time per panel (seconds)
MAX_PANEL_TIME = 30.0  # Maximum time per panel (seconds)


def count_text_length(text: str, language: str = "ja") -> int:
    """
    Count effective text length for reading time calculation.

    Args:
        text: Text content
        language: Language code

    Returns:
        Effective character/word count
    """
    if language == "ja" or language == "zh":
        # For Japanese/Chinese, count characters
        return len(text)
    else:
        # For other languages, count words
        words = text.split()
        return len(words)


def estimate_reading_time(
    panel_texts: List[str],
    language: str = "ja",
) -> float:
    """
    Estimate reading time for panel texts.

    Args:
        panel_texts: List of text content
        language: Language code

    Returns:
        Reading time in seconds
    """
    total_length = sum(count_text_length(text, language) for text in panel_texts)

    if language == "ja" or language == "zh":
        # Japanese/Chinese: characters per minute
        reading_speed = CHARACTERS_PER_MINUTE
    else:
        # Other languages: words per minute
        reading_speed = WORDS_PER_MINUTE

    reading_time = (total_length / reading_speed) * 60  # Convert to seconds

    return reading_time


def calculate_image_complexity(
    panel_data: Dict,
) -> float:
    """
    Calculate image complexity score (0.0 to 1.0).

    Based on:
    - Number of characters
    - Number of objects/elements
    - Panel size
    - Presence of detailed backgrounds

    Args:
        panel_data: Panel entry

    Returns:
        Complexity score
    """
    complexity = 0.0

    # Character count
    character_count = len(panel_data.get("character", []))
    complexity += min(character_count * 0.1, 0.3)

    # Manpu count (indicates visual detail)
    manpu_count = len(panel_data.get("manpu", []))
    complexity += min(manpu_count * 0.05, 0.2)

    # Onomatopoeia count
    onomatopoeia_count = len(panel_data.get("onomatopoeia", []))
    complexity += min(onomatopoeia_count * 0.05, 0.15)

    # Panel size (larger panels = more detail)
    panel_size = panel_data.get("panel", {}).get("panel_size", {})
    panel_area = panel_size.get("width", 0) * panel_size.get("height", 0)
    # Normalize (assuming max area ~1,000,000)
    area_score = min(panel_area / 1000000.0, 0.35)
    complexity += area_score

    return min(complexity, 1.0)


def estimate_viewing_time(
    panel_data: Dict,
    base_viewing_time: float = 3.0,
) -> float:
    """
    Estimate viewing time for panel (time to look at image).

    Args:
        panel_data: Panel entry
        base_viewing_time: Base viewing time in seconds

    Returns:
        Viewing time in seconds
    """
    complexity = calculate_image_complexity(panel_data)

    # More complex images = more viewing time
    viewing_time = base_viewing_time * (1.0 + complexity)

    # Scene intensity affects viewing time
    scene_context = panel_data.get("scene_context", {})
    intensity = scene_context.get("intensity", 0.5)

    # High intensity scenes might be viewed longer
    viewing_time *= 1.0 + intensity * 0.3

    return viewing_time


def generate_timeline_for_panel(
    panel_data: Dict,
    start_time: float,
    language: str = "ja",
) -> TimelineEntry:
    """
    Generate timeline entry for a single panel.

    Args:
        panel_data: Panel entry
        start_time: Start time in seconds
        language: Language code

    Returns:
        TimelineEntry object
    """
    panel_id = panel_data.get("panel", {}).get("panel_id", 0)

    # Extract texts
    panel_texts = [bubble.get("text", "") for bubble in panel_data.get("content", [])]

    # Estimate reading time
    reading_time = estimate_reading_time(panel_texts, language)

    # Estimate viewing time
    viewing_time = estimate_viewing_time(panel_data)

    # Total duration = reading time + viewing time
    # But reading can happen while viewing, so use max + some overlap
    duration = max(reading_time, viewing_time) + min(reading_time, viewing_time) * 0.3

    # Apply min/max constraints
    duration = max(MIN_PANEL_TIME, min(duration, MAX_PANEL_TIME))

    end_time = start_time + duration

    return TimelineEntry(
        panel_id=panel_id,
        start_time=start_time,
        end_time=end_time,
        duration=duration,
        reading_time=reading_time,
        viewing_time=viewing_time,
    )


def generate_timeline_for_page(
    page_entry: Dict,
    start_time: float,
    language: str = "ja",
) -> List[TimelineEntry]:
    """
    Generate timeline for all panels in a page.

    Args:
        page_entry: Page entry
        start_time: Start time for first panel
        language: Language code

    Returns:
        List of TimelineEntry objects
    """
    panel_entries = page_entry.get("content", [])

    # Sort by reading order if available
    if panel_entries and "reading_order" in panel_entries[0].get("panel", {}):
        panel_entries = sorted(
            panel_entries, key=lambda p: p.get("panel", {}).get("reading_order", 0)
        )

    timeline_entries: List[TimelineEntry] = []
    current_time = start_time

    for panel_entry in panel_entries:
        timeline_entry = generate_timeline_for_panel(
            panel_entry,
            current_time,
            language,
        )
        timeline_entries.append(timeline_entry)

        # Update panel entry with timeline
        panel_entry["timeline"] = {
            "start_time": timeline_entry.start_time,
            "end_time": timeline_entry.end_time,
            "duration": timeline_entry.duration,
            "reading_time": timeline_entry.reading_time,
            "viewing_time": timeline_entry.viewing_time,
        }

        # Next panel starts when this one ends
        current_time = timeline_entry.end_time

    return timeline_entries


def generate_timeline_for_chapter(
    chapter_entries: List[Dict],
    language: str = "ja",
    start_time: float = 0.0,
) -> List[TimelineEntry]:
    """
    Generate timeline for entire chapter.

    Args:
        chapter_entries: List of page entries
        language: Language code
        start_time: Starting time for chapter

    Returns:
        List of TimelineEntry objects for all panels
    """
    all_timeline_entries: List[TimelineEntry] = []
    current_time = start_time

    for page_entry in chapter_entries:
        page_timeline = generate_timeline_for_page(
            page_entry,
            current_time,
            language,
        )
        all_timeline_entries.extend(page_timeline)

        # Update page entry with total duration
        if page_timeline:
            page_start = page_timeline[0].start_time
            page_end = page_timeline[-1].end_time
            page_entry["page"]["timeline"] = {
                "start_time": page_start,
                "end_time": page_end,
                "duration": page_end - page_start,
            }

            # Next page starts with small gap
            current_time = page_end + 0.5  # 0.5 second gap between pages

    return all_timeline_entries


def get_panel_at_time(
    chapter_entries: List[Dict],
    timestamp: float,
) -> Optional[Dict]:
    """
    Get panel that should be displayed at given timestamp.

    Args:
        chapter_entries: List of page entries
        timestamp: Time in seconds

    Returns:
        Panel entry or None
    """
    for page_entry in chapter_entries:
        panel_entries = page_entry.get("content", [])

        for panel_entry in panel_entries:
            timeline = panel_entry.get("timeline", {})
            start_time = timeline.get("start_time", 0)
            end_time = timeline.get("end_time", 0)

            if start_time <= timestamp <= end_time:
                return panel_entry

    return None
