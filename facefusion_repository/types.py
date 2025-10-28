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
class FaceMetadata:
    """Metadata for a face entry."""
    added_date: str
    person: str  # Mandatory person name (replaces collection concept)
    name: Optional[str] = None  # Optional descriptive name (e.g., "frontal", "profile")
    tags: List[str] = field(default_factory=list)


@dataclass
class FaceEntry:
    """Represents a face in the repository."""
    id: str
    file_path: str
    orientation_angle: int  # 0, 45, 90, 135, 180, 225, 270, 315
    quality_metrics: QualityMetrics
    face_embedding: NDArray[numpy.float64]
    face_landmarks: Dict[str, Any]
    metadata: FaceMetadata
    # 3D orientation data (pitch/yaw/tilt)
    pitch: Optional[float] = None  # Up/down angle
    yaw: Optional[float] = None  # Left/right angle
    tilt: Optional[float] = None  # Rotation angle
    occlusion_score: Optional[float] = None  # 0.0-1.0, lower is better

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
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
                'person': self.metadata.person,
                'name': self.metadata.name,
                'tags': self.metadata.tags
            },
            'pitch': self.pitch,
            'yaw': self.yaw,
            'tilt': self.tilt,
            'occlusion_score': self.occlusion_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FaceEntry':
        """Deserialize from dictionary."""
        # Support both old format (without person) and new format
        metadata_data = data['metadata']
        person = metadata_data.get('person')
        
        # Migration: use 'name' as person if person is not present (backward compatibility)
        if person is None:
            person = metadata_data.get('name', 'unknown')
        
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
                added_date=metadata_data['added_date'],
                person=person,
                name=metadata_data.get('name'),
                tags=metadata_data.get('tags', [])
            ),
            pitch=data.get('pitch'),
            yaw=data.get('yaw'),
            tilt=data.get('tilt'),
            occlusion_score=data.get('occlusion_score')
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


# GPU Types

@dataclass
class GPUInfo:
    """Information about available GPU."""
    device_id: int
    name: str
    memory_total: int  # MB
    memory_available: int  # MB
    compute_capability: Optional[str] = None
    driver_version: Optional[str] = None


@dataclass
class GPUConfig:
    """GPU configuration settings."""
    enabled: bool = True
    device_ids: List[int] = field(default_factory=lambda: [0])
    memory_limit: Optional[int] = None  # MB
    providers: List[str] = field(default_factory=lambda: ['CUDAExecutionProvider', 'CPUExecutionProvider'])


# Preview System Types

@dataclass
class PreviewResult:
    """Result of preview operation."""
    success: bool
    preview_path: Optional[str] = None
    quality_score: Optional[float] = None
    orientation_match: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class TestImage:
    """Test image for preview system."""
    path: str
    orientation_angle: int
    face_count: int
    best_face_quality: float


# 3D Orientation Types

@dataclass
class Pose3D:
    """3D pose estimation data."""
    pitch: float  # Up/down rotation (-90 to 90)
    yaw: float  # Left/right rotation (-90 to 90)
    tilt: float  # Head tilt (-180 to 180)
    confidence: float  # 0.0 to 1.0


@dataclass
class OcclusionInfo:
    """Face occlusion information."""
    score: float  # 0.0 (no occlusion) to 1.0 (fully occluded)
    occluded_landmarks: List[str]  # Names of occluded landmarks
    is_usable: bool  # Whether face is usable despite occlusion


# FaceFusion Integration Types

@dataclass
class DestinationSelectionSettings:
    """FaceFusion destination selection settings."""
    face_selector_mode: str = 'reference'  # 'reference', 'one', 'many', 'best-quality', etc.
    face_index: Optional[int] = None
    reference_face_position: int = 0
    reference_face_distance: float = 0.6
    reference_frame_number: int = 0


@dataclass
class QueueEntry:
    """Enhanced queue entry with FaceFusion destination selection."""
    queue_id: str
    source_person: str  # Person name
    source_face_id: str
    destination_media: str
    destination_selection: DestinationSelectionSettings
    processing_settings: Optional[str] = None  # Settings profile name
    created_date: Optional[str] = None
    status: str = 'pending'  # 'pending', 'processing', 'completed', 'failed'


# Type Aliases
ProgressCallback: TypeAlias = Callable[[int, int, str], None]
OrientationAngle: TypeAlias = int  # 0-360
FaceID: TypeAlias = str
PersonName: TypeAlias = str
