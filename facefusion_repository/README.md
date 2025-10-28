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

### Example 3: Settings Profile Management

```bash
# View available templates
python facefusion_repo_cli.py settings-templates

# Create profile from template
python facefusion_repo_cli.py settings-create \
  --name my_high_quality \
  --template high_quality \
  --tags production

# List all settings profiles
python facefusion_repo_cli.py settings-list

# View profile details
python facefusion_repo_cli.py settings-show --name my_high_quality

# Compare two profiles
python facefusion_repo_cli.py settings-compare \
  --profile1 my_high_quality \
  --profile2 fast_preview

# Export for sharing
python facefusion_repo_cli.py settings-export \
  --name my_high_quality \
  --output my_settings.json
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
│   ├── my_profile.json
│   ├── production.json
│   └── ...
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

### Module 3: Settings Management ✅

**Components:**
- `SettingsManager`: CRUD operations for settings profiles
- `ProfileValidator`: Parameter validation and compatibility checking
- `SettingsTemplate`: Pre-configured settings templates
- `ProfileComparator`: Profile comparison and analysis

**Status**: Complete

**Features:**
- Create, read, update, delete settings profiles
- 6 built-in templates (default, high-quality, fast-preview, gpu-accelerated, multi-face, reference-face)
- Comprehensive validation for all FaceFusion parameters
- Profile comparison with difference highlighting
- Export/import profiles via JSON
- Tag-based organization
- CLI commands for all operations

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
- **[SETTINGS_GUIDE.md](SETTINGS_GUIDE.md)**: Settings profile management user guide
- **[SETTINGS_PARAMETERS.md](SETTINGS_PARAMETERS.md)**: Complete settings parameters reference

## Development Status

**Current Version**: 2.0.0 (Modules 1-3 Complete)

**Completed**:
- ✅ Repository management (add, list, show, remove)
- ✅ Quality assessment system
- ✅ Orientation matching algorithms
- ✅ Compatibility matrix and coverage reports
- ✅ CLI interface for Module 1
- ✅ Settings profile management
- ✅ Profile validation and templates
- ✅ Profile comparison and analysis
- ✅ CLI interface for Module 3
- ✅ Comprehensive documentation

**In Progress**:
- 🔄 Destination face analysis (Module 2)
- 🔄 Named presets system (Module 4)
- 🔄 Batch execution engine (Module 5)
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
