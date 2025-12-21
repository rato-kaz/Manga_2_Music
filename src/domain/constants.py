"""
Domain Constants: Constants used across the domain layer.

These constants define domain-specific values and configurations.
"""

from typing import Dict, List

# Reading speed constants
WORDS_PER_MINUTE: int = 200
CHARACTERS_PER_MINUTE: int = 1000  # For Japanese/Chinese
MIN_PANEL_TIME_SECONDS: float = 2.0
MAX_PANEL_TIME_SECONDS: float = 30.0

# Gutter detection
MIN_GUTTER_SIZE: float = 10.0

# Scene type keywords
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

# Manpu to emotion mapping
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

# Image file extensions
SUPPORTED_IMAGE_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".webp"}

# Audio sample rate
DEFAULT_SAMPLE_RATE: int = 44100

# Audio volume defaults
DEFAULT_BGM_VOLUME: float = 0.7
DEFAULT_SFX_VOLUME: float = 1.0
DEFAULT_DIALOGUE_VOLUME: float = 1.0

# Character clustering
DEFAULT_CLUSTERING_EPS: float = 0.5
DEFAULT_MIN_SAMPLES: int = 2

# Reading order
DEFAULT_4KOMA_THRESHOLD: float = 0.8  # Panel width threshold for 4-koma detection

