"""
Type definitions for FaceFusion Repository System.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeAlias

import numpy
from numpy.typing import NDArray

# Re-export FaceFusion types
from facefusion.types import Face


# Repository Types

@dataclass
class QualityMetrics:
    """Quality assessment metrics for a face image."""
    resolution: Tuple[int, int]
    sharpness: float  # 0.0 to 1.0
    detector_score: float  # Face detector confidence
    brightness: float  # 0.0 to 1.0
    contrast: float  # 0.0 to 1.0
    overall_quality: float  # Weighted average, 0.0 to 1.0


@dataclass
class FaceOrientation:
    """
    Multi-axis face orientation.
    
    Attributes:
        yaw: Left-right rotation (-180 to 180, 0 is frontal)
        pitch: Up-down tilt (-90 to 90, 0 is level)
        roll: Head tilt rotation (-180 to 180, 0 is upright)
    """
    yaw: float = 0.0  # Horizontal rotation (legacy orientation_angle)
    pitch: float = 0.0  # Vertical tilt
    roll: float = 0.0  # Head rotation/tilt
    
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
        Input yaw range is -180 to 180 degrees.
        
        Returns:
            Angle in 0-360 range (e.g., -45 becomes 315)
        """
        # Normalize yaw to 0-360 range
        angle = self.yaw % 360
        return int(angle)


@dataclass
class FaceMetadata:
    """Metadata for a face entry."""
    added_date: str
    character_name: Optional[str] = None  # Primary identifier for person/character
    face_name: Optional[str] = None  # Optional specific name for this face (e.g., "frontal", "profile_left")
    tags: List[str] = field(default_factory=list)
    
    # Legacy support
    @property
    def name(self) -> Optional[str]:
        """Legacy name property for backward compatibility."""
        return self.face_name or self.character_name


@dataclass
class FaceEntry:
    """Represents a face in the repository."""
    id: str
    file_path: str
    orientation: FaceOrientation  # Multi-axis orientation (yaw, pitch, roll)
    quality_metrics: QualityMetrics
    face_embedding: NDArray[numpy.float64]
    face_landmarks: Dict[str, Any]
    metadata: FaceMetadata
    
    # Legacy support
    @property
    def orientation_angle(self) -> int:
        """Legacy single-axis orientation for backward compatibility."""
        return self.orientation.get_legacy_angle()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'id': self.id,
            'file_path': self.file_path,
            'orientation': self.orientation.to_dict(),
            # Keep legacy field for backward compatibility
            'orientation_angle': self.orientation_angle,
            'quality_metrics': {
                'resolution': list(self.quality_metrics.resolution),
                'sharpness': float(self.quality_metrics.sharpness),
                'detector_score': float(self.quality_metrics.detector_score),
                'brightness': float(self.quality_metrics.brightness),
                'contrast': float(self.quality_metrics.contrast),
                'overall_quality': float(self.quality_metrics.overall_quality)
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
class QualityThresholds:
    """Thresholds for quality assessment."""
    min_resolution: Tuple[int, int]
    min_sharpness: float
    min_detector_score: float
    min_brightness: float
    max_brightness: float
    min_contrast: float
    min_overall_quality: float


# Default quality thresholds
DEFAULT_QUALITY_THRESHOLDS = QualityThresholds(
    min_resolution=(256, 256),
    min_sharpness=0.3,
    min_detector_score=0.5,
    min_brightness=0.2,
    max_brightness=0.9,
    min_contrast=0.1,
    min_overall_quality=0.4
)


@dataclass
class RepositoryStats:
    """Statistics about the repository."""
    total_faces: int
    faces_by_orientation: Dict[int, int]
    average_quality: float
    total_size_mb: float
    unique_names: int


# Destination Analysis Types

@dataclass
class DetectedFace:
    """Face detected in destination media."""
    face: Face
    orientation: int
    confidence: float
    source_file: str


@dataclass
class FrameFace:
    """Face detected in specific video frame."""
    face: Face
    orientation: int
    frame_number: int
    timestamp: float
    video_path: str
    matched_face_id: Optional[str] = None


@dataclass
class FrameInfo:
    """Information about a video frame."""
    frame_number: int
    timestamp: float
    face_count: int
    faces: List[Face]


@dataclass
class BatchExtractionResult:
    """Result of batch extraction operation."""
    total_files: int
    total_faces: int
    faces_by_orientation: Dict[int, int]
    failed_files: List[str]
    processing_time: float


@dataclass
class QueueStats:
    """Statistics about processing queues."""
    total_queues: int
    total_faces: int
    faces_per_queue: Dict[str, int]
    estimated_time: Optional[float] = None


# Settings Types

@dataclass
class ValidationResult:
    """Result of settings validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# Preset Types

@dataclass
class Preset:
    """Named preset combining face and settings."""
    name: str
    description: str
    face_id: str
    settings_profile: str
    created_date: str
    last_used: Optional[str] = None
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'face_id': self.face_id,
            'settings_profile': self.settings_profile,
            'created_date': self.created_date,
            'last_used': self.last_used,
            'usage_count': self.usage_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Preset':
        """Deserialize from dictionary."""
        return cls(
            name=data['name'],
            description=data['description'],
            face_id=data['face_id'],
            settings_profile=data['settings_profile'],
            created_date=data['created_date'],
            last_used=data.get('last_used'),
            usage_count=data.get('usage_count', 0)
        )


# Batch Processing Types

@dataclass
class QueueResult:
    """Result of processing a single queue."""
    face_id: str
    total_swaps: int
    successful_swaps: int
    failed_swaps: int
    processing_time: float
    errors: List[str] = field(default_factory=list)


@dataclass
class BatchResult:
    """Result of batch processing operation."""
    total_queues: int
    successful_queues: int
    failed_queues: int
    total_swaps: int
    successful_swaps: int
    failed_swaps: int
    total_time: float
    queue_results: List[QueueResult] = field(default_factory=list)


@dataclass
class CoverageReport:
    """Report on orientation coverage in repository."""
    total_orientations: int
    covered_orientations: List[int]
    missing_orientations: List[int]
    coverage_percentage: float
    faces_per_orientation: Dict[int, int]


# Type Aliases
ProgressCallback: TypeAlias = Callable[[int, int, str], None]
OrientationAngle: TypeAlias = int  # 0-360
FaceID: TypeAlias = str
