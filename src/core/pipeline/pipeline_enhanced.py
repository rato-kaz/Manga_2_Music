"""
Enhanced Pipeline with Reading Order, Character Re-ID, Manpu Detection, etc.

This module integrates all the new modules into the main pipeline.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Dict, Optional, Sequence
import numpy as np

from src.infrastructure.logger import get_logger

# Import original pipeline
from src.core.pipeline.pipeline_generate_json import (
    generate_json_for_chapter as base_generate_json,
    PageImage,
    BBOX,
    bbox_size_and_position,
    find_panel_index,
    format_character_entry,
    format_bubble_entry,
)

# Import new modules
from src.core.visual_analysis.reading_order import estimate_reading_order, detect_4koma_layout
from src.core.visual_analysis.character_reid import (
    CharacterFeatureExtractor,
    CharacterDetection,
    reidentify_characters,
)
from src.core.visual_analysis.speaker_diarization import (
    SpeechBubble,
    Character as SpeakerCharacter,
    assign_speaker_to_bubble,
    diarize_speakers_in_panel,
)
from src.core.visual_analysis.manpu_detector import detect_manpu_in_panel, aggregate_emotions
from src.core.visual_analysis.onomatopoeia_classifier import detect_onomatopoeia_in_panel

logger = get_logger(__name__)


def enhance_json_with_reading_order(
    chapter_entries: List[Dict],
    pages: List[PageImage],
) -> List[Dict]:
    """
    Add reading order to panels in chapter entries.
    
    Args:
        chapter_entries: List of page entries from base pipeline
        pages: List of PageImage objects
    
    Returns:
        Enhanced chapter entries with reading_order field
    """
    enhanced_entries = []
    
    for page_entry, page in zip(chapter_entries, pages):
        panel_entries = page_entry.get("content", [])
        if not panel_entries:
            enhanced_entries.append(page_entry)
            continue
        
        # Extract panel bboxes
        panel_bboxes: List[BBOX] = []
        for panel_entry in panel_entries:
            panel_pos = panel_entry["panel"]["panel_position"]
            panel_bboxes.append([
                panel_pos["x1"],
                panel_pos["y1"],
                panel_pos["x2"],
                panel_pos["y2"],
            ])
        
        # Estimate reading order
        page_width = page.width
        page_height = page.height
        
        reading_order_indices = estimate_reading_order(
            panel_bboxes,
            page_width,
            page_height,
        )
        
        # Reorder panels and add reading_order field
        reordered_panels = [panel_entries[i] for i in reading_order_indices]
        
        for idx, panel in enumerate(reordered_panels):
            panel["panel"]["reading_order"] = idx + 1
        
        page_entry["content"] = reordered_panels
        enhanced_entries.append(page_entry)
    
    return enhanced_entries


def enhance_json_with_character_reid(
    chapter_entries: List[Dict],
    pages: List[PageImage],
    feature_extractor: Optional[CharacterFeatureExtractor] = None,
) -> List[Dict]:
    """
    Add global character IDs using character re-identification.
    
    Args:
        chapter_entries: List of page entries
        pages: List of PageImage objects
        feature_extractor: Feature extractor for characters
    
    Returns:
        Enhanced chapter entries with global_character_id
    """
    # Collect all character detections
    all_detections: List[CharacterDetection] = []
    
    for page_idx, (page_entry, page) in enumerate(zip(chapter_entries, pages)):
        panel_entries = page_entry.get("content", [])
        
        for panel_idx, panel_entry in enumerate(panel_entries):
            characters = panel_entry.get("character", [])
            
            for char_entry in characters:
                char_pos = char_entry["character_position"]
                bbox = [
                    char_pos["x1"],
                    char_pos["y1"],
                    char_pos["x2"],
                    char_pos["y2"],
                ]
                
                # Extract features if extractor available
                feature_vector = None
                if feature_extractor is not None:
                    try:
                        feature_vector = feature_extractor.extract_features(page.array, bbox)
                    except Exception as e:
                        logger.warning(f"Feature extraction failed: {e}", exc_info=True)
                
                detection = CharacterDetection(
                    page_idx=page_idx,
                    panel_idx=panel_idx,
                    bbox=bbox,
                    character_id=char_entry["character_id"],
                    character_name=char_entry.get("character_name"),
                    feature_vector=feature_vector,
                )
                all_detections.append(detection)
    
    # Perform clustering
    if all_detections:
        global_id_map = reidentify_characters(all_detections, method="agglomerative")
        
        # Update chapter entries with global IDs
        for page_idx, page_entry in enumerate(chapter_entries):
            panel_entries = page_entry.get("content", [])
            
            for panel_idx, panel_entry in enumerate(panel_entries):
                characters = panel_entry.get("character", [])
                
                for char_entry in characters:
                    key = (page_idx, panel_idx, char_entry["character_id"])
                    if key in global_id_map:
                        char_entry["global_character_id"] = global_id_map[key]
    
    return chapter_entries


def enhance_json_with_manpu(
    chapter_entries: List[Dict],
    pages: List[PageImage],
) -> List[Dict]:
    """
    Add manpu (emotion symbol) detections to panels.
    
    Args:
        chapter_entries: List of page entries
        pages: List of PageImage objects
    
    Returns:
        Enhanced chapter entries with manpu detections and emotions
    """
    for page_entry, page in zip(chapter_entries, pages):
        panel_entries = page_entry.get("content", [])
        
        for panel_entry in panel_entries:
            # Get character bboxes in panel
            characters = panel_entry.get("character", [])
            char_bboxes: List[BBOX] = []
            
            for char_entry in characters:
                char_pos = char_entry["character_position"]
                char_bboxes.append([
                    char_pos["x1"],
                    char_pos["y1"],
                    char_pos["x2"],
                    char_pos["y2"],
                ])
            
            # Detect manpu
            try:
                manpu_detections = detect_manpu_in_panel(page.array, char_bboxes)
                
                # Convert to JSON format
                manpu_list = []
                for det in manpu_detections:
                    size, pos = bbox_size_and_position(det.bbox)
                    manpu_list.append({
                        "manpu_type": det.manpu_type,
                        "manpu_position": pos,
                        "manpu_size": size,
                        "confidence": det.confidence,
                        "emotion_tags": det.emotion_tags,
                    })
                
                panel_entry["manpu"] = manpu_list
                
                # Aggregate emotions
                emotions = aggregate_emotions(manpu_detections)
                panel_entry["emotions"] = emotions
                
            except Exception as e:
                logger.warning(f"Manpu detection failed: {e}", exc_info=True)
                panel_entry["manpu"] = []
                panel_entry["emotions"] = []
    
    return chapter_entries


def enhance_json_with_onomatopoeia(
    chapter_entries: List[Dict],
    pages: List[PageImage],
) -> List[Dict]:
    """
    Add onomatopoeia detections to panels.
    
    Args:
        chapter_entries: List of page entries
        pages: List of PageImage objects
    
    Returns:
        Enhanced chapter entries with onomatopoeia
    """
    for page_entry, page in zip(chapter_entries, pages):
        panel_entries = page_entry.get("content", [])
        
        for panel_entry in panel_entries:
            # Get speech bubble bboxes to exclude
            bubbles = panel_entry.get("content", [])
            speech_bboxes: List[BBOX] = []
            
            for bubble in bubbles:
                if "bubble" in bubble:
                    bubble_pos = bubble["bubble"]["bubble_position"]
                    speech_bboxes.append([
                        bubble_pos["x1"],
                        bubble_pos["y1"],
                        bubble_pos["x2"],
                        bubble_pos["y2"],
                    ])
            
            # Get panel bbox
            panel_pos = panel_entry["panel"]["panel_position"]
            panel_bbox = [
                panel_pos["x1"],
                panel_pos["y1"],
                panel_pos["x2"],
                panel_pos["y2"],
            ]
            
            # Crop panel image
            x1, y1, x2, y2 = [int(coord) for coord in panel_bbox]
            h, w = page.array.shape[:2]
            x1 = max(0, min(x1, w))
            y1 = max(0, min(y1, h))
            x2 = max(0, min(x2, w))
            y2 = max(0, min(y2, h))
            
            if x2 > x1 and y2 > y1:
                panel_image = page.array[y1:y2, x1:x2]
                
                try:
                    onomatopoeia_detections = detect_onomatopoeia_in_panel(
                        panel_image,
                        exclude_speech_bubbles=speech_bboxes,
                    )
                    
                    # Convert to JSON format
                    onomatopoeia_list = []
                    for det in onomatopoeia_detections:
                        # Adjust bbox coordinates back to page space
                        adj_bbox = [
                            det.bbox[0] + x1,
                            det.bbox[1] + y1,
                            det.bbox[2] + x1,
                            det.bbox[3] + y1,
                        ]
                        size, pos = bbox_size_and_position(adj_bbox)
                        
                        onomatopoeia_list.append({
                            "onomatopoeia_type": det.type,
                            "visual_form": det.visual_form,
                            "onomatopoeia_position": pos,
                            "onomatopoeia_size": size,
                            "audio_keywords": det.audio_keywords,
                            "confidence": det.confidence,
                        })
                    
                    panel_entry["onomatopoeia"] = onomatopoeia_list
                    
                except Exception as e:
                    logger.warning(f"Onomatopoeia detection failed: {e}", exc_info=True)
                    panel_entry["onomatopoeia"] = []
            else:
                panel_entry["onomatopoeia"] = []
    
    return chapter_entries


def enhance_json_with_speaker_diarization(
    chapter_entries: List[Dict],
    pages: List[PageImage],
) -> List[Dict]:
    """
    Improve speaker diarization using tail detection and other methods.
    
    Args:
        chapter_entries: List of page entries
        pages: List of PageImage objects
    
    Returns:
        Enhanced chapter entries with improved speaker assignments
    """
    conversation_history: List[Dict] = []
    
    for page_entry, page in zip(chapter_entries, pages):
        panel_entries = page_entry.get("content", [])
        
        for panel_entry in panel_entries:
            # Get panel bbox
            panel_pos = panel_entry["panel"]["panel_position"]
            panel_bbox = [
                panel_pos["x1"],
                panel_pos["y1"],
                panel_pos["x2"],
                panel_pos["y2"],
            ]
            
            # Crop panel image
            x1, y1, x2, y2 = [int(coord) for coord in panel_bbox]
            h, w = page.array.shape[:2]
            x1 = max(0, min(x1, w))
            y1 = max(0, min(y1, h))
            x2 = max(0, min(x2, w))
            y2 = max(0, min(y2, h))
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            panel_image = page.array[y1:y2, x1:x2]
            
            # Get characters in panel
            characters = panel_entry.get("character", [])
            speaker_characters = []
            
            for char_entry in characters:
                char_pos = char_entry["character_position"]
                # Adjust coordinates to panel space
                adj_bbox = [
                    char_pos["x1"] - x1,
                    char_pos["y1"] - y1,
                    char_pos["x2"] - x1,
                    char_pos["y2"] - y1,
                ]
                speaker_char = SpeakerCharacter(
                    bbox=adj_bbox,
                    character_id=char_entry.get("global_character_id", char_entry["character_id"]),
                    character_name=char_entry.get("character_name"),
                )
                speaker_characters.append(speaker_char)
            
            # Update bubbles with improved speaker assignment
            bubbles = panel_entry.get("content", [])
            for bubble in bubbles:
                if "bubble" in bubble:
                    bubble_pos = bubble["bubble"]["bubble_position"]
                    # Adjust to panel space
                    adj_bubble_bbox = [
                        bubble_pos["x1"] - x1,
                        bubble_pos["y1"] - y1,
                        bubble_pos["x2"] - x1,
                        bubble_pos["y2"] - y1,
                    ]
                    
                    speech_bubble = SpeechBubble(
                        bbox=adj_bubble_bbox,
                        text=bubble.get("text", ""),
                        bubble_id=bubble["bubble"]["bubble_id"],
                        panel_idx=0,  # Not used
                    )
                    
                    # Improve speaker assignment
                    updated_bubble = assign_speaker_to_bubble(
                        speech_bubble,
                        speaker_characters,
                        panel_image=panel_image,
                        conversation_history=conversation_history,
                    )
                    
                    # Update bubble entry
                    if updated_bubble.speaker_character_id is not None:
                        bubble["speaker"]["character_id"] = updated_bubble.speaker_character_id
                        bubble["speaker"]["type"] = "character"
                    
                    bubble["speaker"]["method"] = updated_bubble.speaker_method
                    bubble["speaker"]["confidence"] = updated_bubble.confidence
    
    return chapter_entries


def generate_enhanced_json_for_chapter(
    model,
    device,
    manga_name: str,
    chapter_label: str,
    chapter_number: int,
    images: List[Path],
    text_language: str,
    describe_panel=None,
    *,
    pages_per_batch: int = 2,
    max_long_edge: Optional[int] = None,
    ocr_batch_size: int = 16,
    fallback_to_cpu_on_oom: bool = True,
    enable_reading_order: bool = True,
    enable_character_reid: bool = True,
    enable_manpu: bool = True,
    enable_onomatopoeia: bool = True,
    enable_speaker_diarization: bool = True,
) -> List[Dict]:
    """
    Generate enhanced JSON with all new features.
    
    This wraps the base pipeline and adds all enhancements.
    """
    from pipeline_generate_json import prepare_images
    
    # Generate base JSON
    pages, arrays = prepare_images(images, max_long_edge=max_long_edge)
    
    # Call base function (we need to extract pages separately)
    # For now, we'll call the base function and then enhance
    chapter_entries = base_generate_json(
        model=model,
        device=device,
        manga_name=manga_name,
        chapter_label=chapter_label,
        chapter_number=chapter_number,
        images=images,
        text_language=text_language,
        describe_panel=describe_panel,
        pages_per_batch=pages_per_batch,
        max_long_edge=max_long_edge,
        ocr_batch_size=ocr_batch_size,
        fallback_to_cpu_on_oom=fallback_to_cpu_on_oom,
    )
    
    # Enhance with reading order
    if enable_reading_order:
        chapter_entries = enhance_json_with_reading_order(chapter_entries, pages)
    
    # Enhance with character re-ID
    if enable_character_reid:
        feature_extractor = None
        try:
            import torch
            device_str = "cuda" if torch.cuda.is_available() else "cpu"
            feature_extractor = CharacterFeatureExtractor(device=device_str)
        except Exception as e:
            logger.warning(f"Character feature extractor not available: {e}", exc_info=True)
        
        chapter_entries = enhance_json_with_character_reid(
            chapter_entries,
            pages,
            feature_extractor,
        )
    
    # Enhance with manpu detection
    if enable_manpu:
        chapter_entries = enhance_json_with_manpu(chapter_entries, pages)
    
    # Enhance with onomatopoeia
    if enable_onomatopoeia:
        chapter_entries = enhance_json_with_onomatopoeia(chapter_entries, pages)
    
    # Enhance with speaker diarization
    if enable_speaker_diarization:
        chapter_entries = enhance_json_with_speaker_diarization(chapter_entries, pages)
    
    return chapter_entries

