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
class PoseEstimation:
    """3D pose estimation for a face."""
    pitch: float  # Head rotation up/down (-90 to 90 degrees)
    yaw: float  # Head rotation left/right (-90 to 90 degrees)
    tilt: float  # Head tilt/roll (-180 to 180 degrees)


@dataclass
class OcclusionData:
    """Occlusion detection data for face quality."""
    is_occluded: bool
    occlusion_score: float  # 0.0 (no occlusion) to 1.0 (fully occluded)
    occluded_regions: List[str] = field(default_factory=list)  # e.g., ['eyes', 'mouth']


@dataclass
class QualityMetrics:
    """Quality assessment metrics for a face image."""
    resolution: Tuple[int, int]
    sharpness: float  # 0.0 to 1.0
    detector_score: float  # Face detector confidence
    brightness: float  # 0.0 to 1.0
    contrast: float  # 0.0 to 1.0
    overall_quality: float  # Weighted average, 0.0 to 1.0
    pose: Optional[PoseEstimation] = None
    occlusion: Optional[OcclusionData] = None


@dataclass
class FaceMetadata:
    """Metadata for a face entry."""
    added_date: str
    person_id: str  # Person this face belongs to (MANDATORY)
    name: Optional[str] = None  # Optional descriptive name for this specific face
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

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        quality_dict = {
            'resolution': list(self.quality_metrics.resolution),
            'sharpness': float(self.quality_metrics.sharpness),
            'detector_score': float(self.quality_metrics.detector_score),
            'brightness': float(self.quality_metrics.brightness),
            'contrast': float(self.quality_metrics.contrast),
            'overall_quality': float(self.quality_metrics.overall_quality)
        }
        
        if self.quality_metrics.pose:
            quality_dict['pose'] = {
                'pitch': float(self.quality_metrics.pose.pitch),
                'yaw': float(self.quality_metrics.pose.yaw),
                'tilt': float(self.quality_metrics.pose.tilt)
            }
        
        if self.quality_metrics.occlusion:
            quality_dict['occlusion'] = {
                'is_occluded': self.quality_metrics.occlusion.is_occluded,
                'occlusion_score': float(self.quality_metrics.occlusion.occlusion_score),
                'occluded_regions': self.quality_metrics.occlusion.occluded_regions
            }
        
        return {
            'id': self.id,
            'file_path': self.file_path,
            'orientation_angle': self.orientation_angle,
            'quality_metrics': quality_dict,
            'face_embedding': self.face_embedding.tolist(),
            'face_landmarks': self.face_landmarks,
            'metadata': {
                'added_date': self.metadata.added_date,
                'person_id': self.metadata.person_id,
                'name': self.metadata.name,
                'tags': self.metadata.tags
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FaceEntry':
        """Deserialize from dictionary."""
        qm_data = data['quality_metrics']
        
        pose = None
        if 'pose' in qm_data:
            pose = PoseEstimation(
                pitch=qm_data['pose']['pitch'],
                yaw=qm_data['pose']['yaw'],
                tilt=qm_data['pose']['tilt']
            )
        
        occlusion = None
        if 'occlusion' in qm_data:
            occlusion = OcclusionData(
                is_occluded=qm_data['occlusion']['is_occluded'],
                occlusion_score=qm_data['occlusion']['occlusion_score'],
                occluded_regions=qm_data['occlusion'].get('occluded_regions', [])
            )
        
        return cls(
            id=data['id'],
            file_path=data['file_path'],
            orientation_angle=data['orientation_angle'],
            quality_metrics=QualityMetrics(
                resolution=tuple(qm_data['resolution']),
                sharpness=qm_data['sharpness'],
                detector_score=qm_data['detector_score'],
                brightness=qm_data['brightness'],
                contrast=qm_data['contrast'],
                overall_quality=qm_data['overall_quality'],
                pose=pose,
                occlusion=occlusion
            ),
            face_embedding=numpy.array(data['face_embedding']),
            face_landmarks=data['face_landmarks'],
            metadata=FaceMetadata(
                added_date=data['metadata']['added_date'],
                person_id=data['metadata'].get('person_id', 'unknown'),  # Backward compat
                name=data['metadata'].get('name'),
                tags=data['metadata'].get('tags', [])
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
class PersonEntry:
    """Represents a person in the repository."""
    id: str  # person identifier (alphanumeric, no spaces)
    display_name: str  # Human-readable name
    face_ids: List[str] = field(default_factory=list)  # List of face IDs for this person
    created_date: str = ''
    last_modified: str = ''
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'id': self.id,
            'display_name': self.display_name,
            'face_ids': self.face_ids,
            'created_date': self.created_date,
            'last_modified': self.last_modified,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonEntry':
        """Deserialize from dictionary."""
        return cls(
            id=data['id'],
            display_name=data['display_name'],
            face_ids=data.get('face_ids', []),
            created_date=data.get('created_date', ''),
            last_modified=data.get('last_modified', ''),
            metadata=data.get('metadata', {})
        )


@dataclass
class RepositoryStats:
    """Statistics about the repository."""
    total_faces: int
    total_people: int  # New field for person count
    faces_by_orientation: Dict[int, int]
    faces_by_person: Dict[str, int]  # New field for faces per person
    average_quality: float
    total_size_mb: float
    unique_names: int  # Deprecated, kept for compatibility


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
class FaceFusionSettings:
    """FaceFusion processing settings profile."""
    name: str
    description: str
    parameters: Dict[str, Any]  # Direct FaceFusion parameters
    created_date: str
    last_modified: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'created_date': self.created_date,
            'last_modified': self.last_modified
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FaceFusionSettings':
        """Deserialize from dictionary."""
        return cls(
            name=data['name'],
            description=data['description'],
            parameters=data['parameters'],
            created_date=data['created_date'],
            last_modified=data['last_modified']
        )


@dataclass
class ValidationResult:
    """Result of settings validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# Preset Types

@dataclass
class Preset:
    """Named preset combining person and settings."""
    name: str
    description: str
    person_id: str  # Changed from face_id to person_id
    settings_name: str  # Reference to FaceFusionSettings by name
    created_date: str
    last_used: Optional[str] = None
    usage_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'person_id': self.person_id,
            'settings_name': self.settings_name,
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
            person_id=data.get('person_id', data.get('face_id', '')),  # Backward compat
            settings_name=data.get('settings_name', data.get('settings_profile', '')),  # Backward compat
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
