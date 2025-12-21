"""
Domain Entities: Core business objects.

These are the fundamental building blocks of the domain model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
import numpy as np


@dataclass(frozen=True)
class BoundingBox:
    """Immutable bounding box value object."""
    x1: float
    y1: float
    x2: float
    y2: float
    
    @property
    def center(self) -> tuple[float, float]:
        """Get center point of bounding box."""
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)
    
    @property
    def width(self) -> float:
        """Get width of bounding box."""
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        """Get height of bounding box."""
        return self.y2 - self.y1
    
    @property
    def area(self) -> float:
        """Get area of bounding box."""
        return max(0.0, self.width * self.height)
    
    def to_list(self) -> List[float]:
        """Convert to list format [x1, y1, x2, y2]."""
        return [self.x1, self.y1, self.x2, self.y2]
    
    @classmethod
    def from_list(cls, bbox: List[float]) -> BoundingBox:
        """Create from list format [x1, y1, x2, y2]."""
        if len(bbox) != 4:
            raise ValueError(f"BoundingBox requires 4 values, got {len(bbox)}")
        return cls(x1=bbox[0], y1=bbox[1], x2=bbox[2], y2=bbox[3])


@dataclass
class PageImage:
    """Represents a manga page image."""
    path: Path
    image_array: np.ndarray
    width: int
    height: int
    
    def __post_init__(self) -> None:
        """Validate image dimensions."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"Invalid image dimensions: {self.width}x{self.height}")


@dataclass
class Panel:
    """Represents a manga panel."""
    panel_id: int
    bounding_box: BoundingBox
    reading_order: Optional[int] = None
    characters: List[Character] = field(default_factory=list)
    speech_bubbles: List[SpeechBubble] = field(default_factory=list)
    manpu_detections: List[ManpuDetection] = field(default_factory=list)
    onomatopoeia_detections: List[OnomatopoeiaDetection] = field(default_factory=list)
    scene_context: Optional[SceneContext] = None
    timeline: Optional[TimelineEntry] = None


@dataclass
class Character:
    """Represents a character in manga."""
    character_id: int
    global_character_id: Optional[int] = None
    name: Optional[str] = None
    bounding_box: Optional[BoundingBox] = None
    voice_profile_id: Optional[int] = None


@dataclass
class SpeechBubble:
    """Represents a speech bubble."""
    bubble_id: int
    text: str
    language: str
    bounding_box: BoundingBox
    speaker: Speaker
    is_dialogue: bool = True
    speech_audio_path: Optional[Path] = None


@dataclass
class Speaker:
    """Represents the speaker of a speech bubble."""
    speaker_type: str  # 'character' or 'narrator'
    character_id: Optional[int] = None
    character_name: Optional[str] = None
    assignment_method: Optional[str] = None  # 'tail', 'geometric', 'llm'
    confidence: float = 0.0


@dataclass
class ManpuDetection:
    """Represents a detected manpu (emotion symbol)."""
    manpu_type: str  # 'vein', 'sweat', 'sparkles', etc.
    bounding_box: BoundingBox
    emotion_tags: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class OnomatopoeiaDetection:
    """Represents a detected onomatopoeia."""
    visual_form: str
    onomatopoeia_type: str  # 'giongo' or 'gitaigo'
    bounding_box: BoundingBox
    audio_keywords: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class SceneContext:
    """Represents semantic context of a scene."""
    scene_type: str  # 'battle', 'romance', 'comedy', etc.
    location: Optional[str] = None
    time_of_day: Optional[str] = None
    mood: str = "neutral"
    intensity: float = 0.5  # 0.0 to 1.0
    emotion_tags: List[str] = field(default_factory=list)


@dataclass
class TimelineEntry:
    """Represents timeline information for a panel."""
    panel_id: int
    start_time: float  # seconds
    end_time: float  # seconds
    duration: float  # seconds
    reading_time: float  # seconds
    viewing_time: float  # seconds


@dataclass
class Page:
    """Represents a manga page."""
    page_id: int
    manga_name: str
    chapter_number: int
    page_image: PageImage
    panels: List[Panel] = field(default_factory=list)
    width: int = 0
    height: int = 0
    
    def __post_init__(self) -> None:
        """Set dimensions from image if not provided."""
        if self.width == 0:
            self.width = self.page_image.width
        if self.height == 0:
            self.height = self.page_image.height


@dataclass
class Chapter:
    """Represents a manga chapter."""
    chapter_number: int
    manga_name: str
    pages: List[Page] = field(default_factory=list)
    
    @property
    def total_panels(self) -> int:
        """Get total number of panels in chapter."""
        return sum(len(page.panels) for page in self.pages)
    
    @property
    def total_duration(self) -> float:
        """Get total duration in seconds."""
        total = 0.0
        for page in self.pages:
            for panel in page.panels:
                if panel.timeline:
                    total += panel.timeline.duration
        return total

