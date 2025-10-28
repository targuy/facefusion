# FaceFusion Repository System - Technical Specifications

## Version 1.0.0

## Table of Contents
1. [Overview](#overview)
2. [Module 1: Face Repository Management](#module-1-face-repository-management)
3. [Module 2: Destination Face Analysis](#module-2-destination-face-analysis)
4. [Module 3: Settings Management](#module-3-settings-management)
5. [Module 4: Named Presets System](#module-4-named-presets-system)
6. [Module 5: Batch Execution Engine](#module-5-batch-execution-engine)
7. [Data Formats](#data-formats)
8. [API Reference](#api-reference)
9. [CLI Reference](#cli-reference)

## Overview

This document provides detailed technical specifications for the FaceFusion Repository System, a comprehensive extension to the FaceFusion platform for advanced face swap operations with orientation-based matching.

### System Requirements
- Python 3.12+
- FaceFusion core dependencies (see requirements.txt)
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space for repository storage

### Dependencies
All dependencies inherited from FaceFusion core:
- numpy>=2.3.2
- opencv-python>=4.12.0.88
- onnxruntime>=1.22.1
- scipy>=1.16.1

## Module 1: Face Repository Management

### 1.1 Purpose
Manage a collection of source face images with orientation metadata, quality metrics, and compatibility information.

### 1.2 Components

#### 1.2.1 Repository Manager (`repository/manager.py`)

**Class: `RepositoryManager`**

```python
class RepositoryManager:
    """Manages face repository CRUD operations."""
    
    def __init__(self, repository_path: str) -> None:
        """Initialize repository manager with path."""
    
    def initialize_repository(self) -> bool:
        """Create new repository structure."""
    
    def add_face(self, image_path: str, name: Optional[str] = None, 
                 tags: Optional[List[str]] = None) -> Optional[str]:
        """Add new face to repository. Returns face ID or None."""
    
    def get_face(self, face_id: str) -> Optional[FaceEntry]:
        """Retrieve face entry by ID."""
    
    def list_faces(self, filter_by_orientation: Optional[int] = None,
                   filter_by_tags: Optional[List[str]] = None) -> List[FaceEntry]:
        """List all faces with optional filters."""
    
    def remove_face(self, face_id: str) -> bool:
        """Remove face from repository."""
    
    def update_face(self, face_id: str, **kwargs) -> bool:
        """Update face metadata."""
    
    def get_statistics(self) -> RepositoryStats:
        """Get repository statistics."""
```

#### 1.2.2 Face Entry (`repository/face_entry.py`)

**Class: `FaceEntry`**

```python
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
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FaceEntry':
        """Deserialize from dictionary."""
```

**Class: `QualityMetrics`**

```python
@dataclass
class QualityMetrics:
    """Quality assessment metrics for a face image."""
    
    resolution: Tuple[int, int]
    sharpness: float  # 0.0 to 1.0
    detector_score: float  # Face detector confidence
    brightness: float  # 0.0 to 1.0
    contrast: float  # 0.0 to 1.0
    overall_quality: float  # Weighted average, 0.0 to 1.0
```

#### 1.2.3 Quality Assessor (`repository/quality_assessor.py`)

**Class: `QualityAssessor`**

```python
class QualityAssessor:
    """Assesses face image quality."""
    
    @staticmethod
    def assess_face(vision_frame: VisionFrame, face: Face) -> QualityMetrics:
        """Calculate quality metrics for detected face."""
    
    @staticmethod
    def calculate_sharpness(vision_frame: VisionFrame, 
                           bounding_box: BoundingBox) -> float:
        """Calculate Laplacian variance as sharpness metric."""
    
    @staticmethod
    def calculate_brightness(vision_frame: VisionFrame,
                            bounding_box: BoundingBox) -> float:
        """Calculate average brightness in face region."""
    
    @staticmethod
    def calculate_contrast(vision_frame: VisionFrame,
                          bounding_box: BoundingBox) -> float:
        """Calculate standard deviation as contrast metric."""
    
    @staticmethod
    def is_acceptable_quality(metrics: QualityMetrics,
                             thresholds: QualityThresholds) -> bool:
        """Check if quality meets minimum thresholds."""
```

#### 1.2.4 Orientation Matcher (`repository/orientation_matcher.py`)

**Class: `OrientationMatcher`**

```python
class OrientationMatcher:
    """Matches faces based on orientation angles."""
    
    @staticmethod
    def normalize_angle(angle: int) -> int:
        """Normalize angle to 0-360 range."""
    
    @staticmethod
    def get_closest_standard_angle(angle: int) -> int:
        """Map angle to closest standard angle (0, 45, 90, ...)."""
    
    @staticmethod
    def calculate_angle_distance(angle1: int, angle2: int) -> int:
        """Calculate minimum angular distance between two angles."""
    
    @staticmethod
    def find_best_match(target_angle: int, 
                       candidates: List[FaceEntry],
                       max_angle_diff: int = 45) -> Optional[FaceEntry]:
        """Find best matching face based on orientation."""
    
    @staticmethod
    def is_orientation_similar(angle1: int, angle2: int, 
                              threshold: int = 15) -> bool:
        """Check if two orientations are similar enough to be duplicates."""
```

#### 1.2.5 Compatibility Matrix (`repository/compatibility_matrix.py`)

**Class: `CompatibilityMatrix`**

```python
class CompatibilityMatrix:
    """Manages face swap compatibility matrix."""
    
    def __init__(self, repository_manager: RepositoryManager) -> None:
        """Initialize with repository manager."""
    
    def build_matrix(self) -> Dict[int, List[str]]:
        """Build orientation -> face_ids mapping."""
    
    def get_available_orientations(self) -> List[int]:
        """Get list of all available orientations in repository."""
    
    def get_faces_for_orientation(self, orientation: int,
                                  tolerance: int = 45) -> List[FaceEntry]:
        """Get all faces within tolerance of given orientation."""
    
    def visualize_matrix(self) -> str:
        """Generate ASCII visualization of compatibility matrix."""
    
    def get_coverage_report(self) -> CoverageReport:
        """Generate report on orientation coverage."""
```

### 1.3 Quality Thresholds

Default quality thresholds for face acceptance:

```python
DEFAULT_QUALITY_THRESHOLDS = {
    'min_resolution': (256, 256),
    'min_sharpness': 0.3,
    'min_detector_score': 0.5,
    'min_brightness': 0.2,
    'max_brightness': 0.9,
    'min_contrast': 0.1,
    'min_overall_quality': 0.4
}
```

### 1.4 Storage Format

Repository data stored in JSON format at `~/.facefusion_repository/repository.json`:

```json
{
    "version": "1.0.0",
    "created_date": "2025-10-28T08:00:00Z",
    "last_modified": "2025-10-28T10:30:00Z",
    "faces": [
        {
            "id": "face_20251028_001",
            "file_path": "/path/to/face.jpg",
            "orientation_angle": 0,
            "quality_metrics": {
                "resolution": [512, 512],
                "sharpness": 0.75,
                "detector_score": 0.95,
                "brightness": 0.65,
                "contrast": 0.58,
                "overall_quality": 0.82
            },
            "face_embedding": "base64_encoded_array",
            "face_landmarks": {
                "5": [[x1, y1], [x2, y2], ...],
                "68": [[x1, y1], [x2, y2], ...]
            },
            "metadata": {
                "added_date": "2025-10-28T08:15:00Z",
                "name": "Alice Frontal",
                "tags": ["main", "frontal", "high-quality"]
            }
        }
    ]
}
```

## Module 2: Destination Face Analysis

### 2.1 Purpose
Extract faces from destination videos/images, classify their orientations, and match them with repository entries.

### 2.2 Components

#### 2.2.1 Face Extractor (`destination/extractor.py`)

**Class: `DestinationExtractor`**

```python
class DestinationExtractor:
    """Extracts faces from destination media."""
    
    def __init__(self, repository_manager: RepositoryManager) -> None:
        """Initialize with repository manager."""
    
    def extract_from_image(self, image_path: str) -> List[DetectedFace]:
        """Extract all faces from single image."""
    
    def extract_from_video(self, video_path: str,
                          progress_callback: Optional[Callable] = None
                          ) -> List[FrameFace]:
        """Extract faces from all frames in video."""
    
    def extract_from_batch(self, paths: List[str]) -> BatchExtractionResult:
        """Extract faces from multiple files."""
```

#### 2.2.2 Orientation Classifier (`destination/classifier.py`)

**Class: `OrientationClassifier`**

```python
class OrientationClassifier:
    """Classifies face orientations in destination media."""
    
    @staticmethod
    def classify_face_orientation(face: Face) -> int:
        """Determine orientation angle for detected face."""
    
    @staticmethod
    def estimate_confidence(face: Face) -> float:
        """Estimate confidence of orientation classification."""
```

#### 2.2.3 Queue Manager (`destination/queue_manager.py`)

**Class: `QueueManager`**

```python
class QueueManager:
    """Manages batch processing queues."""
    
    def __init__(self) -> None:
        """Initialize empty queue manager."""
    
    def add_to_queue(self, frame_face: FrameFace, 
                     matched_entry: FaceEntry) -> None:
        """Add face to processing queue."""
    
    def get_queues(self) -> Dict[str, List[FrameFace]]:
        """Get all queues organized by source face ID."""
    
    def get_queue_statistics(self) -> QueueStats:
        """Get statistics about current queues."""
    
    def clear_queue(self, face_id: Optional[str] = None) -> None:
        """Clear specific queue or all queues."""
    
    def export_queue(self, output_path: str) -> bool:
        """Export queue to file for later processing."""
    
    def import_queue(self, input_path: str) -> bool:
        """Import queue from file."""
```

#### 2.2.4 Frame Tracker (`destination/frame_tracker.py`)

**Class: `FrameTracker`**

```python
class FrameTracker:
    """Tracks frame sequence information for video processing."""
    
    def __init__(self, video_path: str) -> None:
        """Initialize with video path."""
    
    def add_frame(self, frame_number: int, timestamp: float,
                  faces: List[Face]) -> None:
        """Record frame information."""
    
    def get_frame_info(self, frame_number: int) -> Optional[FrameInfo]:
        """Retrieve frame information."""
    
    def get_total_frames(self) -> int:
        """Get total number of frames tracked."""
    
    def export_tracking_data(self, output_path: str) -> bool:
        """Export tracking data to JSON."""
```

### 2.3 Data Structures

```python
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
class BatchExtractionResult:
    """Result of batch extraction operation."""
    total_files: int
    total_faces: int
    faces_by_orientation: Dict[int, int]
    failed_files: List[str]
    processing_time: float
```

## Module 3: Settings Management

### 3.1 Purpose
Persist and manage FaceFusion configuration parameters.

### 3.2 Components

#### 3.2.1 Settings Manager (`settings/manager.py`)

**Class: `SettingsManager`**

```python
class SettingsManager:
    """Manages FaceFusion settings profiles."""
    
    def __init__(self, settings_path: str) -> None:
        """Initialize with settings directory path."""
    
    def create_profile(self, name: str, settings: Dict[str, Any]) -> bool:
        """Create new settings profile."""
    
    def get_profile(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve settings profile."""
    
    def list_profiles(self) -> List[str]:
        """List all available profiles."""
    
    def delete_profile(self, name: str) -> bool:
        """Delete settings profile."""
    
    def apply_profile(self, name: str) -> bool:
        """Apply settings profile to state_manager."""
    
    def export_profile(self, name: str, output_path: str) -> bool:
        """Export profile to file."""
    
    def import_profile(self, input_path: str, name: str) -> bool:
        """Import profile from file."""
```

#### 3.2.2 Settings Validator (`settings/validator.py`)

**Class: `SettingsValidator`**

```python
class SettingsValidator:
    """Validates settings against FaceFusion requirements."""
    
    @staticmethod
    def validate_settings(settings: Dict[str, Any]) -> ValidationResult:
        """Validate all settings."""
    
    @staticmethod
    def validate_processors(processors: List[str]) -> bool:
        """Validate processor list."""
    
    @staticmethod
    def validate_models(settings: Dict[str, Any]) -> bool:
        """Validate model selections."""
    
    @staticmethod
    def get_available_options() -> Dict[str, List[Any]]:
        """Get all available options for each setting."""
```

### 3.3 Settings Profile Format

```json
{
    "name": "high_quality_swap",
    "description": "High quality face swap settings",
    "version": "1.0.0",
    "settings": {
        "processors": ["face_swapper"],
        "face_selector_mode": "one",
        "face_selector_order": "best-worst",
        "face_detector_model": "yolo_face",
        "face_detector_size": "640x640",
        "face_detector_score": 0.5,
        "face_landmarker_model": "2dfan4",
        "face_landmarker_score": 0.5,
        "face_masker_types": ["box", "region"],
        "face_mask_blur": 0.3,
        "face_mask_padding": [0, 0, 0, 0]
    }
}
```

## Module 4: Named Presets System

### 4.1 Purpose
Create named configurations combining source face and settings profiles.

### 4.2 Components

#### 4.2.1 Preset Manager (`presets/manager.py`)

**Class: `PresetManager`**

```python
class PresetManager:
    """Manages named presets."""
    
    def __init__(self, presets_path: str,
                 repository_manager: RepositoryManager,
                 settings_manager: SettingsManager) -> None:
        """Initialize with paths and managers."""
    
    def create_preset(self, name: str, face_id: str,
                     settings_profile: str,
                     description: Optional[str] = None) -> bool:
        """Create new preset."""
    
    def get_preset(self, name: str) -> Optional[Preset]:
        """Retrieve preset by name."""
    
    def list_presets(self) -> List[str]:
        """List all presets."""
    
    def delete_preset(self, name: str) -> bool:
        """Delete preset."""
    
    def update_preset(self, name: str, **kwargs) -> bool:
        """Update preset properties."""
    
    def run_preset(self, name: str, target_path: str,
                   output_path: str) -> bool:
        """Execute face swap using preset."""
```

### 4.3 Preset Format

```json
{
    "name": "mary_profile_view",
    "description": "Mary's profile view with high quality settings",
    "face_id": "face_20251028_005",
    "settings_profile": "high_quality_swap",
    "created_date": "2025-10-28T12:00:00Z",
    "last_used": "2025-10-28T14:30:00Z",
    "usage_count": 5
}
```

## Module 5: Batch Execution Engine

### 5.1 Purpose
Process multiple face swaps efficiently using queued operations.

### 5.2 Components

#### 5.2.1 Batch Executor (`batch/executor.py`)

**Class: `BatchExecutor`**

```python
class BatchExecutor:
    """Executes batch face swap operations."""
    
    def __init__(self, queue_manager: QueueManager,
                 repository_manager: RepositoryManager) -> None:
        """Initialize with managers."""
    
    def execute_batch(self, output_path: str,
                     progress_callback: Optional[Callable] = None) -> BatchResult:
        """Execute all queued swaps."""
    
    def execute_queue(self, face_id: str, output_path: str) -> QueueResult:
        """Execute swaps for specific source face."""
    
    def process_video(self, video_path: str, queue: List[FrameFace],
                     source_face: FaceEntry, output_path: str) -> bool:
        """Process single video with face swaps."""
```

#### 5.2.2 Progress Tracker (`batch/progress_tracker.py`)

**Class: `ProgressTracker`**

```python
class ProgressTracker:
    """Tracks batch processing progress."""
    
    def __init__(self, total_items: int) -> None:
        """Initialize with total items."""
    
    def update(self, completed: int) -> None:
        """Update progress."""
    
    def get_eta(self) -> float:
        """Estimate time remaining."""
    
    def get_progress_string(self) -> str:
        """Get formatted progress string."""
```

### 5.3 Batch Processing Flow

1. **Queue Organization**: Group faces by source face ID
2. **Sequential Processing**: Process each queue separately
3. **Frame Tracking**: Maintain frame order for videos
4. **Error Handling**: Skip failed swaps, log errors
5. **Output Assembly**: Combine processed frames into video
6. **Progress Reporting**: Update progress after each item

## Data Formats

### Repository Database
- **File**: `~/.facefusion_repository/repository.json`
- **Format**: JSON with version, metadata, and face entries array

### Settings Profiles
- **Directory**: `~/.facefusion_repository/settings/`
- **Format**: Individual JSON files named `{profile_name}.json`

### Presets Database
- **File**: `~/.facefusion_repository/presets.json`
- **Format**: JSON with array of preset objects

### Queue Export
- **Format**: JSON with queue data and frame tracking info
- **Extension**: `.queue.json`

## CLI Reference

### Repository Commands

```bash
# Initialize repository
python facefusion.py repo-init

# Add face to repository
python facefusion.py repo-add-face --source path/to/face.jpg [--name "Name"] [--tags tag1,tag2]

# List faces
python facefusion.py repo-list [--orientation 0] [--tags tag1,tag2]

# Show face details
python facefusion.py repo-show --face-id face_001

# Remove face
python facefusion.py repo-remove --face-id face_001

# Show statistics
python facefusion.py repo-stats
```

### Destination Analysis Commands

```bash
# Analyze target media
python facefusion.py repo-analyze-target --target path/to/video.mp4

# Match with repository
python facefusion.py repo-match --target path/to/video.mp4 [--max-angle-diff 45]

# Show queue
python facefusion.py repo-queue-show

# Clear queue
python facefusion.py repo-queue-clear [--face-id face_001]
```

### Settings Commands

```bash
# Create settings profile
python facefusion.py settings-create --name profile_name [--from-current]

# List profiles
python facefusion.py settings-list

# Show profile
python facefusion.py settings-show --name profile_name

# Delete profile
python facefusion.py settings-delete --name profile_name

# Apply profile
python facefusion.py settings-apply --name profile_name
```

### Preset Commands

```bash
# Create preset
python facefusion.py preset-create --name preset_name --face-id face_001 --settings profile_name

# List presets
python facefusion.py preset-list

# Show preset
python facefusion.py preset-show --name preset_name

# Delete preset
python facefusion.py preset-delete --name preset_name

# Run preset
python facefusion.py preset-run --name preset_name --target input.mp4 --output output.mp4
```

### Batch Commands

```bash
# Execute batch queue
python facefusion.py batch-run --output output_directory

# Show batch status
python facefusion.py batch-status
```

## Error Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | File not found |
| 4 | Face detection failed |
| 5 | Quality check failed |
| 6 | No matching face found |
| 7 | Processing error |
| 8 | Repository error |

## Performance Specifications

### Expected Performance
- Face addition: < 5 seconds per face
- Repository search: < 100ms for 1000 faces
- Video analysis: Real-time to 2x real-time depending on face count
- Batch processing: 80-90% of single swap performance per face

### Memory Requirements
- Base memory: ~2GB
- Per face in memory: ~50MB
- Video processing buffer: ~1GB per concurrent video

### Storage Requirements
- Per face entry: ~1MB (including embeddings)
- Settings profile: ~10KB
- Queue data: ~100KB per 1000 frames
- Temporary files: ~2x input video size during processing
