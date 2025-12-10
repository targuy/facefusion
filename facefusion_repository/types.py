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
class Orientation3D:
    """3D orientation of face (Euler angles in degrees)."""
    yaw: float  # Horizontal rotation (left/right): -180 to 180
    pitch: float  # Vertical tilt (up/down): -90 to 90
    roll: float  # Head rotation (clockwise/counter-clockwise): -180 to 180
    
    def to_dict(self) -> Dict[str, float]:
        """Serialize to dictionary."""
        return {
            'yaw': float(self.yaw),
            'pitch': float(self.pitch),
            'roll': float(self.roll)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Orientation3D':
        """Deserialize from dictionary."""
        return cls(
            yaw=data['yaw'],
            pitch=data['pitch'],
            roll=data['roll']
        )


@dataclass
class FaceMetadata:
    """Metadata for a face entry."""
    added_date: str
    name: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    character_id: Optional[str] = None  # Group faces by character/person


@dataclass
class FaceEntry:
    """Represents a face in the repository."""
    id: str
    file_path: str
    orientation_angle: int  # Legacy: 0, 45, 90, 135, 180, 225, 270, 315 (yaw only)
    quality_metrics: QualityMetrics
    face_embedding: NDArray[numpy.float64]
    face_landmarks: Dict[str, Any]
    metadata: FaceMetadata
    orientation_3d: Optional['Orientation3D'] = None  # New: Full 3D orientation (yaw, pitch, roll)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        result = {
            'id': self.id,
            'file_path': self.file_path,
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
                'name': self.metadata.name,
                'tags': self.metadata.tags,
                'character_id': self.metadata.character_id
            }
        }
        if self.orientation_3d:
            result['orientation_3d'] = self.orientation_3d.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FaceEntry':
        """Deserialize from dictionary."""
        orientation_3d = None
        if 'orientation_3d' in data:
            orientation_3d = Orientation3D.from_dict(data['orientation_3d'])
        
        return cls(
            id=data['id'],
            file_path=data['file_path'],
            orientation_angle=data['orientation_angle'],
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
                added_date=data['metadata']['added_date'],
                name=data['metadata'].get('name'),
                tags=data['metadata'].get('tags', []),
                character_id=data['metadata'].get('character_id')
            ),
            orientation_3d=orientation_3d
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


# Type Aliases
ProgressCallback: TypeAlias = Callable[[int, int, str], None]
OrientationAngle: TypeAlias = int  # 0-360
FaceID: TypeAlias = str
CharacterID: TypeAlias = str
