# Enhanced Repository System Examples

This directory contains example scripts demonstrating the enhanced features of the FaceFusion Repository System.

## Examples

### enhanced_repository_features.py

Comprehensive example showing:
- Quality assessment during face addition
- Quality-based face selection
- Settings profile management
- Pose-aware selection (API usage)
- CLI command examples

**Usage:**
```bash
python examples/enhanced_repository_features.py
```

This will display example code and CLI commands for all enhanced features.

## Requirements

These examples require the FaceFusion environment with all dependencies installed. See the main README for installation instructions.

## Features Demonstrated

1. **Quality Assessment**: Multi-metric quality evaluation (sharpness, brightness, contrast, resolution)
2. **Quality Filtering**: Automatic filtering of low-quality faces during addition
3. **Quality-Based Selection**: Select best quality faces for processing
4. **Settings Management**: Create, save, and reuse processing configurations
5. **Pose-Aware Selection**: Match faces based on 3D orientation

## Quick Start

```python
from facefusion_repository.manager import RepositoryManager
from facefusion_repository.selector import RepositorySelector
from facefusion_repository.settings import SettingsManager

# Create repository manager
manager = RepositoryManager('.face_repository')

# Add person with quality filtering
person = manager.create_person(
    'person_name',
    ['face1.jpg', 'face2.jpg'],
    quality_threshold=0.7
)

# Create selector for quality-based selection
selector = RepositorySelector(manager)
best_face = selector.get_best_person_face('person_name', quality_threshold=0.8)

# Manage settings profiles
settings_manager = SettingsManager('.face_repository')
profiles = settings_manager.list_profiles()
print(f"Available profiles: {profiles}")
```

## CLI Examples

### Add Person with Quality Filtering
```bash
python facefusion.py repo-add \
    --person "Marie" \
    --face-paths face1.jpg face2.jpg face3.jpg \
    --quality-threshold 0.7
```

### Execute with Best Quality Face
```bash
python facefusion.py repo-execute \
    --person "Marie" \
    --face-selector-mode "best-quality" \
    --quality-threshold 0.8 \
    --target video.mp4 \
    --output result.mp4 \
    --processors face_swapper
```

### Settings Management
```bash
# List profiles
python facefusion.py repo-settings-list

# Show profile details
python facefusion.py repo-settings-show --profile-name "high_quality"

# Export profile
python facefusion.py repo-settings-export \
    --profile-name "high_quality" \
    --settings-file my_settings.json

# Import profile
python facefusion.py repo-settings-import \
    --profile-name "custom_profile" \
    --settings-file my_settings.json
```

## Documentation

See REPOSITORY.md in the root directory for complete documentation of all enhanced features.
