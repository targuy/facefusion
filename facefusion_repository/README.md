# FaceFusion Repository System

Advanced face repository management with person-based organization, 3D pose estimation, GPU acceleration, and preview system for the FaceFusion platform.

## Overview

The FaceFusion Repository System extends FaceFusion with sophisticated capabilities for managing source faces organized by person, enabling high-quality face swaps with intelligent orientation matching, occlusion detection, and seamless FaceFusion integration.

### Key Features

- **Person-Based Organization**: Simple flat directory structure (`faces/marc/`, `faces/alice/`)
- **Mandatory Person Names**: Every face belongs to a person - no more confusing collections
- **3D Pose Estimation**: Full pitch/yaw/tilt analysis with automatic pose filtering
- **Occlusion Detection**: Automatically skip faces with critical occlusions
- **GPU Hardware Acceleration**: Support for CUDA, DirectML, ROCm, and Apple Silicon
- **Preview System**: Test face swaps before adding to repository
- **Test Image Generation**: Automatically create reference images for preview testing
- **FaceFusion Integration**: Queue system with full destination selection support
- **Multi-Face Processing**: Leverage FaceFusion's face selector modes (reference, best-quality, all, etc.)
- **Automatic Quality Assessment**: Filter faces based on resolution, sharpness, brightness, and contrast
- **Intelligent Matching**: Automatically select the best source face based on 3D orientation
- **Duplicate Prevention**: Keeps only the highest quality face per person per orientation

## Quick Start

### 1. Initialize Repository

```bash
python facefusion_repo_cli.py init
```

This creates the repository structure at `~/.facefusion_repository/`:
- `faces/` - Person-based face storage
- `settings/` - Processing settings profiles
- `presets/` - Person + settings combinations
- `queues/` - Processing queues
- `test_images/` - Reference images for previews

### 2. Add Faces (Person-Based)

```bash
# Add a face for Marc (person name is required)
python facefusion_repo_cli.py add --source face.jpg --person "marc" --name "frontal"

# Add with tags
python facefusion_repo_cli.py add --source profile.jpg --person "marc" --name "profile" --tags profile,high-quality

# Add with preview (validates quality first)
python facefusion_repo_cli.py add --source face.jpg --person "alice" --preview
```

The system will:
- Detect the face in the image
- Estimate 3D pose (pitch, yaw, tilt)
- Check for occlusions
- Assess quality metrics
- Determine orientation angle
- Store in person's directory if acceptable

### 3. List People and Faces

```bash
# List all people in repository
python facefusion_repo_cli.py people

# List all faces for a person
python facefusion_repo_cli.py list --person "marc"

# Filter by orientation and tags
python facefusion_repo_cli.py list --person "marc" --orientation 0 --tags frontal

# Filter by tags
python facefusion_repo_cli.py list --tags high-quality
```

### 4. View Statistics

```bash
# Overall repository statistics
python facefusion_repo_cli.py stats

# Statistics for a specific person
python facefusion_repo_cli.py stats --person "marc"
```

Shows:
- Total faces and quality metrics
- Orientation coverage visualization
- Missing orientations
- People in repository

### 5. GPU Configuration

```bash
# Check GPU status
python facefusion_repo_cli.py gpu-status

# Enable GPU acceleration
python facefusion_repo_cli.py gpu-configure --enable

# Set memory limit
python facefusion_repo_cli.py gpu-configure --memory-limit 8192

# Disable GPU (CPU only)
python facefusion_repo_cli.py gpu-configure --disable
```

### 6. Create Test Images for Preview

```bash
# Generate test images from reference directory
python facefusion_repo_cli.py create-test-images --source-dir ./reference_images

# Use custom output directory
python facefusion_repo_cli.py create-test-images --source-dir ./refs --output-dir ./my_tests
```

### 7. Create Processing Queues

```bash
# Create queue with FaceFusion destination selection
python facefusion_repo_cli.py create-queue \
  --person "marc" \
  --face-id "face_20251028_abc123" \
  --destination "video.mp4" \
  --face-selector "best-quality"

# Use specific face index
python facefusion_repo_cli.py create-queue \
  --person "alice" \
  --face-id "face_20251028_xyz789" \
  --destination "image.jpg" \
  --face-selector "one" \
  --face-index 0

# List all queues
python facefusion_repo_cli.py list-queues

# Filter by status
python facefusion_repo_cli.py list-queues --status pending

# View queue statistics
python facefusion_repo_cli.py queue-stats
```

## Complete CLI Reference

### Repository Management
- `init` - Initialize face repository
- `add` - Add face to repository (requires --person)
- `list` - List faces with optional filters (--person, --orientation, --tags)
- `show` - Show detailed face information including 3D pose
- `remove` - Remove face from repository
- `people` - List all people in repository
- `stats` - Show repository statistics (overall or --person specific)

### GPU Management
- `gpu-status` - Show GPU hardware and configuration
- `gpu-configure` - Configure GPU settings (--enable, --disable, --memory-limit)

### Preview System
- `create-test-images` - Generate test images from source directory
- Use `--preview` flag with `add` command for preview before adding

### Queue Management
- `create-queue` - Create processing queue with FaceFusion destination selection
- `list-queues` - List processing queues (optional --status filter)
- `queue-stats` - Show queue statistics

## Directory Structure

```
~/.facefusion_repository/
├── faces/                    # Person-based face storage
│   ├── marc/                 # Marc's source faces
│   │   ├── face_20251028_abc123.jpg
│   │   └── face_20251028_def456.jpg
│   ├── alice/                # Alice's source faces
│   │   └── face_20251028_xyz789.jpg
│   └── john/                 # John's source faces
│       └── face_20251028_qrs123.jpg
├── settings/                 # Processing settings profiles
├── presets/                  # Person + settings combinations
├── queues/                   # Processing queues
│   ├── queue_uuid1.json
│   └── queue_uuid2.json
├── test_images/              # Reference images for preview
│   ├── test_orientation_000.jpg
│   ├── test_orientation_045.jpg
│   └── ...
├── metadata.json             # Repository metadata
└── gpu_config.json           # GPU configuration

```

## Advanced Features

### 3D Pose Estimation

The system uses 68-point facial landmarks to estimate full 3D head pose:
- **Pitch**: Up/down rotation (-90° to 90°)
- **Yaw**: Left/right rotation (-90° to 90°)
- **Tilt**: Head rotation (-180° to 180°)

Faces with extreme poses are automatically rejected to ensure quality.

### Occlusion Detection

The system detects facial occlusions and identifies:
- Out-of-bounds landmarks
- Clustered landmarks (occlusion indicators)
- Critical region occlusion (eyes, nose)

Faces with critical occlusions are automatically rejected.

### Quality Thresholds

Default thresholds ensure high-quality faces:
- Minimum resolution: 256x256
- Minimum sharpness: 0.3
- Minimum detector score: 0.5
- Brightness range: 0.2-0.9
- Minimum contrast: 0.1
- Minimum overall quality: 0.4

### FaceFusion Integration

The queue system provides complete FaceFusion destination selection:
- **Face Selector Modes**: reference, one, many, best-quality, all
- **Face Index**: Select specific face in destination
- **Reference Distance**: Threshold for reference matching
- **Settings Profiles**: Reusable processing configurations

## Usage Examples

### Example 1: Building a Complete Repository for a Person

```bash
# Initialize
python facefusion_repo_cli.py init

# Create test images from reference photos
python facefusion_repo_cli.py create-test-images --source-dir ./reference_photos

# Add frontal view with preview
python facefusion_repo_cli.py add \
  --source marc_front.jpg \
  --person "marc" \
  --name "frontal" \
  --tags frontal,high-quality \
  --preview

# Add profile views
python facefusion_repo_cli.py add \
  --source marc_left.jpg \
  --person "marc" \
  --name "left_profile" \
  --tags profile

python facefusion_repo_cli.py add \
  --source marc_right.jpg \
  --person "marc" \
  --name "right_profile" \
  --tags profile

# Check coverage for Marc
python facefusion_repo_cli.py stats --person "marc"
```

### Example 2: GPU Configuration

```bash
# Check available GPUs
python facefusion_repo_cli.py gpu-status

# Enable GPU with memory limit
python facefusion_repo_cli.py gpu-configure --enable --memory-limit 8192

# Verify configuration
python facefusion_repo_cli.py gpu-status
```

### Example 3: Queue-Based Processing

```bash
# List Marc's faces to get face ID
python facefusion_repo_cli.py list --person "marc"

# Create queue for video processing with best-quality selector
python facefusion_repo_cli.py create-queue \
  --person "marc" \
  --face-id "face_20251028_abc123" \
  --destination "/path/to/video.mp4" \
  --face-selector "best-quality" \
  --settings "high-quality"

# Create queue for image with specific face index
python facefusion_repo_cli.py create-queue \
  --person "alice" \
  --face-id "face_20251028_xyz789" \
  --destination "/path/to/group_photo.jpg" \
  --face-selector "one" \
  --face-index 2

# View all queues
python facefusion_repo_cli.py list-queues

# Check queue statistics
python facefusion_repo_cli.py queue-stats
```

### Example 4: Managing Multiple People

```bash
# Add faces for different people
python facefusion_repo_cli.py add --source alice.jpg --person "alice"
python facefusion_repo_cli.py add --source bob.jpg --person "bob"
python facefusion_repo_cli.py add --source charlie.jpg --person "charlie"

# List all people
python facefusion_repo_cli.py people

# View faces for specific person
python facefusion_repo_cli.py list --person "alice"

# Compare statistics
python facefusion_repo_cli.py stats --person "alice"
python facefusion_repo_cli.py stats --person "bob"
```

## Quality Requirements

Faces must meet these quality thresholds to be accepted:

- **Minimum Resolution**: 256x256 pixels
- **Minimum Sharpness**: 0.3 (Laplacian variance)
- **Minimum Detector Score**: 0.5 (face detection confidence)
- **Brightness Range**: 0.2 to 0.9 (normalized)
- **Minimum Contrast**: 0.1 (standard deviation)
- **Minimum Overall Quality**: 0.4 (weighted average)

### Tips for High-Quality Faces

1. Use well-lit, sharp images
2. Ensure face is clearly visible and not obscured
3. Use high resolution (1024x1024 or higher recommended)
4. Avoid heavy makeup or accessories
5. Use neutral expressions for best results

## Directory Structure

```
~/.facefusion_repository/
├── repository.json      # Repository database
├── faces/              # Stored face images
│   ├── face_20251028_001.jpg
│   ├── face_20251028_002.jpg
│   └── ...
├── settings/           # Settings profiles (future)
├── presets.json        # Named presets (future)
└── temp/              # Temporary processing files (future)
```

## Architecture

### Module 1: Face Repository Management ✅

**Components:**
- `RepositoryManager`: CRUD operations for face entries
- `QualityAssessor`: Multi-metric quality assessment
- `OrientationMatcher`: Angle matching and grouping
- `CompatibilityMatrix`: Coverage visualization

**Status**: Complete

### Module 2: Destination Face Analysis 🔄

**Components:**
- Frame-by-frame face extraction
- Orientation classification
- Queue management
- Video frame tracking

**Status**: Planned

### Module 3: Settings Management 🔄

**Components:**
- Settings profile storage
- Profile validation
- Apply to FaceFusion state

**Status**: Planned

### Module 4: Named Presets System 🔄

**Components:**
- Preset creation (face + settings)
- Preset execution
- Usage tracking

**Status**: Planned

### Module 5: Batch Execution Engine 🔄

**Components:**
- Queue-based processing
- Progress tracking
- Video reassembly

**Status**: Planned

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Complete system architecture and design
- **[SPECIFICATIONS.md](SPECIFICATIONS.md)**: Detailed technical specifications
- **[MANUAL.md](MANUAL.md)**: Comprehensive user manual
- **[SUMMARY.md](SUMMARY.md)**: Project summary and status

## Development Status

**Current Version**: 1.0.0 (Module 1 Complete)

**Completed**:
- ✅ Repository management (add, list, show, remove)
- ✅ Quality assessment system
- ✅ Orientation matching algorithms
- ✅ Compatibility matrix and coverage reports
- ✅ CLI interface for Module 1
- ✅ Comprehensive documentation

**In Progress**:
- 🔄 Destination face analysis
- 🔄 Settings management
- 🔄 Presets system
- 🔄 Batch execution engine
- 🔄 Complete CLI integration
- 🔄 GUI interface

## Requirements

- Python 3.12+
- FaceFusion core installation
- Dependencies (same as FaceFusion):
  - numpy>=2.3.2
  - opencv-python>=4.12.0.88
  - onnxruntime>=1.22.1
  - scipy>=1.16.1

## Installation

The repository system is integrated with FaceFusion. No separate installation required beyond FaceFusion itself.

## Testing

Currently, the system can be tested using the standalone CLI:

```bash
# Test repository initialization
python facefusion_repo_cli.py init

# Test adding a face (requires a face image)
python facefusion_repo_cli.py add --source test_face.jpg --name "Test"

# Test listing
python facefusion_repo_cli.py list

# Test statistics
python facefusion_repo_cli.py stats
```

**Note**: Comprehensive unit tests will be added in future updates.

## Troubleshooting

### "No face detected in image"

**Cause**: Face not found or image quality too low

**Solution**: 
- Use clearer images with visible faces
- Ensure adequate lighting
- Try different angles

### "Face quality below threshold"

**Cause**: Image doesn't meet quality requirements

**Solution**:
- Use higher resolution images
- Improve lighting
- Use sharper, more focused images

### Repository initialization fails

**Cause**: Permission issues or disk space

**Solution**:
- Check write permissions for home directory
- Ensure adequate disk space (at least 1GB free)

## Contributing

This is part of the FaceFusion project. Follow FaceFusion's contribution guidelines.

## License

OpenRAIL-AS (Same as FaceFusion)

## Support

- **Documentation**: See docs in this directory
- **FaceFusion**: https://docs.facefusion.io
- **Issues**: https://github.com/facefusion/facefusion/issues

## Roadmap

### Phase 1: Core Functionality (Current)
- [x] Module 1: Repository Management
- [ ] Module 2: Destination Analysis
- [ ] Module 3: Settings Management
- [ ] Module 4: Presets System
- [ ] Module 5: Batch Execution

### Phase 2: Polish & Testing
- [ ] Comprehensive unit tests
- [ ] Integration tests
- [ ] Performance optimization
- [ ] CLI refinement

### Phase 3: Advanced Features
- [ ] GUI implementation
- [ ] Cloud synchronization
- [ ] Advanced quality prediction
- [ ] Multi-person support

## Credits

Developed as an extension to FaceFusion by the community.

---

**Version**: 1.0.0  
**Status**: Module 1 Complete  
**Last Updated**: October 28, 2025
