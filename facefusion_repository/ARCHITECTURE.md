# FaceFusion Repository System - Architecture

## Overview

The FaceFusion Repository System extends the core FaceFusion platform with advanced capabilities for managing multiple source faces with orientation-based matching, intelligent batch processing, and preset management.

## Design Principles

1. **Non-Invasive Integration**: All new code exists in separate directory (`facefusion_repository/`)
2. **Leverage Existing Code**: Use FaceFusion's existing modules for core functionality
3. **Environment Compatibility**: Use same dependencies and Python environment as FaceFusion
4. **CLI First, GUI Later**: Build command-line interface first, then add GUI
5. **Data Portability**: Use JSON for configuration and repository storage

## System Architecture

### Module Structure

```
facefusion_repository/
├── __init__.py              # Package initialization
├── ARCHITECTURE.md          # This file
├── SPECIFICATIONS.md        # Detailed specifications
├── MANUAL.md               # User manual
├── types.py                # Type definitions
├── repository/             # Module 1: Face Repository Management
│   ├── __init__.py
│   ├── manager.py          # Repository CRUD operations
│   ├── face_entry.py       # Face entry data structure
│   ├── quality_assessor.py # Face quality assessment
│   ├── orientation_matcher.py # Orientation matching logic
│   └── compatibility_matrix.py # Face swap compatibility
├── destination/            # Module 2: Destination Analysis
│   ├── __init__.py
│   ├── extractor.py        # Face extraction from frames
│   ├── classifier.py       # Orientation classification
│   ├── queue_manager.py    # Batch queue management
│   └── frame_tracker.py    # Video frame sequencing
├── settings/               # Module 3: Settings Management
│   ├── __init__.py
│   ├── manager.py          # Settings CRUD
│   └── validator.py        # Settings validation
├── presets/                # Module 4: Named Presets
│   ├── __init__.py
│   └── manager.py          # Preset management
├── batch/                  # Module 5: Batch Execution
│   ├── __init__.py
│   ├── executor.py         # Batch processing engine
│   └── progress_tracker.py # Progress tracking
├── cli/                    # Command-Line Interface
│   ├── __init__.py
│   ├── commands.py         # CLI command definitions
│   └── parser.py           # Argument parser
└── ui/                     # Graphical User Interface (Future)
    ├── __init__.py
    └── components.py       # UI components
```

## Core Components

### 1. Face Repository Management

**Purpose**: Store and manage multiple source face images with orientation metadata.

**Key Features**:
- Face storage with orientation angles (0°, 90°, 180°, 270°, and intermediate angles)
- Automatic quality assessment (resolution, sharpness, face detection confidence)
- Duplicate detection based on orientation similarity
- Compatibility matrix showing possible swaps

**Data Structure**:
```python
FaceEntry = {
    'id': str,                    # Unique identifier
    'file_path': str,             # Path to source image
    'orientation_angle': int,     # Face angle (0-360)
    'quality_metrics': {
        'resolution': Tuple[int, int],
        'sharpness': float,
        'detector_score': float,
        'overall_quality': float
    },
    'face_embedding': NDArray,    # Face recognition embedding
    'face_landmarks': Dict,       # Facial landmarks
    'metadata': {
        'added_date': str,
        'name': str,              # Optional user-defined name
        'tags': List[str]
    }
}
```

### 2. Destination Face Analysis

**Purpose**: Extract and classify faces from destination videos/images, matching them with repository entries.

**Key Features**:
- Frame-by-frame face detection and extraction
- Orientation angle estimation for each detected face
- Matching algorithm to find best repository face for each detected face
- Queue system organizing faces by matched source
- Frame sequence tracking for video reassembly

**Processing Flow**:
```
Input Video/Images
    ↓
Frame Extraction
    ↓
Face Detection (per frame)
    ↓
Orientation Estimation
    ↓
Repository Matching
    ↓
Queue Assignment
    ↓
Batch Processing
    ↓
Video Reassembly
```

### 3. Settings Management

**Purpose**: Persist and manage FaceFusion configuration parameters.

**Key Features**:
- Store processor settings (models, masks, etc.)
- Validation against available options
- Import/export settings profiles
- Version compatibility checking

**Settings Structure**:
```python
Settings = {
    'processors': List[str],
    'face_selector_mode': str,
    'face_analyser_order': str,
    'face_detector_model': str,
    'face_detector_size': str,
    'face_detector_score': float,
    'face_landmarker_model': str,
    'face_masker_types': List[str],
    # ... other FaceFusion parameters
}
```

### 4. Named Presets System

**Purpose**: Create named configurations combining source face and settings.

**Key Features**:
- Named preset creation (e.g., "Mary profile view")
- Association of repository face ID with settings profile
- Quick preset selection for batch operations
- Preset sharing/export capability

**Preset Structure**:
```python
Preset = {
    'name': str,
    'description': str,
    'face_id': str,              # Reference to FaceEntry.id
    'settings_id': str,          # Reference to Settings profile
    'created_date': str,
    'last_used': str
}
```

### 5. Batch Execution Engine

**Purpose**: Process multiple face swaps efficiently using queued operations.

**Key Features**:
- Queue-based batch processing
- Progress tracking with ETA
- Error handling and retry logic
- Integration with existing FaceFusion processing pipeline
- Parallel processing support

**Batch Processing Strategy**:
1. Group destination faces by matched source face
2. Process each group with same source in single batch
3. Track frame/timecode information
4. Reassemble video in correct sequence
5. Handle failures gracefully

## Data Storage

### Repository Database
- **Format**: JSON
- **Location**: `~/.facefusion_repository/repository.json`
- **Structure**: List of FaceEntry objects with metadata

### Settings Profiles
- **Format**: JSON
- **Location**: `~/.facefusion_repository/settings/`
- **Files**: Individual JSON files per profile

### Presets
- **Format**: JSON
- **Location**: `~/.facefusion_repository/presets.json`
- **Structure**: List of Preset objects

### Temporary Files
- **Location**: `~/.facefusion_repository/temp/`
- **Purpose**: Intermediate processing files
- **Cleanup**: Automatic after batch completion

## Integration with FaceFusion

### Reused Components
- `face_analyser.py`: Face detection and analysis
- `face_detector.py`: Face detection models
- `face_landmarker.py`: Facial landmark detection
- `face_helper.py`: Angle estimation, warping
- `face_recognizer.py`: Face embeddings
- `processors/modules/face_swapper.py`: Face swapping logic
- `ffmpeg.py`: Video processing
- `vision.py`: Image I/O operations

### New vs. Existing Functionality

| Feature | Implementation |
|---------|---------------|
| Face Detection | Use existing `face_detector` |
| Face Recognition | Use existing `face_recognizer` |
| Orientation Estimation | Use existing `face_helper.estimate_face_angle()` |
| Face Swapping | Use existing `face_swapper` processor |
| Quality Assessment | New implementation |
| Repository Management | New implementation |
| Queue System | New implementation |
| Batch Coordination | New implementation |
| Preset Management | New implementation |

## CLI Interface Design

### Command Structure
```bash
python facefusion.py repo-* [options]  # Repository commands
```

### Available Commands
```
repo-init              Initialize new repository
repo-add-face          Add face to repository
repo-list              List faces in repository
repo-remove            Remove face from repository
repo-show              Show face details
repo-stats             Show repository statistics

repo-analyze-target    Analyze target video/images
repo-match             Match target with repository
repo-queue-show        Show current batch queue
repo-queue-clear       Clear batch queue

settings-create        Create settings profile
settings-list          List settings profiles
settings-show          Show settings details
settings-delete        Delete settings profile

preset-create          Create named preset
preset-list            List presets
preset-show            Show preset details
preset-delete          Delete preset
preset-run             Run preset on target

batch-run              Execute batch queue
batch-status           Show batch status
```

## Error Handling

### Face Quality Issues
- If face not detected: Log warning, skip entry
- If quality below threshold: Warn user, allow override
- If orientation unclear: Assign to nearest standard angle

### Processing Errors
- Frame extraction failure: Skip frame, log error
- Face swap failure: Skip swap, continue processing
- Video reassembly error: Save processed frames, report error

### Data Integrity
- Repository corruption: Backup and rebuild
- Missing files: Warn user, offer cleanup
- Duplicate entries: Detect and merge

## Performance Considerations

### Optimization Strategies
1. **Batch Processing**: Process multiple faces with same source together
2. **Caching**: Cache face embeddings and quality metrics
3. **Parallel Processing**: Use FaceFusion's existing threading
4. **Memory Management**: Stream video processing for large files
5. **Index Building**: Build orientation index for fast matching

### Scalability Limits
- Repository size: ~1000 faces recommended maximum
- Video length: No hard limit, memory-based streaming
- Batch size: Limited by available memory
- Queue depth: No hard limit

## Testing Strategy

### Unit Tests
- Repository CRUD operations
- Quality assessment algorithms
- Orientation matching logic
- Settings validation
- Preset management

### Integration Tests
- End-to-end batch processing
- Video frame sequencing
- Repository-to-processor pipeline
- CLI command execution

### Performance Tests
- Large repository operations
- Long video processing
- Memory usage monitoring
- Concurrent operation handling

## Future Enhancements

### Phase 2 (GUI Implementation)
- Visual repository browser
- Interactive face matching preview
- Drag-and-drop batch queue
- Real-time progress visualization
- Preset management interface

### Phase 3 (Advanced Features)
- Machine learning-based quality prediction
- Automatic orientation correction
- Multi-face scenarios handling
- Cloud storage integration
- Collaborative repository sharing

## Security Considerations

1. **Input Validation**: Validate all file paths and user inputs
2. **Safe File Operations**: Use safe file handling practices
3. **Privacy**: No automatic upload of face data
4. **Access Control**: File-system based (OS permissions)
5. **Dependency Security**: Regular security audits of dependencies
