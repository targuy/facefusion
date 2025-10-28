# FaceFusion Repository System

Advanced face repository management with orientation-based matching for the FaceFusion platform.

## Overview

The FaceFusion Repository System extends FaceFusion with sophisticated capabilities for managing multiple source faces at different orientations, enabling high-quality face swaps in videos with varying face angles.

### Key Features

- **Multi-Orientation Repository**: Store source faces at 8 standard orientation angles (0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°)
- **Automatic Quality Assessment**: Filter faces based on resolution, sharpness, brightness, and contrast
- **Intelligent Matching**: Automatically select the best source face for each destination based on orientation
- **Duplicate Detection**: Prevents storing redundant faces with similar orientations
- **Comprehensive Statistics**: Visualize repository coverage and quality metrics

## Quick Start

### 1. Initialize Repository

```bash
python facefusion_repo_cli.py init
```

This creates the repository structure at `~/.facefusion_repository/`

### 2. Add Faces

```bash
# Add a face with a name
python facefusion_repo_cli.py add --source path/to/face.jpg --name "Alice Frontal"

# Add a face with tags
python facefusion_repo_cli.py add --source path/to/profile.jpg --name "Alice Profile" --tags profile,high-quality
```

The system will:
- Detect the face in the image
- Assess quality metrics
- Determine orientation angle
- Store if quality is acceptable

### 3. List Faces

```bash
# List all faces
python facefusion_repo_cli.py list

# Filter by orientation
python facefusion_repo_cli.py list --orientation 0

# Filter by tags
python facefusion_repo_cli.py list --tags frontal,high-quality
```

### 4. View Statistics

```bash
python facefusion_repo_cli.py stats
```

Shows:
- Total faces and quality metrics
- Orientation coverage visualization
- Missing orientations
- Storage usage

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

### Example 3: Creating and Using Presets

```bash
# Create a settings profile from template
python facefusion_repo_cli.py settings-create \
    --name high_quality \
    --template high_quality \
    --description "High quality face swapping"

# Create a preset combining face and settings
python facefusion_repo_cli.py presets-create \
    --name "alice_frontal_hq" \
    --face-id face_20251028_abc123 \
    --settings high_quality \
    --description "Alice frontal view with high quality" \
    --tags alice,frontal,high-quality

# List all presets
python facefusion_repo_cli.py presets-list

# Show preset configuration
python facefusion_repo_cli.py presets-show --name alice_frontal_hq

# Apply preset to get configuration
python facefusion_repo_cli.py presets-apply --name alice_frontal_hq
```

### Example 4: Preset Management

```bash
# Validate a preset
python facefusion_repo_cli.py presets-validate --name alice_frontal_hq

# Copy a preset with modifications
python facefusion_repo_cli.py presets-copy \
    --source alice_frontal_hq \
    --name alice_profile_hq \
    --face-id face_20251028_xyz789

# Export preset for sharing
python facefusion_repo_cli.py presets-export \
    --name alice_frontal_hq \
    --output alice_preset.json

# Import preset
python facefusion_repo_cli.py presets-import \
    --file alice_preset.json \
    --name imported_preset
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
├── settings/           # Settings profiles
│   ├── high_quality.json
│   ├── fast_processing.json
│   └── ...
├── presets.json        # Named presets
├── collections.json    # Preset collections
└── temp/              # Temporary processing files
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

### Module 3: Settings Management ✅

**Components:**
- `SettingsManager`: CRUD operations for settings profiles
- `SettingsValidator`: Validation against FaceFusion requirements
- Template system for common configurations
- Import/export functionality

**Status**: Complete

### Module 4: Named Presets System ✅

**Components:**
- `PresetManager`: Preset CRUD operations
- `PresetValidator`: Face-settings compatibility validation
- `PresetTemplate`: Smart preset generation
- `PresetCollection`: Preset grouping
- `PresetApplicator`: Configuration deployment

**Status**: Complete

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
- **[MODULE4_GUIDE.md](MODULE4_GUIDE.md)**: Module 4 user guide and examples
- **[SUMMARY.md](SUMMARY.md)**: Project summary and status

## Development Status

**Current Version**: 1.1.0 (Modules 1, 3, and 4 Complete)

**Completed**:
- ✅ Module 1: Repository management (add, list, show, remove)
- ✅ Module 1: Quality assessment system
- ✅ Module 1: Orientation matching algorithms
- ✅ Module 1: Compatibility matrix and coverage reports
- ✅ Module 1: CLI interface
- ✅ Module 3: Settings management system
- ✅ Module 3: Settings validation
- ✅ Module 3: Template system
- ✅ Module 3: Import/export functionality
- ✅ Module 4: Preset management system
- ✅ Module 4: Preset validation
- ✅ Module 4: Preset templates
- ✅ Module 4: Preset collections
- ✅ Module 4: Configuration deployment
- ✅ Module 4: CLI interface
- ✅ Comprehensive documentation

**In Progress**:
- 🔄 Module 2: Destination face analysis
- 🔄 Module 5: Batch execution engine
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
