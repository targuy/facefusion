# Module 4: Named Presets System - User Guide

## Overview

Module 4 provides a powerful system for creating and managing named presets that combine repository faces with settings profiles. This enables quick, consistent face swap operations with predefined configurations.

## Key Concepts

### What is a Preset?

A **preset** is a named combination of:
- A **face** from the repository (Module 1)
- A **settings profile** (Module 3)
- Metadata (description, tags, usage statistics)

Presets allow you to:
- Save frequently used configurations
- Ensure consistent results
- Share configurations with others
- Track usage statistics

### What are Settings Profiles?

**Settings profiles** store FaceFusion configuration parameters such as:
- Processors to use (face_swapper, face_enhancer, etc.)
- Face detection models and parameters
- Face masking options
- Output quality settings

## Quick Start

### 1. Create a Settings Profile

First, create a settings profile or use a built-in template:

```bash
# Create from a template
python facefusion_repo_cli.py settings-create \
    --name high_quality \
    --template high_quality \
    --description "High quality face swapping"

# Create from a JSON file
python facefusion_repo_cli.py settings-create \
    --name custom_settings \
    --file my_settings.json \
    --description "Custom configuration"
```

**Available Templates:**
- `high_quality` - Best quality settings
- `fast_processing` - Faster processing with good quality
- `enhanced_quality` - Enhanced with face enhancer
- `video_optimized` - Optimized for video processing

### 2. Create a Preset

Combine a face from your repository with a settings profile:

```bash
python facefusion_repo_cli.py presets-create \
    --name "alice_frontal_hq" \
    --face-id face_20251028_abc123 \
    --settings high_quality \
    --description "Alice frontal view with high quality" \
    --tags alice,frontal,high-quality
```

### 3. List and View Presets

```bash
# List all presets
python facefusion_repo_cli.py presets-list

# Show detailed preset information
python facefusion_repo_cli.py presets-show --name alice_frontal_hq

# List presets filtered by face
python facefusion_repo_cli.py presets-list --face-id face_20251028_abc123

# List presets filtered by settings
python facefusion_repo_cli.py presets-list --settings high_quality
```

### 4. Apply a Preset

Get the complete configuration for a preset:

```bash
python facefusion_repo_cli.py presets-apply --name alice_frontal_hq
```

This shows:
- Face file path
- Settings profile details
- Metadata (orientation, quality, etc.)
- Complete settings configuration

## Settings Management

### Creating Settings Profiles

**From a template:**
```bash
python facefusion_repo_cli.py settings-create \
    --name my_profile \
    --template high_quality
```

**From a JSON file:**
```bash
python facefusion_repo_cli.py settings-create \
    --name my_profile \
    --file settings.json
```

Example JSON structure:
```json
{
  "name": "custom_profile",
  "description": "Custom settings",
  "settings": {
    "processors": ["face_swapper"],
    "face_detector_model": "yolo_face",
    "face_detector_size": "640x640",
    "face_detector_score": 0.5,
    "face_landmarker_model": "2dfan4",
    "face_masker_types": ["box", "region"],
    "face_mask_blur": 0.3
  }
}
```

### Managing Settings Profiles

**List all profiles:**
```bash
python facefusion_repo_cli.py settings-list
```

**Show profile details:**
```bash
python facefusion_repo_cli.py settings-show --name high_quality
```

**Delete a profile:**
```bash
python facefusion_repo_cli.py settings-delete --name old_profile
```

### Exporting and Importing Settings

**Export a profile:**
```bash
python facefusion_repo_cli.py settings-export \
    --name high_quality \
    --output high_quality.json
```

**Import a profile:**
```bash
python facefusion_repo_cli.py settings-import \
    --file high_quality.json \
    --name imported_profile
```

## Preset Management

### Creating Presets

**Basic preset creation:**
```bash
python facefusion_repo_cli.py presets-create \
    --name "my_preset" \
    --face-id face_20251028_abc123 \
    --settings high_quality \
    --description "Description here"
```

**With tags for organization:**
```bash
python facefusion_repo_cli.py presets-create \
    --name "alice_profile_left" \
    --face-id face_20251028_xyz789 \
    --settings video_optimized \
    --description "Alice left profile for video" \
    --tags alice,profile,video
```

### Updating Presets

Update face, settings, or description:

```bash
# Update face ID
python facefusion_repo_cli.py presets-update \
    --name my_preset \
    --face-id new_face_id

# Update settings profile
python facefusion_repo_cli.py presets-update \
    --name my_preset \
    --settings new_settings

# Update description
python facefusion_repo_cli.py presets-update \
    --name my_preset \
    --description "New description"
```

### Copying Presets

Create variations of existing presets:

```bash
# Exact copy
python facefusion_repo_cli.py presets-copy \
    --source original_preset \
    --name new_preset

# Copy with different face
python facefusion_repo_cli.py presets-copy \
    --source original_preset \
    --name new_preset \
    --face-id different_face_id

# Copy with different settings
python facefusion_repo_cli.py presets-copy \
    --source original_preset \
    --name new_preset \
    --settings different_settings
```

### Validating Presets

Check if a preset is valid and ready to use:

```bash
python facefusion_repo_cli.py presets-validate --name my_preset
```

This checks:
- Face exists in repository
- Face file is accessible
- Settings profile exists
- Settings are valid
- Face and settings are compatible

### Deleting Presets

```bash
python facefusion_repo_cli.py presets-delete --name old_preset
```

### Exporting and Importing Presets

**Export a preset:**
```bash
python facefusion_repo_cli.py presets-export \
    --name my_preset \
    --output my_preset.json
```

**Import a preset:**
```bash
python facefusion_repo_cli.py presets-import \
    --file my_preset.json \
    --name imported_preset
```

## Preset Templates

The system includes built-in templates for common use cases:

### High Quality Template
- **Use case:** Best quality results
- **Settings:**
  - Processor: face_swapper
  - Detector: yolo_face (640x640)
  - Masker: box + region
  - Blur: 0.3

### Fast Processing Template
- **Use case:** Faster processing times
- **Settings:**
  - Processor: face_swapper
  - Detector: yunet (320x320)
  - Masker: box only
  - Blur: 0.2

### Enhanced Quality Template
- **Use case:** Maximum quality with enhancement
- **Settings:**
  - Processors: face_swapper + face_enhancer
  - Detector: yolo_face (960x960)
  - Masker: occlusion + region
  - Blur: 0.4

### Video Optimized Template
- **Use case:** Processing videos efficiently
- **Settings:**
  - Processor: face_swapper
  - Selector mode: many (for multiple faces)
  - Detector: yolo_face (640x640)
  - Masker: box + region

## Preset Collections (Future Enhancement)

Collections allow grouping related presets:

```python
# Python API (for future integration)
from facefusion_repository.presets.collection import PresetCollection

collection = PresetCollection()

# Create a collection
collection.create_collection(
    name='alice_all_angles',
    preset_names=[
        'alice_frontal',
        'alice_profile_left',
        'alice_profile_right',
        'alice_three_quarter'
    ],
    description='All angles of Alice'
)
```

## Best Practices

### 1. Naming Conventions

Use clear, descriptive names:
- Include person name: `alice_frontal_hq`
- Include orientation: `bob_profile_left`
- Include quality level: `charlie_enhanced`
- Include use case: `david_video_optimized`

### 2. Tagging Strategy

Use tags for organization:
- Person name: `alice`, `bob`
- Orientation: `frontal`, `profile`, `three-quarter`
- Quality: `high-quality`, `standard`, `fast`
- Use case: `video`, `photo`, `enhanced`

### 3. Settings Organization

Create multiple settings profiles:
- One for high-quality photos
- One for fast video processing
- One for enhanced output
- Custom profiles for specific needs

### 4. Validation

Always validate presets after creation:
```bash
python facefusion_repo_cli.py presets-validate --name my_preset
```

### 5. Documentation

Add meaningful descriptions:
```bash
--description "Alice frontal view, high quality settings for portrait photos"
```

## Python API Examples

### Settings Management

```python
from facefusion_repository.settings.manager import SettingsManager

# Initialize manager
manager = SettingsManager()

# Create profile
settings = {
    'processors': ['face_swapper'],
    'face_detector_model': 'yolo_face',
    'face_detector_size': '640x640'
}
manager.create_profile('my_profile', settings, 'My custom profile')

# List profiles
profiles = manager.list_profiles()

# Get profile
profile = manager.get_profile('my_profile')

# Update profile
manager.update_profile('my_profile', settings=new_settings)

# Delete profile
manager.delete_profile('my_profile')
```

### Preset Management

```python
from facefusion_repository.presets.manager import PresetManager

# Initialize manager
manager = PresetManager()

# Create preset
manager.create_preset(
    name='alice_frontal',
    face_id='face_20251028_abc123',
    settings_profile='high_quality',
    description='Alice frontal view'
)

# List presets
presets = manager.list_presets()

# Get preset
preset = manager.get_preset('alice_frontal')

# Apply preset
from facefusion_repository.presets.applicator import PresetApplicator
applicator = PresetApplicator()
config = applicator.apply_preset('alice_frontal')

# Access configuration
face_path = config['face_path']
settings = config['settings']
```

### Preset Validation

```python
from facefusion_repository.presets.validator import PresetValidator
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.settings.manager import SettingsManager

# Initialize validator
repo = RepositoryManager()
settings_mgr = SettingsManager()
validator = PresetValidator(repo, settings_mgr)

# Validate preset
result = validator.validate_preset('face_id', 'settings_profile')
if result.valid:
    print('Preset is valid')
else:
    print(f'Errors: {result.errors}')
    print(f'Warnings: {result.warnings}')
```

### Preset Templates

```python
from facefusion_repository.presets.template import PresetTemplate
from facefusion_repository.settings.manager import SettingsManager

# List available templates
templates = PresetTemplate.list_templates()
print(f'Available templates: {templates}')

# Get template settings
settings = PresetTemplate.get_template('high_quality')

# Create settings from template
settings_mgr = SettingsManager()
PresetTemplate.create_template_settings('high_quality', settings_mgr)

# Generate preset from template
from facefusion_repository.repository.manager import RepositoryManager
repo = RepositoryManager()
PresetTemplate.generate_preset_from_template(
    preset_name='my_preset',
    face_id='face_id',
    template_name='high_quality',
    repository_manager=repo,
    settings_manager=settings_mgr
)
```

## Troubleshooting

### Preset Validation Fails

**Problem:** Preset validation returns errors

**Solutions:**
1. Check face exists: `python facefusion_repo_cli.py show --face-id <id>`
2. Check settings exist: `python facefusion_repo_cli.py settings-show --name <name>`
3. Verify face file is accessible
4. Check settings are valid

### Settings Validation Fails

**Problem:** Settings profile validation fails

**Solutions:**
1. Check processor names are valid
2. Verify model names exist
3. Ensure score values are between 0.0 and 1.0
4. Check list parameters have correct format

### Import Fails

**Problem:** Cannot import preset or settings

**Solutions:**
1. Verify JSON file format is correct
2. Check file path is accessible
3. Ensure all required fields are present
4. Validate settings in the imported file

## Advanced Usage

### Batch Preset Creation

Create multiple presets from repository faces:

```python
from facefusion_repository.presets.template import PresetTemplate
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.settings.manager import SettingsManager

repo = RepositoryManager()
settings_mgr = SettingsManager()

# Generate presets for all faces using a template
count = PresetTemplate.generate_smart_presets(
    repository_manager=repo,
    settings_manager=settings_mgr,
    template_name='high_quality'
)
print(f'Created {count} presets')
```

### Orientation-Based Presets

Create presets for different orientations:

```python
count = PresetTemplate.generate_orientation_presets(
    base_name='alice',
    repository_manager=repo,
    settings_manager=settings_mgr
)
print(f'Created {count} orientation presets')
```

This creates presets like:
- `alice_0deg`
- `alice_45deg`
- `alice_90deg`
- etc.

## Integration with FaceFusion

Presets are designed to work seamlessly with FaceFusion:

1. **Get preset configuration:**
   ```bash
   python facefusion_repo_cli.py presets-apply --name my_preset
   ```

2. **Extract face path and settings**

3. **Use with FaceFusion:**
   ```bash
   python facefusion.py run \
       --source-path <face_path_from_preset> \
       <settings_from_preset> \
       --target-path destination.mp4 \
       --output-path output.mp4
   ```

## Summary

Module 4 provides a complete preset management system:

- **Settings Profiles:** Store and manage FaceFusion configurations
- **Presets:** Combine faces with settings for quick access
- **Templates:** Built-in templates for common use cases
- **Validation:** Ensure presets are ready to use
- **Import/Export:** Share configurations
- **CLI Interface:** Full command-line control
- **Python API:** Programmatic access for automation

For more information, see:
- `SPECIFICATIONS.md` - Technical specifications
- `ARCHITECTURE.md` - System architecture
- `MANUAL.md` - Complete user manual
