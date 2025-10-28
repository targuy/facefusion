# Face Repository System

The Face Repository System allows you to store multiple face orientations per person and automatically select the optimal face for each video frame based on 3D pose similarity.

## Features

- **Multiple Face Storage**: Store faces in different orientations (front, profile, 3/4 angle, etc.)
- **Automatic Pose Matching**: Automatically selects the best repository face based on target face orientation
- **Dynamic Per-Frame Selection**: Different frames can use different repository faces for optimal results
- **3D Pose Analysis**: Calculates pitch, yaw, and roll from face landmarks
- **Quality Fallback**: Falls back to highest quality face when no close pose match is found

## Usage

### 1. Initialize Repository

```bash
python facefusion.py repo-init
```

This creates the repository structure at `~/.facefusion_repository/`.

### 2. Add Faces to Repository

Add multiple face orientations for a person:

```bash
# Add front-facing photo
python facefusion.py repo-add --person "john" --source john_front.jpg

# Add profile photo
python facefusion.py repo-add --person "john" --source john_profile.jpg

# Add 3/4 angle photo
python facefusion.py repo-add --person "john" --source john_angle.jpg
```

The system will:
- Detect the face in each image
- Extract face landmarks and embeddings
- Calculate 3D pose (pitch/yaw/roll)
- Store face data in the repository

### 3. List Repository Contents

```bash
python facefusion.py repo-list
```

This displays all persons in the repository and their face counts.

### 4. Execute Face Swap with Repository

Process a video using optimal face selection:

```bash
python facefusion.py repo-execute \
  --person "john" \
  --target input_video.mp4 \
  --output result_video.mp4
```

For each frame, the system will:
1. Detect target face(s) in the frame
2. Calculate target face 3D pose
3. Compare with all repository faces for "john"
4. Select the face with most similar pose (weighted 50% yaw, 30% pitch, 20% roll)
5. Perform face swap using the selected face

### 5. Advanced Options

You can combine with existing face swapper options:

```bash
python facefusion.py repo-execute \
  --person "john" \
  --target video.mp4 \
  --output result.mp4 \
  --face-swapper-model inswapper_128 \
  --face-selector-mode many \
  --execution-providers cuda \
  --output-video-quality 90
```

## How It Works

### Pose Calculation

The system calculates 3D face pose from 5-point landmarks:
- **Pitch**: Up/down head tilt (calculated from nose-to-mouth vertical distance)
- **Yaw**: Left/right head rotation (calculated from nose offset from eye center)
- **Roll**: Head rotation around forward axis (calculated from eye line angle)

### Pose Similarity Scoring

Similarity score is calculated as:
```
similarity = 0.3 * pitch_similarity + 0.5 * yaw_similarity + 0.2 * roll_similarity
```

Note: Yaw (left-right rotation) is weighted highest (50%) as it's most impactful for face swapping quality.

Combined with face quality:
```
final_score = 0.8 * pose_similarity + 0.2 * face_quality
```

### Face Selection

1. Calculate pose similarity for all repository faces
2. Select face with highest combined score
3. If best score is below threshold (default 0.5), fall back to highest quality face
4. Cache selections to improve performance

## Best Practices

### Capturing Face Images

For best results:
- Use high-quality, well-lit images
- Include faces at various angles:
  - Front (0° yaw)
  - Left 3/4 (30-45° yaw)
  - Right 3/4 (-30 to -45° yaw)
  - Left profile (70-90° yaw)
  - Right profile (-70 to -90° yaw)
- Keep consistent lighting and quality
- Avoid extreme expressions
- Minimum 3-5 faces per person recommended

### Video Processing

- Use `--face-selector-mode reference` for consistent face tracking
- Enable GPU with `--execution-providers cuda` for faster processing
- Start with default settings, then adjust based on results

## Repository Structure

```
~/.facefusion_repository/
├── persons/
│   ├── john/
│   │   ├── face_1234567890.pkl    # Face data (binary)
│   │   ├── face_1234567890.json   # Face metadata (human-readable)
│   │   ├── face_1234567891.pkl
│   │   └── face_1234567891.json
│   └── jane/
│       ├── face_1234567892.pkl
│       └── face_1234567892.json
```

Each face entry stores:
- Bounding box coordinates
- 5-point and 68-point landmarks
- Face embedding (512-dimensional)
- Normalized embedding
- Detected gender, age, race
- Face quality scores

## Backward Compatibility

The repository system is fully backward compatible:
- Existing `headless-run` and `batch-run` commands work unchanged
- Traditional source image face swapping still supported
- Repository is optional - only used with `repo-execute` command

## Troubleshooting

### "No source face detected"
- Ensure the source image contains a clearly visible face
- Try using a higher quality image
- Check that face is not too small or occluded

### "Person not found in repository"
- Run `repo-list` to verify person name spelling
- Run `repo-init` if repository not initialized
- Check that repository directory `~/.facefusion_repository/` exists and has proper read/write permissions
- Verify person directory exists at `~/.facefusion_repository/persons/<person_name>/`

### Poor face swap quality
- Add more face orientations to the repository
- Ensure repository faces match target video lighting/quality
- Try different face swapper models with `--face-swapper-model`

## Technical Details

### Pose Estimation Algorithm

The pose estimation uses a simplified approach based on facial landmarks:
- Assumes orthographic projection
- Estimates angles from landmark geometry
- Robust to moderate occlusion
- Fast computation (< 1ms per face)

### Performance

- Face loading: ~10ms per face (cached)
- Pose calculation: ~0.5ms per face
- Similarity comparison: ~0.1ms per pair
- Typical overhead: < 10% vs single-face swapping

### Memory Usage

- Face storage: ~50KB per face (including embeddings)
- Runtime cache: ~5MB per 100 faces
- No significant video memory increase
