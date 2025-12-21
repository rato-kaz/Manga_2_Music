"""
Image Loading Infrastructure.

Handles loading and preprocessing of manga page images.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import numpy as np
from PIL import Image

from src.domain.entities import PageImage
from src.domain.exceptions import InvalidImageError
from src.domain.constants import SUPPORTED_IMAGE_EXTENSIONS


class ImageLoader:
    """Handles loading and preprocessing of images."""
    
    @staticmethod
    def load_image(image_path: Path) -> PageImage:
        """
        Load image from file path.
        
        Args:
            image_path: Path to image file
            
        Returns:
            PageImage object
            
        Raises:
            InvalidImageError: If image cannot be loaded
        """
        if not image_path.exists():
            raise InvalidImageError(f"Image file not found: {image_path}")
        
        if image_path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            raise InvalidImageError(
                f"Unsupported image format: {image_path.suffix}. "
                f"Supported: {SUPPORTED_IMAGE_EXTENSIONS}"
            )
        
        try:
            with open(image_path, "rb") as handle:
                pil_image = Image.open(handle).convert("RGB")
                image_array = np.array(pil_image)
            
            height, width = image_array.shape[:2]
            
            return PageImage(
                path=image_path,
                image_array=image_array,
                width=width,
                height=height,
            )
        except Exception as e:
            raise InvalidImageError(f"Failed to load image {image_path}: {e}") from e
    
    @staticmethod
    def resize_long_edge(
        image_array: np.ndarray,
        max_long_edge: Optional[int],
    ) -> np.ndarray:
        """
        Resize image so longest edge is at most max_long_edge.
        
        Args:
            image_array: Image as numpy array
            max_long_edge: Maximum length for longest edge (None = no resize)
            
        Returns:
            Resized image array
        """
        if max_long_edge is None:
            return image_array
        
        height, width = image_array.shape[:2]
        long_edge = max(height, width)
        
        if long_edge <= max_long_edge:
            return image_array
        
        scale = max_long_edge / float(long_edge)
        new_width = max(1, int(width * scale))
        new_height = max(1, int(height * scale))
        
        pil_image = Image.fromarray(image_array)
        resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
        
        return np.array(resized_image)
    
    @staticmethod
    def find_chapter_images(root: Path) -> dict[str, List[Path]]:
        """
        Find all chapter images in directory structure.
        
        Args:
            root: Root directory to search
            
        Returns:
            Dictionary mapping chapter labels to image paths
            
        Raises:
            FileNotFoundError: If no images found
        """
        chapter_map: dict[str, List[Path]] = {}
        
        for directory in sorted(root.rglob("*")):
            if not directory.is_dir():
                continue
            
            images = sorted(
                path
                for path in directory.iterdir()
                if path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
                and path.is_file()
            )
            
            if images:
                chapter_key = str(directory.relative_to(root))
                chapter_map[chapter_key] = images
        
        if not chapter_map:
            raise FileNotFoundError(f"No chapter images found under {root}")
        
        return chapter_map

