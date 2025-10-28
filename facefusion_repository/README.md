# FaceFusion Repository System

Advanced face repository management with person-based architecture and orientation matching for the FaceFusion platform.

## Overview

The FaceFusion Repository System extends FaceFusion with sophisticated capabilities for managing multiple source faces organized by person, enabling high-quality face swaps in videos with varying face angles.

### Key Features

- **Person-Based Architecture**: Organize faces by person with mandatory person identifiers
- **Multi-Orientation Support**: Store faces at various orientation angles (0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°)
- **Automatic Quality Assessment**: Filter faces based on resolution, sharpness, brightness, contrast, and more
- **3D Pose Estimation**: Track pitch, yaw, and tilt for advanced orientation matching
- **Occlusion Detection**: Identify and handle partially obscured faces
- **Intelligent Matching**: Automatically select the best source face for each destination based on orientation
- **Settings Management**: Create and manage FaceFusion parameter profiles with templates
- **Presets System**: Combine person + settings for quick execution
- **Dual Interface**: Full CLI and Gradio GUI support
- **GPU Acceleration**: Utilize CUDA, DirectML, ROCm, or MPS for faster processing

## Quick Start

### 1. Initialize Repository

```bash
python facefusion_repo_cli.py init
```

This creates the person-based repository structure at `~/.facefusion_repository/`:
- `faces/` - Person-based face storage (faces/{person}/)
- `settings/` - FaceFusion parameter profiles
- `presets/` - Person + settings combinations
- `queues/` - Processing queues (future)
- `test_images/` - Preview reference images (future)
- `metadata.json` - Repository metadata

### 2. Add a Person

```bash
# Add a new person
python facefusion_repo_cli.py add-person --person "marc" --display-name "Marc"

# List all people
python facefusion_repo_cli.py people
```

### 3. Add Faces for a Person

```bash
# Add a face for Marc
python facefusion_repo_cli.py add --source path/to/face.jpg --person "marc" --name "Marc Frontal"

# Add another face with tags
python facefusion_repo_cli.py add --source path/to/profile.jpg --person "marc" --name "Marc Profile" --tags profile,high-quality
```

The system will:
- Detect the face in the image
- Assess quality metrics (resolution, sharpness, brightness, contrast)
- Determine orientation angle
- Estimate 3D pose (pitch, yaw, tilt)
- Check for occlusions
- Store in the person's directory if quality is acceptable

### 4. List Faces and People

```bash
# List all people
python facefusion_repo_cli.py people

# List all faces
python facefusion_repo_cli.py list

# Filter by person
python facefusion_repo_cli.py list --person marc

# Filter by orientation
python facefusion_repo_cli.py list --orientation 0

# Filter by tags
python facefusion_repo_cli.py list --tags frontal,high-quality
```

### 5. View Statistics

```bash
python facefusion_repo_cli.py stats
```

Shows:
- Total people and faces
- Quality metrics
- Faces by person
- Orientation coverage visualization
- Missing orientations
- Storage usage

### 6. Settings and Presets

```bash
# Create a settings profile from a template
python facefusion_repo_cli.py repo-settings-create --name "high_quality" --template gpu_accelerated

# List settings
python facefusion_repo_cli.py repo-settings-list

# Create a preset combining person + settings
python facefusion_repo_cli.py repo-presets-create --name "marc_hq" --person "marc" --settings "high_quality"

# List presets
python facefusion_repo_cli.py repo-presets-list
```

## GUI Interface

Launch the Gradio GUI for visual management:

```bash
python facefusion_repo_gui.py
```

The GUI provides tabs for:
- **Repository**: Person and face management with drag-drop upload
- **Settings**: Create and manage FaceFusion parameter profiles
- **Presets**: Combine person + settings for quick access

## Directory Structure

```
~/.facefusion_repository/
├── faces/
│   ├── marc/              # Marc's source faces
│   │   ├── face_20251028_001.jpg
│   │   └── face_20251028_002.jpg
│   ├── alice/             # Alice's source faces
│   └── john/              # John's source faces
├── settings/              # FaceFusion parameter profiles
│   └── profiles.json
├── presets/               # Person + settings combinations
│   └── presets.json
├── queues/               # Processing queues (future)
├── test_images/          # Preview reference images (future)
├── repository.json       # Repository database
└── metadata.json         # Simple repository metadata
```

## Usage Examples

### Example 1: Building a Complete Repository

```bash
# Initialize
python facefusion_repo_cli.py init

# Add frontal view
python facefusion_repo_cli.py add --source alice_front.jpg --name "Alice Front" --tags alice,frontal

# Add profile views
python facefusion_repo_cli.py add --source alice_left.jpg --name "Alice Left" --tags alice,profile
python facefusion_repo_cli.py add --source alice_right.jpg --name "Alice Right" --tags alice,profile

# Check coverage
python facefusion_repo_cli.py stats
```

### Example 2: Managing Faces

```bash
# Show face details
python facefusion_repo_cli.py show --face-id face_20251028_abc123

# Remove a face
python facefusion_repo_cli.py remove --face-id face_20251028_abc123

# List specific person's faces
python facefusion_repo_cli.py list --tags alice
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
