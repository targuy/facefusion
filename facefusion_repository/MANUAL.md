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
python facefusion_repo_cli.py init
```

This creates the repository structure at `~/.facefusion_repository/`:
```
~/.facefusion_repository/
├── repository.json      # Repository database
├── faces/              # Stored face images
├── queues/             # Processing queues
├── settings/           # Settings profiles (future)
├── presets.json        # Named presets (future)
└── temp/              # Temporary processing files
```

2. **Verify Installation**

```bash
python facefusion_repo_cli.py stats
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
python facefusion_repo_cli.py add --source path/to/face.jpg
```

**With Name and Tags**

```bash
python facefusion_repo_cli.py add \
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
python facefusion_repo_cli.py list
```

**Filter by Orientation**

```bash
python facefusion_repo_cli.py list --orientation 0
```

**Filter by Tags**

```bash
python facefusion_repo_cli.py list --tags frontal,main
```

### Viewing Face Details

```bash
python facefusion_repo_cli.py show --face-id face_20251028_abc123
```

Output includes:
- Face ID and name
- Orientation angle
- Quality metrics
- File path
- Tags and metadata

### Removing Faces

```bash
python facefusion_repo_cli.py remove --face-id face_20251028_abc123
```

This permanently removes:
- The face entry from the database
- The stored image file

### Repository Statistics

```bash
python facefusion_repo_cli.py stats
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

Module 2 enables you to analyze destination videos and images, automatically match faces with your repository, and create organized processing queues for efficient batch operations.

### Analyzing Destination Media

The `analyze-destination` command processes destination media to detect faces, match them with repository faces, and create processing queues.

**Analyze an Image**

```bash
python facefusion_repo_cli.py analyze-destination --source image.jpg
```

**Analyze a Video**

```bash
python facefusion_repo_cli.py analyze-destination --source video.mp4
```

**With Frame Sampling for Videos**

Process every 5th frame to speed up analysis:

```bash
python facefusion_repo_cli.py analyze-destination \
    --source video.mp4 \
    --frame-sample-rate 5
```

**Analysis Without Creating Queues**

To preview matches without creating processing queues:

```bash
python facefusion_repo_cli.py analyze-destination \
    --source video.mp4 \
    --no-queues
```

**With Custom Confidence Threshold**

Only create queues for matches above 70% confidence:

```bash
python facefusion_repo_cli.py analyze-destination \
    --source video.mp4 \
    --min-confidence 0.7
```

### Understanding the Analysis Output

When you run `analyze-destination`, you'll see output like:

```
Analyzing destination media: video.mp4

  Processing frame 0/500 (0.0%)
  Processing frame 150/500 (30.0%)
  Processing frame 300/500 (60.0%)
  Processing frame 450/500 (90.0%)

Analysis Complete!
============================================================
Source File: video.mp4
Total Faces Detected: 45
Total Faces Matched: 38
Match Rate: 84.4%
Processing Time: 12.34s

Matches by Repository Face:
  face_20251028_abc123 (Alice Frontal): 25 matches
  face_20251028_def456 (Alice Profile): 13 matches

✓ Processing queues created successfully
  Use "show-queues" to view queues
```

### What the Analysis Does

1. **Face Detection**: Extracts all faces from images/video frames
2. **Quality Filtering**: Applies quality thresholds to ensure acceptable faces
3. **Orientation Analysis**: Determines the orientation angle of each face
4. **Repository Matching**: Finds the best matching repository face based on orientation
5. **Confidence Scoring**: Calculates match confidence based on orientation similarity and quality
6. **Queue Creation**: Organizes matches into processing queues by source face
7. **Metadata Storage**: Stores frame numbers, timestamps, and match information

### Viewing Processing Queues

**Show All Queues**

```bash
python facefusion_repo_cli.py show-queues
```

Output example:

```
Processing Queues:
============================================================

Queue: face_20251028_abc123
  Name: Alice Frontal
  Matches: 25
  Average Confidence: 0.87
  Created: 2025-10-28T09:20:00Z

Queue: face_20251028_def456
  Name: Alice Profile
  Matches: 13
  Average Confidence: 0.82
  Created: 2025-10-28T09:20:00Z

Summary:
------------------------------------------------------------
Total Queues: 2
Total Faces: 38
```

### Queue Statistics

Get detailed statistics about processing queues:

```bash
python facefusion_repo_cli.py queue-stats
```

Output includes:
- Total number of queues
- Total faces across all queues
- Breakdown of faces per queue
- Repository face names and IDs

```
Queue Statistics:
============================================================

Total Queues: 2
Total Faces: 38

Faces per Queue:
  face_20251028_abc123 (Alice Frontal): 25 faces
  face_20251028_def456 (Alice Profile): 13 faces
```

### Exporting Queue Data

Export a specific queue to a JSON file for external processing or backup:

```bash
python facefusion_repo_cli.py export-queue \
    --face-id face_20251028_abc123 \
    --output queue_backup.json
```

The exported JSON contains:
- Source face ID and name
- Match count and average confidence
- Detailed match information (frame numbers, timestamps, confidence scores)
- Source file paths

### Managing Queues

**Clear a Specific Queue**

Remove a single processing queue:

```bash
python facefusion_repo_cli.py clear-queues --face-id face_20251028_abc123
```

**Clear All Queues**

Remove all processing queues:

```bash
python facefusion_repo_cli.py clear-queues
```

### Advanced Analysis Options

**Video Processing with Frame Sampling**

For long videos, use frame sampling to reduce processing time:

```bash
# Process every 10th frame
python facefusion_repo_cli.py analyze-destination \
    --source long_video.mp4 \
    --frame-sample-rate 10
```

Frame sampling is useful for:
- Preview analysis before full processing
- Long videos where processing time is critical
- Videos with relatively static faces

**Adjusting Match Confidence**

The default minimum confidence is 0.5 (50%). Adjust based on your needs:

```bash
# Strict matching (fewer false positives)
python facefusion_repo_cli.py analyze-destination \
    --source video.mp4 \
    --min-confidence 0.8

# Lenient matching (more matches, but lower quality)
python facefusion_repo_cli.py analyze-destination \
    --source video.mp4 \
    --min-confidence 0.3
```

### Workflow Example

Complete workflow for processing a destination video:

```bash
# 1. Initialize repository
python facefusion_repo_cli.py init

# 2. Add source faces at different orientations
python facefusion_repo_cli.py add \
    --source alice_frontal.jpg \
    --name "Alice Frontal"

python facefusion_repo_cli.py add \
    --source alice_profile.jpg \
    --name "Alice Profile"

# 3. Verify repository
python facefusion_repo_cli.py stats

# 4. Analyze destination video
python facefusion_repo_cli.py analyze-destination \
    --source destination_video.mp4 \
    --frame-sample-rate 2

# 5. Review processing queues
python facefusion_repo_cli.py show-queues

# 6. Check detailed statistics
python facefusion_repo_cli.py queue-stats

# 7. Export queue if needed
python facefusion_repo_cli.py export-queue \
    --face-id face_20251028_abc123 \
    --output queue_backup.json
```

### Performance Considerations

**Frame Sampling Guidelines**

- **Sample Rate 1** (every frame): Maximum accuracy, slowest
- **Sample Rate 2-5**: Good balance for most videos
- **Sample Rate 10+**: Fast preview, may miss faces in fast-moving scenes

**Video Processing Tips**

1. Use frame sampling for initial analysis
2. Analyze a short clip first to verify matches
3. Process full video with sample rate 1 for production use
4. Monitor system resources during analysis

**Quality Thresholds**

The system uses default quality thresholds from Module 1:
- Minimum resolution: 256x256
- Minimum sharpness: 0.3
- Minimum detector score: 0.5
- Minimum overall quality: 0.4

These thresholds ensure only acceptable-quality faces are processed.

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
- Increase orientation tolerance (default is 22 degrees)
- Check repository coverage: `python facefusion_repo_cli.py stats`

**4. Processing is slow**

**Causes:**
- Large video files
- Many faces per frame
- Limited system resources
- Frame sample rate set to 1 (processing every frame)

**Solutions:**
- Process in smaller batches
- Reduce video resolution
- Use frame sampling: `--frame-sample-rate 5`
- Close other applications
- Use GPU acceleration if available

**5. "Low match rate" (few faces matched)**

**Causes:**
- Insufficient repository coverage
- Quality thresholds too strict
- Confidence threshold too high

**Solutions:**
- Add more faces at different orientations to repository
- Lower confidence threshold: `--min-confidence 0.3`
- Check which orientations are missing: `python facefusion_repo_cli.py stats`
- Verify destination media quality

**6. "Analysis takes too long for videos"**

**Causes:**
- Processing every frame (sample rate = 1)
- Very long video
- Complex scenes with many faces

**Solutions:**
- Use frame sampling: `--frame-sample-rate 5` or higher
- Analyze a short clip first to test parameters
- Split long videos into smaller segments
- Process preview with `--no-queues` flag first

**7. "Queues not being created"**

**Causes:**
- No matches found (all faces filtered out)
- Confidence threshold too high
- Repository is empty

**Solutions:**
- Verify repository has faces: `python facefusion_repo_cli.py list`
- Lower confidence threshold
- Check analysis output for match statistics
- Review quality of destination media

### Module 2 Specific Issues

**Video Frame Processing Errors**

If you encounter errors during video processing:

```bash
# Test with frame sampling first
python facefusion_repo_cli.py analyze-destination \
    --source video.mp4 \
    --frame-sample-rate 10 \
    --no-queues
```

**Queue Persistence Issues**

If queues aren't saving or loading:

```bash
# Check queue directory exists
ls ~/.facefusion_repository/queues/

# Verify queue file
cat ~/.facefusion_repository/queues/processing_queues.json
```

**Match Confidence Too Low**

If all matches have low confidence:

1. Check orientation coverage in repository
2. Verify face quality in both repository and destination
3. Consider adding more repository faces at needed angles

```bash
# See what orientations are needed
python facefusion_repo_cli.py analyze-destination \
    --source video.mp4 \
    --no-queues

# Check repository coverage
python facefusion_repo_cli.py stats
```

### Checking System Health

**Verify Repository**

```bash
python facefusion_repo_cli.py stats
```

Look for:
- Reasonable number of faces (not too many duplicates)
- Good orientation coverage
- Acceptable quality scores

**Check Processing Queues**

```bash
python facefusion_repo_cli.py show-queues
```

Verify:
- Queues have been created
- Match counts are reasonable
- Average confidence is acceptable (>0.5)

**Check Disk Space**

```bash
du -sh ~/.facefusion_repository
```

Repository can grow large with many high-resolution faces and processing queues.

### Debugging Analysis Issues

**Enable Verbose Output**

Add print statements in the code or check for errors:

```bash
# Run with Python directly to see detailed errors
python facefusion_repo_cli.py analyze-destination --source video.mp4
```

**Test with Simple Image First**

Before processing videos, test with a simple image:

```bash
# Test image analysis
python facefusion_repo_cli.py analyze-destination \
    --source test_image.jpg
```

**Verify Face Detection Works**

Ensure FaceFusion's face detection is working:

```bash
# Initialize state manager
python facefusion_repo_cli.py list
```

### Performance Optimization

**For Large Videos:**

1. Use aggressive frame sampling for preview: `--frame-sample-rate 20`
2. Analyze a short segment first
3. Once parameters are tuned, process full video with lower sampling rate

**For Many Faces:**

1. Increase confidence threshold to filter weak matches
2. Ensure repository has only necessary orientations
3. Use quality filtering to skip poor faces

**Memory Management:**

- Process videos in segments if memory errors occur
- Clear old queues regularly: `python facefusion_repo_cli.py clear-queues`
- Monitor system resources during processing

### Getting Help

**Error Logs**

Check logs at:
- Console output during analysis
- Python stack traces for detailed error information

**Diagnostic Information**

When reporting issues, include:
- Repository statistics (`stats` command output)
- Queue statistics (`queue-stats` output)
- Analysis output with error messages
- Video/image properties (resolution, duration, format)

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

Always analyze destination media before processing:

```bash
python facefusion_repo_cli.py analyze-destination --source video.mp4
```

This helps identify:
- Missing orientations in repository
- Match rate and confidence
- Expected processing coverage

**2. Build Complete Repository**

Before processing a video:
1. Analyze to see what orientations are detected
2. Add necessary faces to repository for those orientations
3. Verify coverage with `stats` command
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
