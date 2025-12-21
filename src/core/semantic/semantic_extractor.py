"""
Semantic Extraction Module for Manga Panels.

This module extracts high-level semantic information:
- Scene classification (Battle, Romance, Comedy, etc.)
- Emotion aggregation from multiple sources
- Context understanding for audio generation
"""

from __future__ import annotations

from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from collections import Counter
import re


@dataclass
class SceneContext:
    """Represents scene context for a panel."""
    scene_type: str  # 'battle', 'romance', 'comedy', 'drama', 'action', 'slice_of_life', etc.
    location: Optional[str] = None  # 'indoors', 'outdoors', 'city', 'nature', etc.
    time_of_day: Optional[str] = None  # 'day', 'night', 'dawn', 'dusk'
    mood: str = "neutral"  # Overall mood
    intensity: float = 0.5  # 0.0 (calm) to 1.0 (intense)
    emotion_tags: List[str] = None  # Aggregated emotions


# Scene classification keywords
SCENE_KEYWORDS: Dict[str, List[str]] = {
    'battle': ['fight', 'attack', 'sword', 'punch', 'kick', 'explosion', 'battle', 'war', 'combat'],
    'romance': ['love', 'kiss', 'heart', 'romance', 'date', 'confession', 'hug'],
    'comedy': ['laugh', 'funny', 'joke', 'comedy', 'silly', 'humor'],
    'drama': ['cry', 'sad', 'tears', 'drama', 'emotional', 'conflict'],
    'action': ['run', 'chase', 'jump', 'action', 'movement', 'speed'],
    'slice_of_life': ['school', 'home', 'daily', 'normal', 'routine', 'everyday'],
    'mystery': ['mystery', 'investigate', 'clue', 'secret', 'hidden'],
    'horror': ['scary', 'fear', 'horror', 'dark', 'shadow', 'ghost'],
}


def classify_scene_type(
    panel_texts: List[str],
    emotions: List[str],
    manpu_types: List[str],
    panel_description: Optional[str] = None,
) -> str:
    """
    Classify scene type based on text, emotions, and visual cues.
    
    Args:
        panel_texts: List of text content in panel
        emotions: List of emotion tags
        manpu_types: List of detected manpu types
        panel_description: Optional VLM description of panel
    
    Returns:
        Scene type string
    """
    # Combine all text sources
    all_text = " ".join(panel_texts).lower()
    if panel_description:
        all_text += " " + panel_description.lower()
    
    # Count keyword matches
    scene_scores: Dict[str, float] = {}
    
    for scene_type, keywords in SCENE_KEYWORDS.items():
        score = 0.0
        for keyword in keywords:
            if keyword in all_text:
                score += 1.0
        
        # Normalize by number of keywords
        if keywords:
            score = score / len(keywords)
        scene_scores[scene_type] = score
    
    # Boost scores based on emotions
    emotion_boosts = {
        'battle': ['anger', 'rage', 'tension', 'frustrated'],
        'romance': ['joy', 'love', 'admiration', 'dreamy'],
        'comedy': ['comedy', 'awkward', 'nervous'],
        'drama': ['sad', 'crying', 'emotional', 'nervous'],
    }
    
    for scene_type, boost_emotions in emotion_boosts.items():
        for emotion in emotions:
            if emotion in boost_emotions:
                scene_scores[scene_type] = scene_scores.get(scene_type, 0) + 0.2
    
    # Boost based on manpu
    manpu_boosts = {
        'battle': ['vein', 'steam'],
        'romance': ['sparkles', 'heart'],
        'comedy': ['sweat'],
        'drama': ['tears', 'vertical_lines'],
    }
    
    for scene_type, boost_manpu in manpu_boosts.items():
        for manpu_type in manpu_types:
            if manpu_type in boost_manpu:
                scene_scores[scene_type] = scene_scores.get(scene_type, 0) + 0.15
    
    # Return scene type with highest score
    if scene_scores:
        best_scene = max(scene_scores.items(), key=lambda x: x[1])
        if best_scene[1] > 0.1:  # Minimum threshold
            return best_scene[0]
    
    return "slice_of_life"  # Default


def infer_location(
    panel_texts: List[str],
    panel_description: Optional[str] = None,
) -> Optional[str]:
    """
    Infer location from text and description.
    
    Returns:
        Location string or None
    """
    all_text = " ".join(panel_texts).lower()
    if panel_description:
        all_text += " " + panel_description.lower()
    
    location_keywords = {
        'indoors': ['room', 'house', 'building', 'inside', 'indoor', 'home', 'school', 'office'],
        'outdoors': ['outside', 'outdoor', 'street', 'park', 'field', 'forest'],
        'city': ['city', 'urban', 'street', 'building', 'skyscraper', 'town'],
        'nature': ['forest', 'mountain', 'beach', 'ocean', 'river', 'tree', 'flower'],
        'school': ['school', 'classroom', 'hallway', 'cafeteria', 'gym'],
        'home': ['home', 'house', 'room', 'bedroom', 'kitchen', 'living room'],
    }
    
    for location, keywords in location_keywords.items():
        for keyword in keywords:
            if keyword in all_text:
                return location
    
    return None


def infer_time_of_day(
    panel_texts: List[str],
    panel_description: Optional[str] = None,
) -> Optional[str]:
    """
    Infer time of day from text and description.
    
    Returns:
        Time of day string or None
    """
    all_text = " ".join(panel_texts).lower()
    if panel_description:
        all_text += " " + panel_description.lower()
    
    time_keywords = {
        'night': ['night', 'dark', 'moon', 'evening', 'midnight', 'stars'],
        'day': ['day', 'sun', 'sunny', 'bright', 'morning', 'afternoon'],
        'dawn': ['dawn', 'sunrise', 'early morning'],
        'dusk': ['dusk', 'sunset', 'twilight', 'evening'],
    }
    
    for time, keywords in time_keywords.items():
        for keyword in keywords:
            if keyword in all_text:
                return time
    
    return None


def calculate_intensity(
    emotions: List[str],
    manpu_types: List[str],
    scene_type: str,
    onomatopoeia_count: int,
) -> float:
    """
    Calculate intensity level (0.0 to 1.0) based on various factors.
    
    Args:
        emotions: List of emotion tags
        manpu_types: List of manpu types
        scene_type: Scene type
        onomatopoeia_count: Number of onomatopoeia detected
    
    Returns:
        Intensity value between 0.0 and 1.0
    """
    intensity = 0.5  # Base intensity
    
    # High intensity emotions
    high_intensity_emotions = ['anger', 'rage', 'furious', 'excited', 'shock', 'surprise']
    for emotion in emotions:
        if emotion in high_intensity_emotions:
            intensity += 0.1
    
    # High intensity manpu
    high_intensity_manpu = ['vein', 'steam', 'vertical_lines']
    for manpu in manpu_types:
        if manpu in high_intensity_manpu:
            intensity += 0.1
    
    # Scene type intensity
    scene_intensities = {
        'battle': 0.9,
        'action': 0.8,
        'horror': 0.7,
        'romance': 0.4,
        'comedy': 0.5,
        'slice_of_life': 0.3,
    }
    if scene_type in scene_intensities:
        intensity = (intensity + scene_intensities[scene_type]) / 2
    
    # Onomatopoeia boost
    intensity += min(onomatopoeia_count * 0.05, 0.2)
    
    # Clamp to [0.0, 1.0]
    return max(0.0, min(1.0, intensity))


def aggregate_emotions(
    manpu_emotions: List[str],
    text_emotions: List[str],
    scene_type: str,
) -> List[str]:
    """
    Aggregate emotions from multiple sources.
    
    Args:
        manpu_emotions: Emotions from manpu detection
        text_emotions: Emotions inferred from text (could be empty)
        scene_type: Scene type
    
    Returns:
        Aggregated list of unique emotions, sorted by frequency
    """
    all_emotions = manpu_emotions + text_emotions
    
    # Add scene-based emotions
    scene_emotions = {
        'battle': ['tension', 'excitement', 'anger'],
        'romance': ['joy', 'love', 'happiness'],
        'comedy': ['joy', 'amusement'],
        'drama': ['sadness', 'tension', 'emotional'],
        'horror': ['fear', 'tension', 'anxiety'],
    }
    
    if scene_type in scene_emotions:
        all_emotions.extend(scene_emotions[scene_type])
    
    # Count and sort by frequency
    emotion_counts = Counter(all_emotions)
    
    # Return top emotions (max 5)
    top_emotions = [emotion for emotion, _ in emotion_counts.most_common(5)]
    
    return top_emotions


def extract_semantic_context(
    panel_data: Dict,
) -> SceneContext:
    """
    Extract semantic context from panel data.
    
    Args:
        panel_data: Panel entry from JSON
    
    Returns:
        SceneContext object
    """
    # Extract data
    panel_texts = [bubble.get("text", "") for bubble in panel_data.get("content", [])]
    panel_description = panel_data.get("caption")
    
    # Extract emotions from manpu
    manpu_list = panel_data.get("manpu", [])
    manpu_emotions = []
    manpu_types = []
    for manpu in manpu_list:
        manpu_emotions.extend(manpu.get("emotion_tags", []))
        manpu_types.append(manpu.get("manpu_type", ""))
    
    # Get existing emotions
    existing_emotions = panel_data.get("emotions", [])
    
    # Classify scene
    scene_type = classify_scene_type(
        panel_texts,
        existing_emotions,
        manpu_types,
        panel_description,
    )
    
    # Infer location and time
    location = infer_location(panel_texts, panel_description)
    time_of_day = infer_time_of_day(panel_texts, panel_description)
    
    # Calculate intensity
    onomatopoeia_count = len(panel_data.get("onomatopoeia", []))
    intensity = calculate_intensity(
        existing_emotions,
        manpu_types,
        scene_type,
        onomatopoeia_count,
    )
    
    # Aggregate emotions
    aggregated_emotions = aggregate_emotions(
        manpu_emotions,
        existing_emotions,
        scene_type,
    )
    
    # Determine overall mood
    mood = "neutral"
    if aggregated_emotions:
        primary_emotion = aggregated_emotions[0]
        if primary_emotion in ['joy', 'happiness', 'love']:
            mood = "positive"
        elif primary_emotion in ['anger', 'rage', 'frustrated']:
            mood = "negative"
        elif primary_emotion in ['sadness', 'sad', 'crying']:
            mood = "sad"
        elif primary_emotion in ['tension', 'nervous', 'anxiety']:
            mood = "tense"
    
    return SceneContext(
        scene_type=scene_type,
        location=location,
        time_of_day=time_of_day,
        mood=mood,
        intensity=intensity,
        emotion_tags=aggregated_emotions,
    )


def extract_semantic_contexts_for_chapter(
    chapter_entries: List[Dict],
) -> List[Dict]:
    """
    Extract semantic contexts for all panels in chapter.
    
    Args:
        chapter_entries: List of page entries
    
    Returns:
        Updated chapter entries with semantic context
    """
    for page_entry in chapter_entries:
        panel_entries = page_entry.get("content", [])
        
        for panel_entry in panel_entries:
            # Extract semantic context
            scene_context = extract_semantic_context(panel_entry)
            
            # Add to panel entry
            panel_entry["scene_context"] = {
                "scene_type": scene_context.scene_type,
                "location": scene_context.location,
                "time_of_day": scene_context.time_of_day,
                "mood": scene_context.mood,
                "intensity": scene_context.intensity,
                "emotion_tags": scene_context.emotion_tags,
            }
    
    return chapter_entries

