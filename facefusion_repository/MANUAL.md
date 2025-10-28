# FaceFusion Repository System - User Manual

## Version 1.0.0

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Basic Concepts](#basic-concepts)
4. [Repository Management](#repository-management)
5. [Working with Destination Media](#working-with-destination-media)
6. [Settings and Presets](#settings-and-presets)
7. [Batch Processing](#batch-processing)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [FAQ](#faq)

## Introduction

The FaceFusion Repository System is an advanced extension to FaceFusion that enables sophisticated face swap operations using a repository of source faces organized by orientation angles. This system allows you to:

- **Manage Multiple Source Faces**: Store and organize source faces with different orientations
- **Automatic Orientation Matching**: Automatically match destination faces with the best source face based on orientation
- **Batch Processing**: Efficiently process multiple face swaps in videos and image batches
- **Quality Control**: Automatic quality assessment ensures only high-quality faces are used
- **Named Presets**: Create reusable configurations combining specific faces with settings

### When to Use This System

Use the Repository System when:
- You need to swap faces in videos where the subject has varying head angles
- You want to maintain consistency across multiple videos or images
- You're processing large batches of media files
- You need different source faces for different orientations (profile, frontal, etc.)

## Getting Started

### Installation

The Repository System is integrated with FaceFusion and requires no additional installation beyond FaceFusion itself.

### System Requirements

- Python 3.12+
- FaceFusion core installation
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space for repository

### Initial Setup

1. **Initialize the Repository**

```bash
python facefusion.py repo-init
```

This creates the repository structure at `~/.facefusion_repository/`:
```
~/.facefusion_repository/
├── repository.json      # Repository database
├── faces/              # Stored face images
├── settings/           # Settings profiles
├── presets.json        # Named presets
└── temp/              # Temporary processing files
```

2. **Verify Installation**

```bash
python facefusion.py repo-stats
```

You should see output indicating an empty repository.

## Basic Concepts

### Face Orientation Angles

The system uses 8 standard orientation angles:
- **0°**: Frontal view
- **45°**: Slight right turn
- **90°**: Right profile
- **135°**: Three-quarter back right
- **180°**: Back view
- **225°**: Three-quarter back left
- **270°**: Left profile
- **315°**: Slight left turn

When you add a face, the system automatically detects its orientation and assigns it to the nearest standard angle.

### Quality Metrics

Each face is assessed on multiple quality dimensions:
- **Resolution**: Image dimensions (minimum 256x256)
- **Sharpness**: Clarity and focus (Laplacian variance)
- **Brightness**: Average luminance (0.2 to 0.9 ideal)
- **Contrast**: Dynamic range (standard deviation)
- **Detector Score**: Face detection confidence
- **Overall Quality**: Weighted combination of all metrics

### Repository Management

The repository stores:
- **Face Images**: Original high-quality source images
- **Metadata**: Names, tags, dates
- **Face Embeddings**: For recognition and matching
- **Quality Metrics**: For selection and filtering
- **Orientation Data**: For automatic matching

## Repository Management

### Adding Faces to the Repository

**Basic Addition**

```bash
python facefusion.py repo-add-face --source path/to/face.jpg
```

**With Name and Tags**

```bash
python facefusion.py repo-add-face \
    --source path/to/face.jpg \
    --name "Alice Frontal" \
    --tags frontal,high-quality,main
```

The system will:
1. Detect the face in the image
2. Assess the quality
3. Determine the orientation
4. Check for duplicate orientations
5. Store the face if quality is acceptable

**What Happens with Duplicates?**

If you add a face with a similar orientation to an existing one:
- The system compares quality metrics
- Keeps only the highest quality version
- Removes or rejects lower quality versions

### Listing Faces

**List All Faces**

```bash
python facefusion.py repo-list
```

**Filter by Orientation**

```bash
python facefusion.py repo-list --orientation 0
```

**Filter by Tags**

```bash
python facefusion.py repo-list --tags frontal,main
```

### Viewing Face Details

```bash
python facefusion.py repo-show --face-id face_20251028_abc123
```

Output includes:
- Face ID and name
- Orientation angle
- Quality metrics
- File path
- Tags and metadata

### Removing Faces

```bash
python facefusion.py repo-remove --face-id face_20251028_abc123
```

This permanently removes:
- The face entry from the database
- The stored image file

### Repository Statistics

```bash
python facefusion.py repo-stats
```

Shows:
- Total number of faces
- Distribution by orientation
- Average quality score
- Storage usage
- Coverage visualization

**Example Output:**

```
Face Repository Statistics
==========================

Total Faces: 5
Average Quality: 0.78
Storage Size: 12.5 MB

Orientation Coverage:
  0° ████████ 2 faces (Q: 0.85)
 45° ██████ 1 face (Q: 0.72)
 90° ████████████ 3 faces (Q: 0.92)
135° (no faces)
180° (no faces)
225° (no faces)
270° ████████ 2 faces (Q: 0.68)
315° (no faces)
```

## Working with Destination Media

### Analyzing Target Media

Before processing, analyze your target video or images to see what faces are detected and how they match with your repository.

**Analyze a Video**

```bash
python facefusion.py repo-analyze-target --target video.mp4
```

This will:
1. Extract faces from all frames
2. Determine orientation for each face
3. Show distribution of orientations
4. Identify frames with no matching source faces

**Analyze Images**

```bash
python facefusion.py repo-analyze-target --target image.jpg
```

### Matching with Repository

After analysis, match detected faces with your repository:

```bash
python facefusion.py repo-match --target video.mp4
```

**With Custom Tolerance**

```bash
python facefusion.py repo-match \
    --target video.mp4 \
    --max-angle-diff 30
```

The `--max-angle-diff` parameter (default 45°) controls how closely orientations must match.

**What Gets Created?**

The matching process creates a queue of face swap operations:
- Groups faces by matched source
- Tracks frame numbers and timestamps
- Prepares for efficient batch processing

### Viewing the Queue

```bash
python facefusion.py repo-queue-show
```

Shows:
- Number of queues (one per source face)
- Faces per queue
- Estimated processing time

### Managing the Queue

**Clear Specific Queue**

```bash
python facefusion.py repo-queue-clear --face-id face_20251028_abc123
```

**Clear All Queues**

```bash
python facefusion.py repo-queue-clear
```

## Settings and Presets

### Settings Profiles

Settings profiles store FaceFusion configuration parameters.

**Create from Current State**

```bash
python facefusion.py settings-create \
    --name high_quality \
    --from-current
```

**List Profiles**

```bash
python facefusion.py settings-list
```

**Show Profile Details**

```bash
python facefusion.py settings-show --name high_quality
```

**Apply a Profile**

```bash
python facefusion.py settings-apply --name high_quality
```

This updates the current FaceFusion state with the saved settings.

**Delete a Profile**

```bash
python facefusion.py settings-delete --name old_profile
```

### Named Presets

Presets combine a specific source face with a settings profile.

**Create a Preset**

```bash
python facefusion.py preset-create \
    --name "alice_profile" \
    --face-id face_20251028_abc123 \
    --settings high_quality \
    --description "Alice's profile view with HQ settings"
```

**List Presets**

```bash
python facefusion.py preset-list
```

**Show Preset Details**

```bash
python facefusion.py preset-show --name alice_profile
```

**Run a Preset**

```bash
python facefusion.py preset-run \
    --name alice_profile \
    --target input.mp4 \
    --output output.mp4
```

This single command:
1. Loads the specified face
2. Applies the settings profile
3. Performs the face swap
4. Saves the result

**Delete a Preset**

```bash
python facefusion.py preset-delete --name old_preset
```

## Batch Processing

### Execute Batch Queue

After matching destination media with your repository, execute the batch:

```bash
python facefusion.py batch-run --output output_directory
```

**Processing Flow:**

1. **Queue Organization**: Faces grouped by source
2. **Sequential Processing**: Each queue processed separately
3. **Frame Tracking**: Original sequence maintained
4. **Video Assembly**: Frames combined back into video
5. **Progress Updates**: Real-time progress display

**What Gets Created?**

- Processed video files with face swaps applied
- Processing log with statistics
- Error log if any failures occurred

### Monitoring Progress

During batch processing, you'll see:

```
Processing Batch Queue
======================

Queue 1/3: face_20251028_abc123 (frontal)
Progress: [████████████████████---------] 75% (150/200 frames)
ETA: 2 minutes 30 seconds

Queue 2/3: face_20251028_def456 (profile)
Status: Pending

Queue 3/3: face_20251028_ghi789 (three-quarter)
Status: Pending
```

### Batch Status

Check status of running batch:

```bash
python facefusion.py batch-status
```

Shows:
- Current queue being processed
- Overall progress
- Time remaining
- Any errors encountered

## Troubleshooting

### Common Issues

**1. "No face detected in image"**

**Causes:**
- Image quality too low
- Face too small or obscured
- Extreme angle or lighting

**Solutions:**
- Use higher resolution images
- Ensure face is clearly visible
- Try different lighting conditions
- Crop image to focus on face

**2. "Face quality below threshold"**

**Causes:**
- Blurry image
- Poor lighting
- Low resolution

**Solutions:**
- Use sharper, higher quality images
- Improve lighting
- Use higher resolution source
- Adjust quality thresholds (advanced)

**3. "No matching face found"**

**Causes:**
- Repository doesn't have faces at needed orientation
- Matching tolerance too strict

**Solutions:**
- Add more faces to repository covering different angles
- Increase `--max-angle-diff` parameter
- Check repository coverage: `python facefusion.py repo-stats`

**4. Processing is slow**

**Causes:**
- Large video files
- Many faces per frame
- Limited system resources

**Solutions:**
- Process in smaller batches
- Reduce video resolution
- Close other applications
- Use GPU acceleration if available

### Checking System Health

**Verify Repository**

```bash
python facefusion.py repo-stats
```

Look for:
- Reasonable number of faces (not too many duplicates)
- Good orientation coverage
- Acceptable quality scores

**Check Disk Space**

```bash
du -sh ~/.facefusion_repository
```

Repository can grow large with many high-resolution faces.

### Getting Help

**Verbose Output**

Add `--log-level debug` to any command for detailed output:

```bash
python facefusion.py repo-add-face \
    --source face.jpg \
    --log-level debug
```

**Error Logs**

Check logs at:
- `~/.facefusion_repository/error.log`
- Console output with debug logging

## Best Practices

### Repository Organization

**1. Use Meaningful Names**

```bash
# Good
--name "Alice Frontal View"

# Less helpful
--name "face1"
```

**2. Use Tags Consistently**

```bash
--tags person-name,orientation,quality-level

# Examples:
--tags alice,frontal,high-quality
--tags bob,profile,medium-quality
```

**3. Maintain Quality Standards**

- Use high-resolution source images (1024x1024 or better)
- Ensure good lighting
- Use sharp, in-focus images
- Avoid heavy makeup or accessories that might interfere

**4. Cover Key Orientations**

For best results, have faces at these critical angles:
- 0° (frontal) - Most important
- 45° / 315° (slight turns) - Common in conversations
- 90° / 270° (profiles) - For side views

### Batch Processing Strategy

**1. Analyze First**

Always analyze target media before processing:

```bash
python facefusion.py repo-analyze-target --target video.mp4
```

This helps identify:
- Missing orientations
- Problematic frames
- Expected processing time

**2. Build Complete Repository**

Before processing a video:
1. Analyze to see what orientations are needed
2. Add all necessary faces to repository
3. Verify coverage with `repo-stats`
4. Then proceed with matching and batch processing

**3. Process in Stages**

For large projects:
1. Process a short test clip first
2. Verify results
3. Adjust settings if needed
4. Process full video

### Performance Optimization

**1. Face Image Optimization**

- Use consistent resolution (e.g., all faces at 1024x1024)
- Pre-crop faces to reduce processing
- Use appropriate compression (PNG for quality, JPEG for size)

**2. System Resources**

- Close unnecessary applications
- Use SSD for repository storage
- Enable GPU acceleration in FaceFusion settings

**3. Batch Size Management**

- Process videos in chunks if very long
- Limit repository size to ~100-200 faces
- Clean up old/unused faces regularly

## FAQ

**Q: How many faces should I have in my repository?**

A: For most use cases, 8-24 faces is optimal (1-3 per orientation angle). More faces can slow down matching and processing.

**Q: Can I use the same repository for different people?**

A: Yes, but use tags to organize faces by person. You can filter by tags when listing or matching.

**Q: What happens if the destination face orientation doesn't match any repository face?**

A: The frame is skipped. You'll see this in the analysis output. Add faces at the needed orientations to your repository.

**Q: Can I process multiple videos with one batch?**

A: Currently, each video is analyzed and processed separately. For multiple videos, run the workflow for each one.

**Q: How do I improve face swap quality?**

A: 
1. Use higher quality source faces
2. Match orientations closely (use smaller `max-angle-diff`)
3. Use appropriate FaceFusion settings (face masks, blending, etc.)
4. Ensure good lighting match between source and destination

**Q: Can I backup my repository?**

A: Yes, simply backup the entire `~/.facefusion_repository/` directory. All data is stored there.

**Q: How do I transfer my repository to another computer?**

A: Copy the entire `~/.facefusion_repository/` directory to the same location on the new computer.

**Q: Does the system work with multiple faces in the same frame?**

A: Yes, each detected face is matched independently with the repository. However, they currently use the same source face if orientations match.

**Q: What video formats are supported?**

A: All formats supported by FaceFusion (MP4, AVI, MKV, MOV, etc.)

**Q: Can I change a face's orientation after adding it?**

A: No, orientation is detected automatically and cannot be manually changed. If incorrect, remove the face and re-add it.

**Q: How accurate is the orientation detection?**

A: The system uses FaceFusion's facial landmark detection, which is quite accurate. Orientation is mapped to the nearest 45° angle for reliability.

**Q: Can I use this system from the FaceFusion GUI?**

A: The GUI integration is planned for a future release. Currently, use the CLI commands.

## Appendix: Command Reference

### Repository Commands

| Command | Description |
|---------|-------------|
| `repo-init` | Initialize repository |
| `repo-add-face` | Add face to repository |
| `repo-list` | List faces |
| `repo-show` | Show face details |
| `repo-remove` | Remove face |
| `repo-stats` | Show statistics |

### Destination Commands

| Command | Description |
|---------|-------------|
| `repo-analyze-target` | Analyze target media |
| `repo-match` | Match with repository |
| `repo-queue-show` | Show batch queue |
| `repo-queue-clear` | Clear batch queue |

### Settings Commands

| Command | Description |
|---------|-------------|
| `settings-create` | Create settings profile |
| `settings-list` | List profiles |
| `settings-show` | Show profile details |
| `settings-apply` | Apply profile |
| `settings-delete` | Delete profile |

### Preset Commands

| Command | Description |
|---------|-------------|
| `preset-create` | Create preset |
| `preset-list` | List presets |
| `preset-show` | Show preset details |
| `preset-run` | Run preset |
| `preset-delete` | Delete preset |

### Batch Commands

| Command | Description |
|---------|-------------|
| `batch-run` | Execute batch queue |
| `batch-status` | Show batch status |

---

## Support and Resources

- **FaceFusion Documentation**: https://docs.facefusion.io
- **GitHub Repository**: https://github.com/facefusion/facefusion
- **Issue Tracker**: https://github.com/facefusion/facefusion/issues

---

**Version**: 1.0.0  
**Last Updated**: October 28, 2025  
**License**: OpenRAIL-AS (Same as FaceFusion)
