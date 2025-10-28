# Settings Profile Management User Guide

## Overview

Module 3 provides comprehensive management of FaceFusion configuration parameters through a settings profile system. Settings profiles allow you to save, organize, and reuse different FaceFusion configurations for various use cases.

## Quick Start

### 1. View Available Templates

```bash
python facefusion_repo_cli.py settings-templates
```

This displays all pre-configured settings templates:
- `default_swap` - Basic face swap with balanced quality and performance
- `high_quality` - High-quality face swap with face enhancement
- `fast_preview` - Fast preview mode for testing
- `gpu_accelerated` - Optimized for GPU acceleration
- `multi_face` - Swap multiple faces in the same frame
- `reference_face` - Use reference face for selective swapping

### 2. Create a Profile from Template

```bash
python facefusion_repo_cli.py settings-create \
  --name my_high_quality \
  --template high_quality \
  --tags production,high-quality
```

### 3. List Your Profiles

```bash
# List all profiles
python facefusion_repo_cli.py settings-list

# Filter by tags
python facefusion_repo_cli.py settings-list --tags production
```

### 4. View Profile Details

```bash
python facefusion_repo_cli.py settings-show --name my_high_quality
```

## Profile Management

### Creating Profiles

#### From Template

```bash
python facefusion_repo_cli.py settings-create \
  --name my_profile \
  --template default_swap \
  --description "My custom settings" \
  --tags custom,testing
```

#### From Custom JSON

Create a JSON file with your settings:

```json
{
  "processors": ["face_swapper"],
  "face_detector_model": "yoloface",
  "face_detector_size": "640x640",
  "face_detector_score": 0.5,
  "execution_providers": ["cpu"],
  "output_video_quality": 80
}
```

Then create the profile:

```bash
python facefusion_repo_cli.py settings-create \
  --name my_custom_profile \
  --settings-file settings.json \
  --description "Custom configuration"
```

### Updating Profiles

#### Update Settings

```bash
python facefusion_repo_cli.py settings-update \
  --name my_profile \
  --settings-file new_settings.json
```

#### Update Description

```bash
python facefusion_repo_cli.py settings-update \
  --name my_profile \
  --description "Updated description"
```

#### Update Tags

```bash
python facefusion_repo_cli.py settings-update \
  --name my_profile \
  --tags production,reviewed,tested
```

### Deleting Profiles

```bash
python facefusion_repo_cli.py settings-delete --name my_profile
```

## Profile Validation

Validate a profile to ensure all settings are correct:

```bash
python facefusion_repo_cli.py settings-validate --name my_profile
```

The validator checks:
- Valid processor names
- Correct model selections
- Proper value ranges (scores, quality, etc.)
- List format for array parameters
- Execution provider compatibility

## Comparing Profiles

Compare two profiles to see their differences:

```bash
python facefusion_repo_cli.py settings-compare \
  --profile1 default_swap \
  --profile2 high_quality
```

The comparison shows:
- **Different Settings**: Parameters with different values
- **Only in Profile 1**: Settings unique to first profile
- **Only in Profile 2**: Settings unique to second profile
- **Common Settings**: Identical parameters
- **Critical Differences**: Important settings that significantly affect behavior

## Import/Export

### Export Profile

Export a profile to share or backup:

```bash
python facefusion_repo_cli.py settings-export \
  --name my_profile \
  --output ~/backups/my_profile.json
```

### Import Profile

Import a profile from a file:

```bash
python facefusion_repo_cli.py settings-import \
  --input ~/shared/profile.json

# Or import with a new name
python facefusion_repo_cli.py settings-import \
  --input ~/shared/profile.json \
  --name imported_profile
```

## Settings Reference

### Processors

Available processors:
- `face_swapper` - Swap faces
- `face_enhancer` - Enhance face quality
- `face_debugger` - Debug face detection
- `frame_enhancer` - Enhance overall frame quality
- `frame_colorizer` - Colorize frames
- `lip_syncer` - Synchronize lip movements
- `age_modifier` - Modify age appearance
- `expression_restorer` - Restore facial expressions

### Face Detection

**Models**: `many`, `retinaface`, `scrfd`, `yoloface`, `yunet`

**Sizes**: `160x160`, `320x320`, `480x480`, `512x512`, `640x640`, `768x768`, `1024x1024`

**Score**: 0.0 to 1.0 (confidence threshold)

### Face Landmarker

**Models**: `2dfan4`, `peppa_wutz`

**Score**: 0.0 to 1.0 (confidence threshold)

### Face Selector

**Modes**:
- `one` - Select one face
- `many` - Select all faces
- `reference` - Use reference face

**Orders**:
- `best-worst` - Sort by quality
- `worst-best` - Reverse quality sort
- `left-right` - Spatial ordering
- `right-left` - Reverse spatial ordering
- `small-large` - Sort by size
- `large-small` - Reverse size sort

### Face Masking

**Types**: `box`, `occlusion`, `region`

**Regions**: `skin`, `left-eyebrow`, `right-eyebrow`, `left-eye`, `right-eye`, `glasses`, `nose`, `mouth`, `upper-lip`, `lower-lip`

**Blur**: 0.0 to 1.0 (feathering amount)

**Padding**: `[top, right, bottom, left]` values from -100 to 100

### Execution

**Providers**: `cpu`, `cuda`, `coreml`, `dml`, `openvino`, `tensorrt`

**Thread Count**: 1 to 128

**Video Memory Strategy**: `strict`, `moderate`, `tolerant`

### Output Settings

**Video Encoders**: `libx264`, `libx265`, `libvpx-vp9`, `h264_nvenc`, `hevc_nvenc`, `h264_amf`, `hevc_amf`

**Video Presets**: `ultrafast`, `superfast`, `veryfast`, `faster`, `fast`, `medium`, `slow`, `slower`, `veryslow`

**Quality**: 0 to 100 (higher is better)

**Frame Format**: `bmp`, `jpg`, `png`

## Profile Storage

Profiles are stored in `~/.facefusion_repository/settings/` as JSON files.

Each profile includes:
- Name and description
- Creation and modification dates
- Version information
- Tags for organization
- Complete settings dictionary

## Best Practices

### Naming Conventions

Use descriptive names that indicate purpose:
- `production_high_quality`
- `testing_fast`
- `gpu_batch_processing`
- `reference_face_actor_a`

### Tags

Use tags to organize profiles:
- By quality: `high-quality`, `standard`, `preview`
- By use case: `production`, `testing`, `development`
- By hardware: `gpu`, `cpu`
- By project: `project-a`, `client-x`

### Validation

Always validate profiles after creation or modification:

```bash
python facefusion_repo_cli.py settings-validate --name my_profile
```

### Version Control

Export important profiles for version control:

```bash
python facefusion_repo_cli.py settings-export \
  --name production_profile \
  --output ./profiles/production_v1.json
```

## Common Use Cases

### High-Quality Production

```bash
python facefusion_repo_cli.py settings-create \
  --name production \
  --template high_quality \
  --tags production,reviewed
```

Settings include:
- Face swapper + face enhancer
- High detector scores (0.6)
- PNG frame format
- 95% output quality
- Slow preset for best quality

### Fast Testing

```bash
python facefusion_repo_cli.py settings-create \
  --name testing \
  --template fast_preview \
  --tags testing,development
```

Settings include:
- Face swapper only
- Lower detector scores (0.4)
- JPG frame format
- 60% output quality
- Ultrafast preset

### GPU Batch Processing

```bash
python facefusion_repo_cli.py settings-create \
  --name gpu_batch \
  --template gpu_accelerated \
  --tags gpu,batch
```

Settings include:
- CUDA execution provider
- Hardware encoder (h264_nvenc)
- Moderate video memory strategy
- Optimized thread count

## Troubleshooting

### Profile Not Found

If a profile isn't found:
1. Check spelling: `python facefusion_repo_cli.py settings-list`
2. Verify file exists: `ls ~/.facefusion_repository/settings/`

### Validation Errors

If validation fails:
1. Check error messages carefully
2. Verify setting values against reference
3. Use a template as starting point
4. Compare with working profile

### Import Fails

If import fails:
1. Verify JSON file is valid
2. Check file permissions
3. Ensure profile name doesn't already exist
4. Use `--name` to specify a different name

## Integration with Other Modules

Settings profiles integrate with:

- **Module 4 (Presets)**: Presets combine face + settings profile
- **Module 5 (Batch Execution)**: Apply settings to batch operations
- **Repository System**: Use with repository faces for complete workflows

## Examples

### Create Workflow-Specific Profiles

```bash
# Actor replacement profile
python facefusion_repo_cli.py settings-create \
  --name actor_replacement \
  --template reference_face \
  --tags production,vfx

# Social media preview
python facefusion_repo_cli.py settings-create \
  --name social_preview \
  --template fast_preview \
  --tags social,preview

# High-res output
python facefusion_repo_cli.py settings-create \
  --name highres_export \
  --template high_quality \
  --tags export,highres
```

### Compare Different Configurations

```bash
# Compare CPU vs GPU settings
python facefusion_repo_cli.py settings-compare \
  --profile1 default_swap \
  --profile2 gpu_accelerated

# Compare quality levels
python facefusion_repo_cli.py settings-compare \
  --profile1 fast_preview \
  --profile2 high_quality
```

## API Usage

For programmatic access:

```python
from facefusion_repository.settings import SettingsManager, ProfileValidator

# Create manager
manager = SettingsManager()

# Create profile
settings = {
    'processors': ['face_swapper'],
    'face_detector_model': 'yoloface',
    'execution_providers': ['cpu']
}

# Validate first
validation = ProfileValidator.validate_settings(settings)
if validation.valid:
    manager.create_profile('my_profile', settings, description='API created')

# List profiles
profiles = manager.list_profiles()
for profile in profiles:
    print(f"{profile.name}: {profile.description}")

# Get profile
profile = manager.get_profile('my_profile')
if profile:
    print(profile.settings)
```

## Future Enhancements

Planned features for future releases:
- Profile inheritance (derive from base profiles)
- Profile groups and categories
- Settings diff and merge tools
- Profile validation against specific FaceFusion versions
- Cloud sync for profiles
- Profile usage analytics
