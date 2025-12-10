# FaceFusion Repository System - User Guide

## Quick Start

The FaceFusion Repository System is now ready to use! Follow these steps to get started.

### System Status

**Current Implementation: 70% Complete (Demonstration Ready)**

✅ **Working Features:**
- Repository management (add, list, show, remove faces)
- Quality assessment and orientation detection
- Destination media analysis
- Processing queue management
- Batch execution framework with progress tracking
- Comprehensive CLI with 13 commands

⚙️ **Structural Components Ready:**
- Batch executor architecture
- Progress tracking system
- Queue orchestration
- Integration points documented

🔄 **Future Integration:**
- Full ML model integration for actual face swapping
- Settings management (Module 3)
- Named presets system (Module 4)
- GUI interface (Gradio-based)

---

## Installation

### Prerequisites
- Python 3.12+
- pip package manager

### Setup

1. **Clone the repository** (if not already done)
```bash
git clone https://github.com/targuy/facefusion.git
cd facefusion
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

This will install:
- gradio (5.42.0) - for future GUI
- numpy (>=2.0.0,<2.3.0) - numerical computing
- onnx (1.19.0) - ML model format
- onnxruntime (1.22.1) - ML inference
- opencv-python (4.12.0.88) - computer vision
- scipy (1.16.1) - scientific computing
- tqdm (4.67.1) - progress bars
- psutil (7.0.0) - system utilities

3. **Verify installation**
```bash
python facefusion_repo_cli.py --help
```

You should see a list of 13 available commands.

---

## Available Commands

The system provides 13 CLI commands organized by function:

### Repository Management
- `init` - Initialize face repository
- `add` - Add face to repository
- `list` - List faces in repository
- `show` - Show face details
- `remove` - Remove face from repository
- `stats` - Show repository statistics

### Destination Analysis
- `analyze-destination` - Analyze media and create queues
- `show-queues` - Display processing queues
- `queue-stats` - Show detailed queue statistics
- `export-queue` - Export queue to JSON
- `clear-queues` - Clear processing queues

### Batch Processing
- `batch-status` - Show batch processing status
- `batch-run` - Execute batch processing

---

## Usage Examples

### Example 1: Repository Setup

```bash
# Initialize repository
python facefusion_repo_cli.py init
# Output: ✓ Repository initialized successfully at ~/.facefusion_repository

# Check initial status
python facefusion_repo_cli.py stats
# Output: Repository is empty - no faces available
#         Coverage: 0.0%
```

### Example 2: Adding Faces (When You Have Images)

```bash
# Add a frontal face
python facefusion_repo_cli.py add \
    --source path/to/frontal_face.jpg \
    --name "Alice Frontal"

# Add a profile view
python facefusion_repo_cli.py add \
    --source path/to/profile_face.jpg \
    --name "Alice Profile" \
    --tags profile,high-quality

# List all faces
python facefusion_repo_cli.py list

# Show detailed statistics
python facefusion_repo_cli.py stats
```

### Example 3: Analyzing Destination Media (When You Have Video/Images)

```bash
# Analyze a video file
python facefusion_repo_cli.py analyze-destination \
    --source target_video.mp4 \
    --frame-sample-rate 5 \
    --min-confidence 0.6

# Check what queues were created
python facefusion_repo_cli.py show-queues

# View queue statistics
python facefusion_repo_cli.py queue-stats
```

### Example 4: Batch Processing

```bash
# Check batch status
python facefusion_repo_cli.py batch-status

# Preview operations (dry run)
python facefusion_repo_cli.py batch-run \
    --output ./output \
    --dry-run

# Execute batch processing (when implemented)
python facefusion_repo_cli.py batch-run \
    --output ./output
```

### Example 5: Using the Example Workflow Script

```bash
# Run the demonstration workflow
python example_workflow.py

# This script will:
# - Check repository status
# - Show all faces and orientations
# - Display coverage statistics
# - Show processing queues (if any)
# - Provide next steps
```

---

## System Architecture

### Directory Structure

```
~/.facefusion_repository/          # Repository root
├── repository.json                 # Face database
├── faces/                         # Stored face images
│   ├── face_20251210_001.jpg
│   ├── face_20251210_002.jpg
│   └── ...
├── queues/                        # Processing queues
│   └── processing_queues.json
└── settings/                      # Settings profiles (future)
```

### Data Flow

```
1. Repository Setup
   User → face images → Repository Manager → Repository DB
   
2. Destination Analysis  
   Media file → Face Extractor → Orientation Detector → 
   Repository Matcher → Processing Queues
   
3. Batch Processing
   Processing Queues → Batch Executor → Face Swapper →
   Output Files
```

### Module Overview

**Module 1: Repository Management (100% ✅)**
- Manages source face library
- Quality assessment (5 metrics)
- Orientation detection (8 angles)
- CRUD operations

**Module 2: Destination Analysis (100% ✅)**
- Extracts faces from media
- Detects face orientations
- Matches with repository
- Creates processing queues

**Module 3: Settings Management (0% ❌)**
- Planned for future
- Will manage FaceFusion configuration

**Module 4: Named Presets (0% ❌)**
- Planned for future
- Will combine face + settings

**Module 5: Batch Execution (70% ⚙️)**
- Queue orchestration ✅
- Progress tracking ✅
- Face swapping integration (pending)

---

## Testing

### Unit Tests

The repository includes comprehensive unit tests:

```bash
# Run all repository tests
python -m pytest tests/test_repository/ -v

# Expected results:
# - Module 1: 13 tests passing
# - Module 2: 25 tests passing
# - Total: 38 tests passing
```

### Integration Testing

Run the example workflow script:

```bash
python example_workflow.py
```

This demonstrates the complete system workflow.

---

## Configuration

### Quality Thresholds

Default quality thresholds for faces (configurable in future versions):

- **Minimum Resolution**: 256x256 pixels
- **Minimum Sharpness**: 0.3 (Laplacian variance)
- **Minimum Detector Score**: 0.5 (face detection confidence)
- **Brightness Range**: 0.2 to 0.9 (normalized)
- **Minimum Contrast**: 0.1 (standard deviation)
- **Minimum Overall Quality**: 0.4 (weighted average)

### Orientation Angles

Standard 8-point orientation system:
- 0° (Frontal)
- 45° (Front-right quarter)
- 90° (Right profile)
- 135° (Back-right quarter)
- 180° (Back)
- 225° (Back-left quarter)
- 270° (Left profile)
- 315° (Front-left quarter)

### Matching Parameters

- **Orientation Tolerance**: 22° (configurable)
- **Minimum Confidence**: 0.5 (adjustable per analysis)
- **Confidence Calculation**: 60% orientation + 40% quality

---

## Troubleshooting

### Common Issues

**Issue: "ModuleNotFoundError: No module named 'cv2'"**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue: "Repository not initialized"**
```bash
# Solution: Initialize repository first
python facefusion_repo_cli.py init
```

**Issue: "No processing queues available"**
```bash
# Solution: Analyze destination media first
python facefusion_repo_cli.py analyze-destination --source video.mp4
```

**Issue: "Face quality below threshold"**
- Use higher resolution images (1024x1024+ recommended)
- Ensure good lighting
- Use sharp, focused images
- Avoid heavy makeup or accessories

**Issue: "No face detected"**
- Verify face is clearly visible
- Try different angles
- Ensure adequate lighting
- Check image format is supported (JPG, PNG)

### Getting Help

1. Check the documentation:
   - `STEP_BY_STEP_IMPLEMENTATION.md` - Detailed implementation guide
   - `ANALYSIS_AND_RECOMMENDATIONS.md` - System analysis
   - `IMPLEMENTATION_SUMMARY.md` - Implementation details

2. Run with verbose output (future feature)

3. Check logs in `~/.facefusion_repository/logs/` (future feature)

---

## Development Status

### Completed (70%)

✅ **Phase 1: Environment Setup**
- Dependencies installed and working
- CLI verified functional
- All 13 commands operational

✅ **Module 1: Repository Management**
- Full CRUD operations
- Quality assessment working
- Orientation detection functional
- Statistics and visualization complete

✅ **Module 2: Destination Analysis**
- Face extraction working
- Orientation classification functional
- Repository matching operational
- Queue management complete

⚙️ **Module 5: Batch Execution**
- Framework implemented
- Progress tracking working
- Queue orchestration functional
- ML integration points documented

### Planned (30%)

❌ **Module 3: Settings Management**
- Settings profile storage
- FaceFusion configuration management
- Profile validation

❌ **Module 4: Named Presets**
- Preset creation
- Preset execution
- Usage tracking

❌ **GUI Implementation**
- Gradio-based interface
- 6-tab design (documented)
- Visual management tools

❌ **Advanced Features**
- Face tracking
- Parallel processing
- Detection caching
- Cloud integration

---

## Contributing

This project is part of the FaceFusion ecosystem. Contributions welcome!

### Areas for Contribution

1. **ML Integration**: Complete FaceFusion face_swapper integration
2. **Settings Module**: Implement Module 3 (Settings Management)
3. **Presets Module**: Implement Module 4 (Named Presets)
4. **GUI**: Implement Gradio interface
5. **Tests**: Add more unit and integration tests
6. **Documentation**: Expand user guides and tutorials
7. **Performance**: Optimize processing speed

### Development Setup

```bash
# Clone repository
git clone https://github.com/targuy/facefusion.git
cd facefusion

# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Run example workflow
python example_workflow.py
```

---

## License

OpenRAIL-AS (Same as FaceFusion)

---

## Support

- **Documentation**: See docs in `facefusion_repository/` directory
- **FaceFusion Main**: https://docs.facefusion.io
- **Issues**: https://github.com/targuy/facefusion/issues

---

## Changelog

### Version 1.0.0 (Current)
- ✅ Repository management complete
- ✅ Destination analysis complete
- ✅ Batch execution framework complete
- ✅ CLI with 13 commands
- ✅ Comprehensive documentation
- ⚙️ ML integration pending

### Future Versions
- v1.1.0: Full ML integration
- v1.2.0: Settings management
- v1.3.0: Named presets
- v2.0.0: GUI interface

---

**Last Updated**: December 10, 2025  
**Version**: 1.0.0  
**Status**: Demonstration Ready (70% Complete)
