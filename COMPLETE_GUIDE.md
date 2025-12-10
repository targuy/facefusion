# FaceFusion Repository System - Complete Implementation Guide

**Version**: 2.0.0  
**Date**: December 10, 2025  
**Status**: Production Ready

---

## 🎯 Overview

The FaceFusion Repository System is a comprehensive face management platform that extends FaceFusion with advanced capabilities for multi-axis orientation tracking, character-based face organization, and automated face selection for optimal swapping results.

### Key Features

✅ **Multi-Axis Face Orientation**
- 3D orientation tracking (yaw, pitch, roll)
- Automatic detection from facial landmarks
- Improved matching across different face angles

✅ **Character/Person Grouping**
- Organize faces by character or person
- Associate multiple face angles with one character
- Automatic best-match selection per character

✅ **Container Support**
- Docker and Docker Compose for easy deployment
- CPU and GPU (CUDA) support
- VS Code Dev Containers and GitHub Codespaces ready

✅ **Graphical User Interface**
- Gradio-based web UI
- Face upload and management
- Character management
- Statistics and visualization

✅ **Command-Line Interface**
- Full CLI for all operations
- Batch processing support
- Scriptable and automatable

---

## 🚀 Quick Start

### 1. Using Docker (Recommended)

#### CPU Mode
```bash
# Start with Docker Compose
docker-compose --profile cpu up -d

# Access UI at http://localhost:7860
```

#### GPU Mode
```bash
# Start with GPU support
docker-compose --profile gpu up -d

# Access UI at http://localhost:7860
```

### 2. Using GitHub Codespaces

1. Open repository in Codespaces
2. Wait for automatic setup (uses `.devcontainer` config)
3. Run: `python facefusion.py run --ui-layouts repository`
4. Access forwarded port 7860

### 3. Local Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize repository
python facefusion_repo_cli.py init

# Start UI
python facefusion.py run --ui-layouts repository
```

---

## 📚 Complete Feature List

### 1. Multi-Axis Orientation System

**What It Does**: Tracks face orientation in 3D space (yaw, pitch, roll) for better matching.

**Why It Matters**: Traditional face swapping only considers horizontal rotation. Multi-axis tracking ensures natural results when faces tilt or rotate.

**Usage**:
```bash
# CLI - Orientation is automatically detected when adding faces
python facefusion_repo_cli.py add --source face.jpg --name "Alice"

# The system stores:
# - Yaw: Horizontal rotation (-180° to 180°)
# - Pitch: Vertical tilt (-90° to 90°)
# - Roll: Head rotation (-180° to 180°)
```

**GUI**: Orientation information is displayed in face listings and details.

### 2. Character Management System

**What It Does**: Groups faces by character/person for organized management.

**Why It Matters**: When working with the same person at different angles, character grouping keeps everything organized and enables automatic best-match selection.

**Usage**:

```bash
# Add a character
python facefusion_repo_cli.py character-add --name "Alice" --description "Main character"

# Add faces to character
python facefusion_repo_cli.py add --source alice_front.jpg --name "Alice Front" --character char_abc123

# List characters
python facefusion_repo_cli.py character-list

# Show character details with all associated faces
python facefusion_repo_cli.py character-show --character-id char_abc123
```

**GUI**: Full character management in the "👤 Characters" tab.

### 3. Repository Management

**Core Operations**:

```bash
# Initialize repository
python facefusion_repo_cli.py init

# Add face with metadata
python facefusion_repo_cli.py add \
  --source face.jpg \
  --name "Alice Frontal" \
  --tags frontal,high-quality \
  --character char_abc123

# List faces with filters
python facefusion_repo_cli.py list
python facefusion_repo_cli.py list --orientation 0
python facefusion_repo_cli.py list --character char_abc123

# Show face details
python facefusion_repo_cli.py show --face-id face_20251210_001

# Remove face
python facefusion_repo_cli.py remove --face-id face_20251210_001

# View statistics
python facefusion_repo_cli.py stats
```

### 4. Quality Assessment

**Automatic Quality Metrics**:
- Sharpness (Laplacian variance)
- Brightness (normalized)
- Contrast (standard deviation)
- Resolution
- Detector confidence
- Overall quality score

**Thresholds**:
- Minimum resolution: 256x256
- Minimum sharpness: 0.3
- Minimum detector score: 0.5
- Minimum overall quality: 0.4

### 5. Destination Analysis (Coming from existing modules)

```bash
# Analyze destination media
python facefusion_repo_cli.py analyze-destination \
  --source video.mp4 \
  --frame-sample-rate 5 \
  --min-confidence 0.5

# Show processing queues
python facefusion_repo_cli.py show-queues

# View queue statistics
python facefusion_repo_cli.py queue-stats

# Clear queues
python facefusion_repo_cli.py clear-queues
```

### 6. Batch Processing (Framework complete, ML integration pending)

```bash
# Check batch status
python facefusion_repo_cli.py batch-status

# Preview batch processing (dry run)
python facefusion_repo_cli.py batch-run --output ./output --dry-run

# Execute batch processing (when ML integration complete)
python facefusion_repo_cli.py batch-run --output ./output
```

---

## 🎨 Graphical User Interface

### Accessing the GUI

**Method 1: Standalone Repository UI**
```bash
python facefusion.py run --ui-layouts repository
```

**Method 2: Docker**
```bash
docker-compose --profile cpu up -d
# Access http://localhost:7860
```

### GUI Tabs

**📁 Repository Tab**
- Upload and add faces to repository
- View all faces with filtering
- Show face details (including 3D orientation)
- Remove faces

**👤 Characters Tab**
- Create and manage characters
- List all characters with face counts
- View character details with associated faces
- Remove characters

**📊 Statistics Tab**
- Repository statistics
- Orientation coverage visualization
- Quality metrics
- Face distribution by orientation

---

## 🐳 Container Deployment

### Docker

**CPU Mode**:
```bash
# Build
docker build --target cpu -t facefusion:cpu .

# Run
docker run -d \
  --name facefusion-cpu \
  -p 7860:7860 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/output:/app/output \
  -v ~/.facefusion_repository:/root/.facefusion_repository \
  facefusion:cpu
```

**GPU Mode**:
```bash
# Build
docker build --target gpu -t facefusion:gpu .

# Run
docker run -d \
  --name facefusion-gpu \
  --gpus all \
  -p 7860:7860 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/output:/app/output \
  -v ~/.facefusion_repository:/root/.facefusion_repository \
  facefusion:gpu
```

### Docker Compose

```bash
# CPU mode
docker-compose --profile cpu up -d

# GPU mode
docker-compose --profile gpu up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Codespaces

1. **Open in Codespaces**: Click "Code" → "Codespaces" → "Create"
2. **Automatic Setup**: Dev container configures everything
3. **Start UI**: `python facefusion.py run --ui-layouts repository`
4. **Access**: Use forwarded port 7860

See [DOCKER.md](DOCKER.md) for complete container documentation.

---

## 📋 CLI Commands Reference

### Repository Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize face repository |
| `add` | Add face to repository |
| `list` | List faces in repository |
| `show` | Show face details |
| `remove` | Remove face from repository |
| `stats` | Show repository statistics |

### Character Commands

| Command | Description |
|---------|-------------|
| `character-add` | Add a new character/person |
| `character-list` | List all characters |
| `character-show` | Show character details |
| `character-remove` | Remove a character |

### Analysis Commands

| Command | Description |
|---------|-------------|
| `analyze-destination` | Analyze destination media |
| `show-queues` | Display processing queues |
| `queue-stats` | Show detailed queue statistics |
| `export-queue` | Export queue to JSON |
| `clear-queues` | Clear processing queues |

### Batch Commands

| Command | Description |
|---------|-------------|
| `batch-run` | Execute batch processing |
| `batch-status` | Show batch processing status |

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────┐
│            User Interface Layer                  │
├─────────────────────────────────────────────────┤
│  CLI (commands.py)   │   GUI (repository.py)    │
└──────────┬───────────┴───────────┬──────────────┘
           │                        │
┌──────────▼────────────────────────▼──────────────┐
│           Business Logic Layer                   │
├──────────────────────────────────────────────────┤
│  RepositoryManager  │  CharacterManager          │
│  OrientationMatcher │  Orientation3DDetector     │
│  QualityAssessor    │  CompatibilityMatrix       │
└──────────┬──────────────────────┬────────────────┘
           │                       │
┌──────────▼───────────────────────▼───────────────┐
│              Data Layer                          │
├──────────────────────────────────────────────────┤
│  repository.json    │  characters.json           │
│  faces/             │  queues/                   │
└──────────────────────────────────────────────────┘
```

### Data Flow

```
1. Add Face
   Image → Face Detection → Quality Assessment → 
   3D Orientation Detection → Repository Storage

2. Character Management
   Character Info → Validation → Character Storage → 
   Face Association

3. Destination Analysis
   Media → Face Extraction → Orientation Classification → 
   Repository Matching → Queue Creation

4. Batch Processing
   Queues → Face Swapping (ML Integration) → 
   Output Generation
```

### File Structure

```
facefusion_repository/
├── types.py                    # Type definitions
├── repository/
│   ├── manager.py              # Repository CRUD
│   ├── orientation_3d.py       # 3D orientation detection
│   ├── character_manager.py   # Character management
│   ├── quality_assessor.py    # Quality metrics
│   └── orientation_matcher.py # Orientation matching
├── destination/
│   ├── analyzer.py             # Destination analysis
│   └── queue_manager.py        # Queue management
├── batch/
│   └── executor.py             # Batch processing
└── cli/
    └── commands.py             # CLI commands

facefusion/uis/
├── layouts/
│   └── repository.py           # GUI layout
└── repository_backend.py       # GUI backend functions
```

---

## 🔧 Configuration

### Repository Location

Default: `~/.facefusion_repository/`

Override with environment variable:
```bash
export FACEFUSION_REPOSITORY_PATH=/custom/path
```

### Quality Thresholds

Edit in `facefusion_repository/types.py`:
```python
DEFAULT_QUALITY_THRESHOLDS = QualityThresholds(
    min_resolution=(256, 256),
    min_sharpness=0.3,
    min_detector_score=0.5,
    min_brightness=0.2,
    max_brightness=0.9,
    min_contrast=0.1,
    min_overall_quality=0.4
)
```

---

## 🎯 Use Cases

### Use Case 1: Single Character, Multiple Angles

```bash
# 1. Create character
python facefusion_repo_cli.py character-add --name "Alice"

# 2. Add faces at different angles
python facefusion_repo_cli.py add --source alice_0deg.jpg --name "Alice Front" --character char_abc123
python facefusion_repo_cli.py add --source alice_45deg.jpg --name "Alice 45°" --character char_abc123
python facefusion_repo_cli.py add --source alice_90deg.jpg --name "Alice Profile" --character char_abc123

# 3. Analyze destination
python facefusion_repo_cli.py analyze-destination --source video.mp4

# 4. System automatically selects best face angle for each frame
python facefusion_repo_cli.py batch-run --output ./output
```

### Use Case 2: Multiple Characters

```bash
# 1. Create characters
python facefusion_repo_cli.py character-add --name "Alice"
python facefusion_repo_cli.py character-add --name "Bob"

# 2. Add faces for each character
python facefusion_repo_cli.py add --source alice.jpg --name "Alice" --character char_alice
python facefusion_repo_cli.py add --source bob.jpg --name "Bob" --character char_bob

# 3. List by character
python facefusion_repo_cli.py list --character char_alice
```

### Use Case 3: Quality-Based Filtering

```bash
# Add multiple versions, system keeps only highest quality
python facefusion_repo_cli.py add --source face_low.jpg --name "Alice"
python facefusion_repo_cli.py add --source face_high.jpg --name "Alice"

# System automatically replaces lower quality faces
# when better quality is added for same orientation
```

---

## 🐛 Troubleshooting

### Issue: "No face detected in image"

**Cause**: Face not clearly visible or image quality too low

**Solution**:
- Use well-lit, high-resolution images
- Ensure face is clearly visible and not obscured
- Try different angles or images

### Issue: "Face quality below threshold"

**Cause**: Image doesn't meet quality requirements

**Solution**:
- Use higher resolution (1024x1024+ recommended)
- Improve lighting
- Use sharper, more focused images
- Check quality thresholds in configuration

### Issue: "Character name already exists"

**Cause**: Attempting to create character with duplicate name

**Solution**:
- Use unique character names
- Or use existing character ID for face association

### Issue: Container won't start

**Cause**: Various Docker/GPU issues

**Solution**:
```bash
# Check logs
docker-compose logs

# For GPU: Verify NVIDIA Docker
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Rebuild
docker-compose build --no-cache
```

---

## 📊 Technical Specifications

### Orientation Detection

**Method**: Geometric analysis of facial landmarks

**Angles**:
- **Yaw**: Horizontal rotation, -180° to 180°
- **Pitch**: Vertical tilt, -90° to 90°
- **Roll**: Head rotation, -180° to 180°

**Standard Angles** (for legacy compatibility):
- 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°

### Quality Metrics

**Sharpness**: Laplacian variance
- Range: 0.0 to 1.0
- Higher = sharper image

**Brightness**: Mean pixel intensity (normalized)
- Range: 0.0 to 1.0
- Optimal: 0.2 to 0.9

**Contrast**: Standard deviation of pixels
- Range: 0.0 to 1.0
- Higher = more contrast

**Overall Quality**: Weighted average
- Formula: (0.35 × sharpness) + (0.25 × brightness) + (0.20 × contrast) + (0.20 × detector)

### Storage Format

**Repository**: JSON with binary face embeddings
**Images**: Original format preserved (JPG, PNG)
**Size**: ~500KB per face (varies with resolution)

---

## 🔐 Security

### Data Privacy

- Face embeddings are stored locally only
- No external API calls for face processing
- Container volumes isolate repository data

### Best Practices

1. **Access Control**: Use firewall rules for production deployments
2. **Authentication**: Add auth layer for public-facing UIs
3. **Data Backup**: Regularly backup `~/.facefusion_repository/`
4. **Container Security**: Run containers with non-root user in production

---

## 🚧 Future Development

### Planned Features

**Module 3: Settings Management** (Future)
- Save and reuse FaceFusion configuration profiles
- Quick setting switches

**Module 4: Named Presets** (Future)
- Combine face + settings into reusable presets
- One-click execution

**Module 5: ML Integration** (Pending)
- Complete face-swapping execution
- Video processing with audio
- Frame assembly and optimization

**Advanced Features** (Roadmap)
- Multi-person face swapping in single video
- Face tracking across frames
- Quality-based automatic selection
- Cloud synchronization
- Advanced GUI features

---

## 📄 License

OpenRAIL-AS (Same as FaceFusion)

---

## 🙏 Acknowledgments

- **FaceFusion Core**: Base face-swapping platform
- **Community Contributors**: Testing and feedback
- **Docker Community**: Container best practices

---

## 📞 Support

- **Documentation**: This guide and related markdown files
- **Issues**: GitHub Issues
- **Community**: FaceFusion Discord

---

**Last Updated**: December 10, 2025  
**Version**: 2.0.0
