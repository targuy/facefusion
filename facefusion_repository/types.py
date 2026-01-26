"""
Type definitions for FaceFusion Repository System.

Combines multi-axis orientation, character management, and quality assessment.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeAlias

import numpy
from numpy.typing import NDArray


@dataclass
class QualityMetrics:
    """Quality assessment metrics for a face."""
    resolution: Tuple[int, int]
    sharpness: float  # Laplacian variance
    detector_score: float  # Face detector confidence
    brightness: float  # Mean pixel intensity (normalized)
    contrast: float  # Standard deviation of pixels
    overall_quality: float  # Weighted average, 0.0 to 1.0


@dataclass
class FaceOrientation:
    """
    Multi-axis face orientation (Euler angles in degrees).
    
    Attributes:
        yaw: Horizontal rotation (-180 to 180, 0 is frontal)
        pitch: Vertical tilt (-90 to 90, 0 is level)
        roll: Head rotation/tilt (-180 to 180, 0 is upright)
    """
    yaw: float = 0.0
    pitch: float = 0.0
    roll: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Serialize to dictionary."""
        return {
            'yaw': float(self.yaw),
            'pitch': float(self.pitch),
            'roll': float(self.roll)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'FaceOrientation':
        """Deserialize from dictionary."""
        return cls(
            yaw=data.get('yaw', 0.0),
            pitch=data.get('pitch', 0.0),
            roll=data.get('roll', 0.0)
        )
    
    def get_legacy_angle(self) -> int:
        """
        Get legacy single-axis orientation angle (0-360).
        
        Converts yaw to 0-360 degree range for backward compatibility.
        
        Returns:
            Angle in 0-360 range (e.g., -45 becomes 315)
        """
        angle = self.yaw % 360
        return int(angle)


@dataclass
class FaceMetadata:
    """Metadata for a face entry."""
    added_date: str
    character_name: Optional[str] = None  # Primary identifier for person/character
    face_name: Optional[str] = None  # Optional specific name for this face variant
    tags: List[str] = field(default_factory=list)
    
    # Legacy support
    @property
    def name(self) -> Optional[str]:
        """Legacy name property for backward compatibility."""
        return self.face_name or self.character_name


@dataclass
class FaceEntry:
    """
    Represents a face in the repository.
    
    Attributes:
        id: Unique identifier for the face entry
        file_path: Path to the stored face image file
        orientation: Multi-axis orientation (yaw, pitch, roll) in degrees
        quality_metrics: Quality assessment scores for the face
        face_embedding: 128/512-dimensional feature vector for face recognition
        face_landmarks: Dictionary containing landmark coordinates ('5' and/or '68' point sets)
        metadata: Additional information (name, character, tags, date added)
    """
    id: str
    file_path: str
    orientation: FaceOrientation  # Multi-axis orientation
    quality_metrics: QualityMetrics
    face_embedding: NDArray[numpy.float64]
    face_landmarks: Dict[str, Any]
    metadata: FaceMetadata
    
    # Legacy support
    @property
    def orientation_angle(self) -> int:
        """Legacy single-axis orientation for backward compatibility."""
        return self.orientation.get_legacy_angle()
    
    # For PR #17 compatibility
    @property
    def orientation_3d(self) -> FaceOrientation:
        """Alias for orientation to match PR #17 naming."""
        return self.orientation

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'id': self.id,
            'file_path': self.file_path,
            'orientation': self.orientation.to_dict(),
            'orientation_angle': self.orientation_angle,  # Legacy
            'quality_metrics': {
                'resolution': list(self.quality_metrics.resolution),
                'sharpness': self.quality_metrics.sharpness,
                'detector_score': self.quality_metrics.detector_score,
                'brightness': self.quality_metrics.brightness,
                'contrast': self.quality_metrics.contrast,
                'overall_quality': self.quality_metrics.overall_quality
            },
            'face_embedding': self.face_embedding.tolist(),
            'face_landmarks': self.face_landmarks,
            'metadata': {
                'added_date': self.metadata.added_date,
                'character_name': self.metadata.character_name,
                'face_name': self.metadata.face_name,
                'name': self.metadata.name,  # Legacy field
                'tags': self.metadata.tags
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FaceEntry':
        """Deserialize from dictionary."""
        # Handle both new and legacy orientation formats
        if 'orientation' in data and isinstance(data['orientation'], dict):
            orientation = FaceOrientation.from_dict(data['orientation'])
        else:
            # Legacy format: single orientation_angle
            orientation = FaceOrientation(yaw=float(data.get('orientation_angle', 0)))
        
        # Handle both new and legacy metadata formats
        metadata_data = data['metadata']
        character_name = metadata_data.get('character_name') or metadata_data.get('name')
        face_name = metadata_data.get('face_name')
        
        return cls(
            id=data['id'],
            file_path=data['file_path'],
            orientation=orientation,
            quality_metrics=QualityMetrics(
                resolution=tuple(data['quality_metrics']['resolution']),
                sharpness=data['quality_metrics']['sharpness'],
                detector_score=data['quality_metrics']['detector_score'],
                brightness=data['quality_metrics']['brightness'],
                contrast=data['quality_metrics']['contrast'],
                overall_quality=data['quality_metrics']['overall_quality']
            ),
            face_embedding=numpy.array(data['face_embedding']),
            face_landmarks=data['face_landmarks'],
            metadata=FaceMetadata(
                added_date=metadata_data['added_date'],
                character_name=character_name,
                face_name=face_name,
                tags=metadata_data.get('tags', [])
            )
        )


@dataclass
class Character:
    """Represents a character/person with associated faces."""
    id: str
    name: str
    description: Optional[str] = None
    face_ids: List[str] = field(default_factory=list)
    created_date: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'face_ids': self.face_ids,
            'created_date': self.created_date,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Deserialize from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description'),
            face_ids=data.get('face_ids', []),
            created_date=data.get('created_date'),
            tags=data.get('tags', [])
        )


@dataclass
class QualityThresholds:
    """Thresholds for face quality assessment."""
    min_resolution: Tuple[int, int] = (256, 256)
    min_sharpness: float = 0.3
    min_detector_score: float = 0.5
    min_brightness: float = 0.2
    max_brightness: float = 0.9
    min_contrast: float = 0.1
    min_overall_quality: float = 0.4


DEFAULT_QUALITY_THRESHOLDS = QualityThresholds()


@dataclass
class RepositoryStats:
    """Statistics about the face repository."""
    total_faces: int
    average_quality: float
    total_size_mb: float
    unique_names: int
    faces_by_orientation: Dict[int, int]


@dataclass
class DestinationFace:
    """Represents a detected face in destination media."""
    frame_number: int
    face_data: Any
    orientation_angle: int
    quality_score: float
    timestamp: float


@dataclass
class Match:
    """Represents a match between repository face and destination face."""
    repository_face_id: str
    destination_face: DestinationFace
    confidence: float
    orientation_similarity: float
    quality_ratio: float


@dataclass
class ProcessingQueue:
    """Queue of face swapping operations for a source face."""
    source_face_id: str
    matches: List[Match]
    source_file: str
    created_date: str

    def get_size(self) -> int:
        """Get number of matches in queue."""
        return len(self.matches)

    def get_average_confidence(self) -> float:
        """Calculate average confidence across all matches."""
        if not self.matches:
            return 0.0
        return sum(m.confidence for m in self.matches) / len(self.matches)


@dataclass
class QueueStats:
    """Statistics about processing queues."""
    total_queues: int
    total_faces: int
    average_confidence: float
    queues_by_source_face: Dict[str, int]


@dataclass
class BatchProgress:
    """Progress information for batch processing."""
    current_queue: int
    total_queues: int
    current_face: int
    faces_in_queue: int
    current_operation: str
    elapsed_time: float
    estimated_remaining: float


# Type Aliases with documentation
ProgressCallback: TypeAlias = Callable[[int, int, str], None]
"""Callback function for progress updates.

Args:
    int: Current progress count
    int: Total items count  
    str: Current operation description
"""

OrientationAngle: TypeAlias = int
"""Face orientation angle in degrees (0-360)."""

FaceID: TypeAlias = str
"""Unique identifier for a face entry."""

CharacterID: TypeAlias = str
"""Unique identifier for a character."""
