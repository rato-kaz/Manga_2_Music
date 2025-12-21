"""
Character Re-Identification Module for Manga.

This module implements character clustering across pages/chapters
to maintain consistent character identities for voice assignment.
"""

from __future__ import annotations

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import torch
import torch.nn as nn
from PIL import Image
import cv2

from src.infrastructure.logger import get_logger

logger = get_logger(__name__)

BBOX = List[float]  # [x1, y1, x2, y2]


@dataclass
class CharacterDetection:
    """Represents a character detection."""
    page_idx: int
    panel_idx: int
    bbox: BBOX
    character_id: int  # Local ID within page/panel
    character_name: Optional[str] = None
    feature_vector: Optional[np.ndarray] = None


class CharacterFeatureExtractor:
    """
    Feature extractor for character images using CNN.
    
    Uses a pre-trained model (ResNet/EfficientNet) to extract
    feature vectors from character bounding boxes.
    """
    
    def __init__(self, model_name: str = "resnet18", device: str = "cpu"):
        """
        Initialize feature extractor.
        
        Args:
            model_name: Model to use ('resnet18', 'resnet50', 'efficientnet_b0')
            device: 'cpu' or 'cuda'
        """
        self.device = torch.device(device)
        self.model_name = model_name
        
        # Load pre-trained model
        if model_name.startswith("resnet"):
            import torchvision.models as models
            if model_name == "resnet18":
                model = models.resnet18(pretrained=True)
                model.fc = nn.Identity()  # Remove classification head
            elif model_name == "resnet50":
                model = models.resnet50(pretrained=True)
                model.fc = nn.Identity()
            else:
                raise ValueError(f"Unknown ResNet model: {model_name}")
        elif model_name.startswith("efficientnet"):
            try:
                import efficientnet_pytorch
                if model_name == "efficientnet_b0":
                    model = efficientnet_pytorch.EfficientNet.from_pretrained('efficientnet-b0')
                    model._fc = nn.Identity()
                else:
                    raise ValueError(f"Unknown EfficientNet model: {model_name}")
            except ImportError:
                # Fallback to ResNet if efficientnet not available
                logger.warning(
                    "efficientnet-pytorch not installed, using ResNet18 as fallback"
                )
                model = models.resnet18(pretrained=True)
                model.fc = nn.Identity()
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        self.model = model.to(self.device).eval()
        
        # Image preprocessing
        from torchvision import transforms
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
    
    def extract_features(
        self,
        image: np.ndarray,
        bbox: BBOX,
    ) -> np.ndarray:
        """
        Extract feature vector from character bounding box.
        
        Args:
            image: Full page image as numpy array (H, W, 3)
            bbox: Bounding box [x1, y1, x2, y2]
        
        Returns:
            Feature vector as numpy array
        """
        x1, y1, x2, y2 = [int(coord) for coord in bbox]
        
        # Crop character region
        h, w = image.shape[:2]
        x1 = max(0, min(x1, w))
        y1 = max(0, min(y1, h))
        x2 = max(0, min(x2, w))
        y2 = max(0, min(y2, h))
        
        if x2 <= x1 or y2 <= y1:
            # Invalid bbox, return zero vector
            return np.zeros(512)
        
        crop = image[y1:y2, x1:x2]
        
        # Convert to PIL Image
        if len(crop.shape) == 3 and crop.shape[2] == 3:
            pil_image = Image.fromarray(crop.astype(np.uint8))
        else:
            # Grayscale or invalid
            pil_image = Image.fromarray(crop.astype(np.uint8)).convert('RGB')
        
        # Preprocess and extract features
        with torch.no_grad():
            input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            features = self.model(input_tensor)
            features = features.cpu().numpy().flatten()
        
        # Normalize features
        norm = np.linalg.norm(features)
        if norm > 0:
            features = features / norm
        
        return features


def compute_similarity_matrix(
    detections: List[CharacterDetection],
) -> np.ndarray:
    """
    Compute pairwise similarity matrix between character detections.
    
    Uses cosine similarity if features are available, otherwise
    falls back to geometric similarity.
    """
    n = len(detections)
    similarity = np.zeros((n, n))
    
    for i in range(n):
        for j in range(i, n):
            if i == j:
                similarity[i, j] = 1.0
                continue
            
            det_i = detections[i]
            det_j = detections[j]
            
            # Use feature similarity if available
            if det_i.feature_vector is not None and det_j.feature_vector is not None:
                # Cosine similarity
                sim = np.dot(det_i.feature_vector, det_j.feature_vector)
            else:
                # Geometric similarity based on bbox overlap and position
                overlap = bbox_overlap(det_i.bbox, det_j.bbox)
                area_i = bbox_area(det_i.bbox)
                area_j = bbox_area(det_j.bbox)
                
                if area_i > 0 and area_j > 0:
                    iou = overlap / (area_i + area_j - overlap)
                    sim = iou
                else:
                    sim = 0.0
            
            similarity[i, j] = sim
            similarity[j, i] = sim
    
    return similarity


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


def dbscan_clustering(
    detections: List[CharacterDetection],
    eps: float = 0.5,
    min_samples: int = 2,
) -> List[int]:
    """
    Cluster character detections using DBSCAN algorithm.
    
    Args:
        detections: List of character detections
        eps: Maximum distance between samples in same cluster
        min_samples: Minimum samples to form a cluster
    
    Returns:
        List of cluster labels (-1 for noise)
    """
    from sklearn.cluster import DBSCAN
    
    if not detections:
        return []
    
    # Extract feature vectors
    features = []
    for det in detections:
        if det.feature_vector is not None:
            features.append(det.feature_vector)
        else:
            # Fallback: use bbox center and size as features
            x1, y1, x2, y2 = det.bbox
            center_x = (x1 + x2) / 2.0
            center_y = (y1 + y2) / 2.0
            width = x2 - x1
            height = y2 - y1
            features.append(np.array([center_x, center_y, width, height]))
    
    if not features:
        return [-1] * len(detections)
    
    features_array = np.array(features)
    
    # Normalize features
    if features_array.shape[1] > 4:  # Real feature vectors
        # Already normalized in extractor
        pass
    else:
        # Normalize geometric features
        features_array = (features_array - features_array.mean(axis=0)) / (features_array.std(axis=0) + 1e-8)
    
    # Run DBSCAN
    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine' if features_array.shape[1] > 4 else 'euclidean')
    labels = clustering.fit_predict(features_array)
    
    return labels.tolist()


def agglomerative_clustering(
    detections: List[CharacterDetection],
    n_clusters: Optional[int] = None,
    distance_threshold: Optional[float] = None,
) -> List[int]:
    """
    Cluster character detections using Agglomerative Clustering.
    
    Args:
        detections: List of character detections
        n_clusters: Number of clusters (if None, use distance_threshold)
        distance_threshold: Distance threshold for clustering
    
    Returns:
        List of cluster labels
    """
    from sklearn.cluster import AgglomerativeClustering
    
    if not detections:
        return []
    
    # Extract feature vectors
    features = []
    for det in detections:
        if det.feature_vector is not None:
            features.append(det.feature_vector)
        else:
            x1, y1, x2, y2 = det.bbox
            center_x = (x1 + x2) / 2.0
            center_y = (y1 + y2) / 2.0
            width = x2 - x1
            height = y2 - y1
            features.append(np.array([center_x, center_y, width, height]))
    
    if not features:
        return [0] * len(detections)
    
    features_array = np.array(features)
    
    # Normalize if needed
    if features_array.shape[1] <= 4:
        features_array = (features_array - features_array.mean(axis=0)) / (features_array.std(axis=0) + 1e-8)
    
    # Run clustering
    if n_clusters is not None:
        clustering = AgglomerativeClustering(n_clusters=n_clusters, linkage='average')
    elif distance_threshold is not None:
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=distance_threshold,
            linkage='average'
        )
    else:
        # Default: estimate number of clusters
        n_clusters = min(10, len(detections) // 2)
        clustering = AgglomerativeClustering(n_clusters=n_clusters, linkage='average')
    
    labels = clustering.fit_predict(features_array)
    
    return labels.tolist()


def assign_global_character_ids(
    detections: List[CharacterDetection],
    cluster_labels: List[int],
) -> Dict[Tuple[int, int, int], int]:
    """
    Assign global character IDs based on cluster labels.
    
    Args:
        detections: List of character detections
        cluster_labels: Cluster label for each detection
    
    Returns:
        Mapping from (page_idx, panel_idx, local_char_id) to global_char_id
    """
    # Group detections by cluster
    clusters: Dict[int, List[int]] = defaultdict(list)
    for idx, label in enumerate(cluster_labels):
        if label >= 0:  # Ignore noise (-1)
            clusters[label].append(idx)
    
    # Assign global IDs
    global_id_map: Dict[Tuple[int, int, int], int] = {}
    global_id_counter = 1
    
    for cluster_id, detection_indices in sorted(clusters.items()):
        for det_idx in detection_indices:
            det = detections[det_idx]
            key = (det.page_idx, det.panel_idx, det.character_id)
            global_id_map[key] = global_id_counter
        
        global_id_counter += 1
    
    return global_id_map


def reidentify_characters(
    character_detections: List[CharacterDetection],
    method: str = "agglomerative",
    **kwargs,
) -> Dict[Tuple[int, int, int], int]:
    """
    Main function to re-identify characters across pages.
    
    Args:
        character_detections: List of all character detections
        method: Clustering method ('dbscan' or 'agglomerative')
        **kwargs: Additional parameters for clustering
    
    Returns:
        Mapping from (page_idx, panel_idx, local_char_id) to global_char_id
    """
    if not character_detections:
        return {}
    
    # Cluster detections
    if method == "dbscan":
        eps = kwargs.get("eps", 0.5)
        min_samples = kwargs.get("min_samples", 2)
        cluster_labels = dbscan_clustering(character_detections, eps=eps, min_samples=min_samples)
    else:  # agglomerative
        n_clusters = kwargs.get("n_clusters", None)
        distance_threshold = kwargs.get("distance_threshold", 0.5)
        cluster_labels = agglomerative_clustering(
            character_detections,
            n_clusters=n_clusters,
            distance_threshold=distance_threshold,
        )
    
    # Assign global IDs
    global_id_map = assign_global_character_ids(character_detections, cluster_labels)
    
    return global_id_map

