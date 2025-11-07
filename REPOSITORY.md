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

## Import Preview and Zone-Specific Face Management

The repository system now includes advanced preview capabilities and zone-specific face management for optimal 3D face coverage.

### Preview on Test Faces

Generate previews of face imports on test faces before committing them to the repository:

```bash
# Add face with preview
python facefusion.py repo-add \
    --person "Marie" \
    --face-paths new_face.jpg \
    --preview-on-test-faces \
    --test-faces-dir ./test_faces
```

This will:
1. Load test faces from the specified directory
2. Generate preview transformations for each test face
3. Display preview results and quality scores
4. Add the face to repository if acceptable

### Interactive Mode

Use interactive mode for preview approval and conflict resolution:

```bash
python facefusion.py repo-add \
    --person "Marie" \
    --face-paths new_face.jpg \
    --preview-on-test-faces \
    --interactive
```

In interactive mode, the system will:
- Show preview results on test faces
- Ask for user confirmation before adding
- Handle orientation overlaps with side-by-side comparison
- Allow zone-specific face selection for optimal coverage

### Test Faces Management

Test faces are sample images used for preview generation. They should represent typical target scenarios:

**Setting up test faces directory:**

```bash
# Directory structure
test_faces/
├── front_face.jpg        # Frontal view
├── profile_left.jpg      # Left profile
├── profile_right.jpg     # Right profile
├── looking_up.jpg        # Face looking up
├── looking_down.jpg      # Face looking down
└── README.md             # Auto-generated guide
```

**Using custom test faces directory:**

```bash
python facefusion.py repo-add \
    --person "Marie" \
    --face-paths face.jpg \
    --preview-on-test-faces \
    --test-faces-dir /path/to/custom/test_faces
```

### Zone-Specific Coverage

The system manages 3D face coverage zones to optimize face selection:

**Coverage Zone Concept:**
- Each face has a specific orientation (pitch, yaw, roll)
- Coverage zones define angle ranges where the face performs best
- Multiple faces can coexist with non-overlapping zones
- System automatically selects optimal face for each target orientation

**Metadata Structure:**

Each face stores:
- **Orientation**: Center pose (pitch, yaw, roll in degrees)
- **Coverage Zones**: Angle ranges where face is effective
- **Quality Metrics**: Quality scores for the face
- **Preview Results**: Quality scores on test faces

**Overlap Resolution:**

When orientation overlap is detected:
1. System compares faces on multiple test cases
2. Shows side-by-side quality comparison
3. Allows user to choose preferred face per zone (in interactive mode)
4. Assigns non-overlapping coverage zones to both faces

### API Usage

**Generate Import Preview:**

```python
from facefusion_repository.manager import RepositoryManager

manager = RepositoryManager('.face_repository')

# Preview face import
preview_result = manager.preview_face_import(
    'new_face.jpg',
    test_faces_dir='./test_faces',
    max_test_faces=5
)

if preview_result['success']:
    for test_face, result in preview_result['preview_results'].items():
        print(f"Test face: {test_face}")
        print(f"Quality: {result.quality_score:.2f}")
        print(f"Preview: {result.preview_path}")
```

**Compare Faces on Test Cases:**

```python
# Compare existing vs new face
comparison = manager.compare_faces_on_test_cases(
    'existing_face.jpg',
    'new_face.jpg',
    test_faces_dir='./test_faces'
)

if comparison['success']:
    for test_face, comp_result in comparison['comparison_results'].items():
        print(f"Test face: {test_face}")
        print(f"Existing quality: {comp_result.existing_preview.quality_score:.2f}")
        print(f"New quality: {comp_result.new_preview.quality_score:.2f}")
        print(f"Winner: {comp_result.winner}")
```

**Zone Management:**

```python
from facefusion_repository.zone_manager import (
    calculate_zone_from_orientation,
    check_zone_overlap,
    format_zone_description
)

# Calculate coverage zone
orientation = {'pitch': 10.0, 'yaw': 20.0, 'roll': 5.0}
zone = calculate_zone_from_orientation(orientation, tolerance=15.0)

# Check for overlaps
zone1 = calculate_zone_from_orientation(orientation1, tolerance=15.0)
zone2 = calculate_zone_from_orientation(orientation2, tolerance=15.0)
has_overlap = check_zone_overlap(zone1, zone2)

# Format zone for display
description = format_zone_description(zone)
print(description)
# Output: "Pitch: [-5.0°, 25.0°], Yaw: [5.0°, 35.0°], Roll: [-10.0°, 20.0°]"
```

**Test Faces Management:**

```python
from facefusion_repository.test_faces import (
    get_test_faces,
    create_test_faces_directory,
    add_test_face
)

# Get test faces
test_faces = get_test_faces('./test_faces', max_count=5)

# Create test faces directory
test_dir = create_test_faces_directory('./test_faces')

# Add a test face
success = add_test_face('my_face.jpg', './test_faces')
```

### Best Practices

**Test Faces:**
- Use 5-10 diverse test faces covering different orientations
- Include frontal, profile, and angled views
- Use good quality images (sharp, well-lit)
- Representative of typical use cases

**Preview Workflow:**
- Always preview faces before adding to repository
- Review quality scores on multiple test faces
- Accept faces that perform well across orientations
- Reject low-quality or problematic faces

**Zone Management:**
- Let system handle zone assignment automatically
- Use interactive mode for manual control when needed
- Keep multiple faces for better orientation coverage
- Monitor face metadata for optimal zone distribution

### Troubleshooting

**No test faces found:**
```
Solution: Create test faces directory and add sample images
$ mkdir -p test_faces
$ cp your_test_images/*.jpg test_faces/
```

**Preview generation fails:**
```
Solution: Ensure test faces are valid images and accessible
Check file permissions and image formats (jpg, png, etc.)
```

**Zone conflicts:**
```
Solution: Use interactive mode to resolve manually
System will show comparison and let you choose per zone
```

### Benefits

1. **Quality Assurance**: See actual results before committing faces
2. **Optimal Coverage**: Best face for each 3D zone, not just global replacement
3. **Fine Control**: Zone-specific management without losing good faces
4. **Visual Feedback**: Clear comparison interface for informed decisions
5. **Better Results**: Improved swap quality through preview-based selection

