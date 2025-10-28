# Repository System Integration - User Guide

## What's New

FaceFusion now includes a **Repository System** for person-centric face management. This allows you to:

- Organize faces by person
- Manage face quality and selection
- Streamline your face-swapping workflows
- Store and reuse face collections

## Quick Start

### 1. Initialize Repository

Create a new face repository:

```bash
python facefusion.py repo-init
```

This creates a `.facefusion_repository` directory to store your face collections.

### 2. Add Faces

Add a face to your repository:

```bash
python facefusion.py repo-add --source path/to/image.jpg --person "John Doe"
```

With quality preview:

```bash
python facefusion.py repo-add --source path/to/image.jpg --person "Alice" --preview
```

### 3. List Your Collection

View all persons:

```bash
python facefusion.py repo-list
```

View faces for a specific person:

```bash
python facefusion.py repo-list --person "John Doe"
```

## Commands Reference

### `repo-init`

Initialize a new face repository.

**Usage:**
```bash
python facefusion.py repo-init [--log-level LEVEL]
```

**Options:**
- `--log-level`: Set logging level (error, warn, info, debug)

### `repo-add`

Add a face to the repository.

**Usage:**
```bash
python facefusion.py repo-add --source IMAGE --person NAME [--preview] [--log-level LEVEL]
```

**Required Options:**
- `-s, --source`: Path to the source image containing the face
- `-p, --person`: Name of the person

**Optional Options:**
- `--preview`: Display quality assessment before adding
- `--log-level`: Set logging level

**Examples:**
```bash
# Add a face
python facefusion.py repo-add -s face.jpg -p "Bob"

# Add with quality preview
python facefusion.py repo-add -s face.jpg -p "Alice" --preview

# Add with debug logging
python facefusion.py repo-add -s face.jpg -p "Charlie" --log-level debug
```

### `repo-list`

List persons or faces in the repository.

**Usage:**
```bash
python facefusion.py repo-list [--person NAME] [--log-level LEVEL]
```

**Optional Options:**
- `-p, --person`: Filter by person name to show their faces
- `--log-level`: Set logging level

**Examples:**
```bash
# List all persons
python facefusion.py repo-list

# List faces for a specific person
python facefusion.py repo-list --person "Alice"
```

## Repository Structure

The repository is stored in `.facefusion_repository/`:

```
.facefusion_repository/
├── repository.json          # Database file
└── faces/                   # Face images
    ├── person_id_1/        # Faces for person 1
    │   ├── face_abc123.jpg
    │   └── face_def456.jpg
    └── person_id_2/        # Faces for person 2
        └── face_ghi789.jpg
```

### Database Format

The `repository.json` file stores:

- **Version**: Repository format version
- **Persons**: List of person entries

Each person entry contains:
- `person_id`: Unique identifier
- `person_name`: Display name
- `faces`: Array of face entries
- `created_date`: Creation timestamp
- `modified_date`: Last modification timestamp

Each face entry contains:
- `face_id`: Unique identifier
- `image_path`: Original image path
- `face_path`: Repository copy path
- `pose_3d`: 3D orientation (yaw, pitch, roll)
- `quality`: Quality metrics (sharpness, brightness)
- `added_date`: Addition timestamp
- `tags`: Optional tags

## Quality Assessment

When adding faces, the system automatically evaluates:

### Sharpness
Measures image clarity. Higher values indicate sharper, clearer images.

### Brightness
Evaluates lighting conditions. Optimal range is 30-70% brightness.

### Overall Quality
Combined score from 0.0 to 1.0. Higher is better.

### Pose Analysis
Detects face orientation:
- **Yaw**: Left/right rotation
- **Pitch**: Up/down rotation
- **Roll**: Tilt angle

Best results typically come from frontal faces (< 15° rotation).

## Best Practices

1. **Use High-Quality Source Images**
   - Clear, sharp images
   - Good lighting (not too dark or bright)
   - Minimal blur or noise

2. **Frontal Faces Work Best**
   - Face looking at camera
   - Minimal tilt or rotation
   - Clear facial features

3. **Multiple Faces Per Person**
   - Add several faces per person
   - Vary lighting and expressions
   - System will use best quality automatically

4. **Organize with Names**
   - Use consistent person names
   - Names are case-insensitive
   - Spaces are allowed

## Troubleshooting

### "Repository not initialized"

**Problem:** Trying to add faces before initializing.

**Solution:**
```bash
python facefusion.py repo-init
```

### "Source file not found"

**Problem:** Image path is incorrect.

**Solution:** Check the file path and ensure the file exists:
```bash
ls -l path/to/image.jpg
```

### "Person not found"

**Problem:** Trying to list faces for non-existent person.

**Solution:** List all persons first:
```bash
python facefusion.py repo-list
```

## Integration with Existing Workflows

The repository system is **fully backward compatible**:

- Existing FaceFusion commands work unchanged
- Repository is optional - only used if you initialize it
- No impact on performance of standard workflows
- Can be used alongside traditional source/target workflow

## Future Enhancements

Planned features (not yet implemented):

- GUI integration with Gradio interface
- Preset management (person + settings)
- Direct face swap from repository
- Batch import from directories
- Face similarity search
- Automatic best face selection

## Technical Details

### Type Safety
The system uses Python type hints throughout:
- `RepositoryPersonId`: Person identifier type
- `RepositoryFaceId`: Face identifier type
- `RepositoryPose3D`: 3D pose information
- `RepositoryQualityMetrics`: Quality metrics
- Full TypedDict definitions

### Storage Format
- JSON-based for portability
- Human-readable format
- Easy backup and version control
- Cross-platform compatible

### Module Architecture
```
facefusion_repository/
├── core/          # Business logic
├── storage/       # Persistence layer
├── cli/           # Command interface
└── gui/           # GUI components (future)
```

## Support

For issues or questions:
1. Check this documentation
2. Review the README in `facefusion_repository/`
3. File issues on GitHub

## See Also

- [Repository README](facefusion_repository/README.md) - Developer documentation
- [FaceFusion Documentation](README.md) - Main documentation
