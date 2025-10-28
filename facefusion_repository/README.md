# FaceFusion Repository System

## Overview

The FaceFusion Repository System provides person-centric face management for FaceFusion. It allows you to organize faces by person, manage face quality, and streamline face swapping workflows.

## Features

- **Person-Centric Organization**: Group faces by person for easy management
- **Quality Assessment**: Automatic evaluation of face image quality
- **3D Pose Analysis**: Face orientation and pose detection
- **JSON-Based Storage**: Simple, portable repository format
- **CLI Integration**: Seamless integration with FaceFusion CLI
- **Type-Safe**: Complete type hints for all modules

## Installation

The repository system is included with FaceFusion. No additional installation required.

## Usage

### Initialize Repository

Initialize a new face repository:

```bash
python facefusion.py repo-init
```

This creates a `.facefusion_repository` directory with the following structure:
```
.facefusion_repository/
├── repository.json    # Database of persons and faces
└── faces/            # Directory containing face images
    └── {person_id}/  # Subdirectory for each person
```

### Add Faces to Repository

Add a face to a person's collection:

```bash
python facefusion.py repo-add --source path/to/face.jpg --person "John Doe"
```

With quality preview:

```bash
python facefusion.py repo-add --source path/to/face.jpg --person "John Doe" --preview
```

### List Persons

List all persons in the repository:

```bash
python facefusion.py repo-list
```

### List Faces for a Person

List all faces for a specific person:

```bash
python facefusion.py repo-list --person "John Doe"
```

## Repository Structure

### Person Entry

Each person in the repository has:
- Unique person ID
- Person name
- Collection of faces
- Creation and modification timestamps

### Face Entry

Each face entry includes:
- Unique face ID
- Image paths (original and repository copy)
- 3D pose information (yaw, pitch, roll)
- Quality metrics (sharpness, brightness, overall quality)
- Face embeddings (for recognition)
- Tags for organization

## Architecture

### Core Modules

- **person_manager.py**: Manages person entities and operations
- **face_analyzer.py**: Analyzes face pose and orientation
- **quality_assessor.py**: Evaluates face image quality

### Storage Modules

- **json_storage.py**: JSON-based persistence layer
- **file_manager.py**: File system operations

### CLI Module

- **repository_cli.py**: Command-line interface implementation

## Type System

The repository system includes comprehensive type definitions:

- `RepositoryPersonId`: Person identifier
- `RepositoryFaceId`: Face identifier
- `RepositoryPose3D`: 3D pose information (yaw, pitch, roll, confidence)
- `RepositoryQualityMetrics`: Quality metrics (sharpness, brightness, occlusion)
- `RepositoryPersonFace`: Complete face metadata
- `RepositoryEntry`: Person entry with all faces

## Integration with FaceFusion

The repository system integrates seamlessly with FaceFusion:

1. **Non-Breaking**: Existing workflows are unaffected
2. **Modular**: Lives in separate `facefusion_repository/` directory
3. **Type-Safe**: Uses FaceFusion's type system
4. **CLI Compatible**: Follows FaceFusion command patterns

## Quality Assessment

Faces are automatically assessed for:

- **Sharpness**: Image clarity using Laplacian variance
- **Brightness**: Optimal lighting conditions
- **Overall Quality**: Combined quality score
- **Occlusion Detection**: Checks for face obstructions

Quality scores range from 0.0 to 1.0, with higher values indicating better quality.

## 3D Pose Analysis

The system analyzes face orientation:

- **Yaw**: Horizontal rotation (left/right)
- **Pitch**: Vertical rotation (up/down)
- **Roll**: Tilt angle
- **Confidence**: Reliability of pose estimation

Pose categories:
- `frontal`: Face looking straight ahead (< 15°)
- `slight_turn`: Minor rotation (15-30°)
- `profile`: Side view (30-60°)
- `extreme`: Extreme angle (> 60°)

## Future Enhancements

Planned features:

- [ ] GUI integration with Gradio tabs
- [ ] Preset management (person + settings combinations)
- [ ] Advanced face detection integration
- [ ] Batch import from directories
- [ ] Face similarity search
- [ ] Automatic best face selection
- [ ] Export/import repository format

## Development

### Running Tests

```bash
pytest tests/test_repository.py
```

### Module Structure

```
facefusion_repository/
├── __init__.py
├── types.py              # Type definitions
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── person_manager.py
│   ├── face_analyzer.py
│   └── quality_assessor.py
├── storage/              # Persistence layer
│   ├── __init__.py
│   ├── json_storage.py
│   └── file_manager.py
├── cli/                  # CLI interface
│   ├── __init__.py
│   └── repository_cli.py
└── gui/                  # GUI components (placeholder)
    ├── __init__.py
    └── repository_tabs.py
```

## Contributing

When contributing to the repository system:

1. Follow existing FaceFusion code style
2. Add type hints to all functions
3. Write tests for new features
4. Update documentation
5. Ensure backward compatibility

## License

Same as FaceFusion main project.
