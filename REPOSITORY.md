# FaceFusion Repository System

The Repository System provides person-based face management for FaceFusion, allowing you to create a library of faces organized by person and use them for face swapping operations.

## Features

- **Person Management**: Create, list, and remove persons with associated face images
- **Face Storage**: Automatic organization and storage of face images by person
- **Quality Assessment**: Multi-metric quality evaluation (sharpness, brightness, contrast, resolution)
- **Pose-Aware Selection**: 3D pose-based face matching with configurable tolerance
- **Fallback Selection**: Define fallback persons when primary person not found
- **Settings Management**: Save and reuse processing configurations
- **GUI Integration**: Visual interface for managing persons and selecting faces
- **CLI Support**: Complete command-line interface for all operations

## CLI Usage

### Adding a Person to Repository

Add a new person with one or more face images:

```bash
python facefusion.py repo-add \
    --person "Marie" \
    --face-paths face1.jpg face2.jpg face3.jpg
```

#### With Quality Filtering

Filter faces by quality threshold during addition:

```bash
python facefusion.py repo-add \
    --person "Marie" \
    --face-paths face1.jpg face2.jpg face3.jpg face4.jpg \
    --quality-threshold 0.7
```

Only faces with quality score >= 0.7 will be added. Quality metrics include:
- **Sharpness**: Laplacian variance-based sharpness detection
- **Brightness**: Optimal luminance analysis
- **Contrast**: Standard deviation-based contrast measurement
- **Resolution**: Native resolution scoring
- **Overall**: Weighted combination of all metrics

### Listing Persons in Repository

List all persons currently in the repository:

```bash
python facefusion.py repo-list
```

Example output:
```
Persons in repository:
  - Marie (3 faces)
  - Alice (2 faces)
  - Sophie (1 face)
```

### Removing a Person from Repository

Remove a person and their associated face images:

```bash
python facefusion.py repo-remove --person "Marie"
```

### Executing Face Swap with Repository Person

Process a video using faces from a person in the repository:

```bash
python facefusion.py repo-execute \
    --person "Marie" \
    --target input_video.mp4 \
    --output output_video.mp4 \
    --processors face_swapper
```

#### Face Selector Modes

Control how faces are selected from the repository:

```bash
# Use best quality face only
python facefusion.py repo-execute \
    --person "Marie" \
    --face-selector-mode "best-quality" \
    --target video.mp4 \
    --output result.mp4 \
    --processors face_swapper

# Use all faces from person
python facefusion.py repo-execute \
    --person "Marie" \
    --face-selector-mode "all" \
    --target video.mp4 \
    --output result.mp4 \
    --processors face_swapper

# Use first face only
python facefusion.py repo-execute \
    --person "Marie" \
    --face-selector-mode "first" \
    --target video.mp4 \
    --output result.mp4 \
    --processors face_swapper
```

Available modes:
- **best-quality**: Select the highest quality face only
- **all**: Use all faces from the person (default)
- **first**: Use only the first face

#### With Quality Filtering

Filter faces by quality during execution:

```bash
python facefusion.py repo-execute \
    --person "Marie" \
    --quality-threshold 0.8 \
    --target video.mp4 \
    --output result.mp4 \
    --processors face_swapper
```

#### With Pose-Aware Selection

Match faces by 3D orientation (pitch, yaw, roll):

```bash
python facefusion.py repo-execute \
    --person "Marie" \
    --orientation-tolerance 15.0 \
    --target video.mp4 \
    --output result.mp4 \
    --processors face_swapper
```

The `orientation-tolerance` parameter specifies maximum angular difference in degrees for pose matching.

### Using Fallback Persons

Define fallback persons if the primary person is not found:

```bash
python facefusion.py repo-execute \
    --person "Marie" \
    --fallback-persons "Alice,Sophie,Default" \
    --target input_video.mp4 \
    --output output_video.mp4 \
    --processors face_swapper
```

### Advanced Face Selection Parameters

The repository system supports all FaceFusion face selection parameters:

```bash
python facefusion.py repo-execute \
    --person "Marie" \
    --fallback-persons "Alice" \
    --face-selector-mode "best-quality" \
    --quality-threshold 0.8 \
    --orientation-tolerance 15.0 \
    --target video.mp4 \
    --output result.mp4 \
    --processors face_swapper \
    --face-detector-model "retinaface" \
    --face-detector-score 0.6 \
    --reference-face-distance 0.5 \
    --face-mask-types "box" "region"
```

### Settings Profile Management

Save and reuse processing configurations with settings profiles.

#### List Available Profiles

```bash
python facefusion.py repo-settings-list
```

Built-in profiles:
- **high_quality**: High quality processing with best results
- **fast_processing**: Fast processing with good quality balance  
- **gpu_optimized**: Optimized for GPU processing

#### Show Profile Details

```bash
python facefusion.py repo-settings-show --profile-name "high_quality"
```

#### Export Profile to File

```bash
python facefusion.py repo-settings-export \
    --profile-name "high_quality" \
    --settings-file my_settings.json
```

#### Import Profile from File

```bash
python facefusion.py repo-settings-import \
    --profile-name "custom_profile" \
    --settings-file my_settings.json
```

#### Delete Profile

```bash
python facefusion.py repo-settings-delete --profile-name "custom_profile"
```

#### Face Selector Modes
- `many`: Process all detected faces
- `one`: Single best face per frame
- `reference`: Match against reference face
- `best-quality`: Highest quality face only

#### Face Detector Models
- `retinaface`: High accuracy detection
- `scrfd`: Balanced speed/accuracy
- `yolov8n`, `yolov8s`, `yolov8m`, `yolov8l`, `yolov8x`: YOLO variants
- `yunet`: Lightweight detection

#### Common Parameters
- `--face-detector-score`: Detection confidence threshold (0.0-1.0)
- `--face-landmarker-score`: Landmark confidence threshold (0.0-1.0)
- `--reference-face-distance`: Similarity threshold (0.0-1.5)
- `--face-mask-types`: Mask types (box, occlusion, region)

## GUI Usage

### Opening the Repository Tab

1. Launch FaceFusion with GUI:
   ```bash
   python facefusion.py run
   ```

2. The Repository section appears in the left column of the interface

### Adding a Person via GUI

1. **Enter Person Name**: Type the person's name in the "Person Name" field
2. **Upload Face Images**: Click "Face Images" and select one or more face images
3. **Click "Add Person"**: The person will be added to the repository
4. **Verify**: Check the "Persons in Repository" section to confirm

### Selecting a Person for Processing

1. **Click "Refresh List"**: Update the dropdown with current persons
2. **Select Person**: Choose a person from the "Select Person" dropdown
3. **Process**: The selected person's faces will automatically be used as source images

### Repository Status

The Status field shows:
- Success messages when adding persons
- Error messages if something goes wrong
- Current operation status

## Repository Structure

The repository is stored in `.face_repository/` (default) with the following structure:

```
.face_repository/
├── repository.json         # Person metadata and face paths
└── faces/
    ├── <person-id-1>/     # Faces for person 1
    │   ├── face1.jpg
    │   └── face2.jpg
    └── <person-id-2>/     # Faces for person 2
        └── face1.jpg
```

### Repository Data Format

The `repository.json` file stores person information:

```json
{
  "version": "1.0.0",
  "persons": {
    "person-uuid-1": {
      "person_id": "person-uuid-1",
      "display_name": "Marie",
      "face_paths": [
        ".face_repository/faces/person-uuid-1/face1.jpg",
        ".face_repository/faces/person-uuid-1/face2.jpg"
      ],
      "face_count": 2,
      "metadata": {}
    }
  }
}
```

## Configuration

### Custom Repository Location

Specify a custom repository path:

```bash
python facefusion.py repo-add \
    --repository-path /path/to/custom/repository \
    --person "Marie" \
    --face-paths face1.jpg
```

## Best Practices

### Face Image Quality

- Use high-resolution images (at least 512x512 pixels)
- Include multiple angles and expressions for pose-aware selection
- Ensure good lighting and clear facial features
- Avoid heavily edited or filtered images
- Quality threshold of 0.7-0.8 is recommended for production use
- Add 5-10 faces with varying poses for optimal coverage

### Person Organization

- Use consistent naming conventions
- Add 3-5 face images per person for best results
- Include different facial angles (front, profile, 3/4 view)
- Organize persons by use case or project

### Fallback Strategy

Define fallback persons in order of preference:
```bash
--person "PrimaryPerson" \
--fallback-persons "Backup1,Backup2,DefaultFace"
```

## Integration with FaceFusion

The repository system integrates seamlessly with FaceFusion's existing features:

- **Face Swapping**: Use repository persons as source faces
- **Face Selection**: All face selector modes work with repository faces
- **Batch Processing**: Process multiple videos with the same person
- **Job System**: Create jobs using repository persons

## Troubleshooting

### "Person not found" Error

- Verify the person name matches exactly (case-sensitive)
- Run `repo-list` to see available persons
- Check that faces were successfully added

### "No faces found" Error

- Ensure face images are valid and exist
- Check file permissions
- Verify images contain detectable faces

### Repository Not Updating in GUI

- Click the "Refresh List" button
- Restart the GUI if changes were made via CLI

## Examples

### Example 1: Basic Workflow

```bash
# 1. Add a person
python facefusion.py repo-add \
    --person "John" \
    --face-paths john_front.jpg john_side.jpg

# 2. List persons
python facefusion.py repo-list

# 3. Process video
python facefusion.py repo-execute \
    --person "John" \
    --target input.mp4 \
    --output output.mp4 \
    --processors face_swapper
```

### Example 2: Advanced Processing

```bash
python facefusion.py repo-execute \
    --person "Marie" \
    --fallback-persons "Alice" \
    --target video.mp4 \
    --output result.mp4 \
    --processors face_swapper \
    --face-selector-mode "reference" \
    --face-detector-model "retinaface" \
    --face-detector-score 0.7 \
    --reference-face-distance 0.4 \
    --execution-providers cuda
```

### Example 3: Batch Processing

```bash
# Process multiple videos with same person
for video in videos/*.mp4; do
    python facefusion.py repo-execute \
        --person "Marie" \
        --target "$video" \
        --output "output/$(basename $video)" \
        --processors face_swapper
done
```

## API Reference

### RepositoryManager

```python
from facefusion_repository.manager import RepositoryManager

# Create manager
manager = RepositoryManager(repository_path='.face_repository')

# Add person
person = manager.create_person('Marie', ['face1.jpg', 'face2.jpg'])

# List persons
persons = manager.list_persons()

# Get person by name
person = manager.get_person_by_name('Marie')

# Remove person
manager.remove_person(person_id)
```

### RepositorySelector

```python
from facefusion_repository.selector import RepositorySelector

# Create selector
selector = RepositorySelector(manager)

# Get faces for person
face_paths = selector.get_person_faces('Marie')

# Select with fallback
face_paths = selector.select_faces_for_person('Marie', ['Alice', 'Sophie'])
```

## Support

For issues or questions:
- Check the troubleshooting section above
- Review FaceFusion documentation
- Ensure all face images are valid and accessible
