# FaceFusion Repository System

A person-centric face management system for organizing and using faces in FaceFusion.

## Overview

The FaceFusion Repository system provides a structured way to organize and manage faces for use in face swapping operations. Instead of manually specifying source images each time, you can build a repository of persons with their associated face images and reference them by name.

## Features

- **Person-centric organization**: Group multiple face images under person names
- **Face quality tracking**: Each face is stored with quality scores for selection
- **Embedding storage**: Pre-computed face embeddings for efficient processing
- **Simple CLI**: Easy-to-use commands for repository management
- **Integration with FaceFusion**: Seamless integration with existing face swapping pipeline

## Installation

The repository system is included with FaceFusion. No additional installation required.

## Quick Start

### 1. Initialize a Repository

```bash
python facefusion.py repo-init
```

This creates a `.facefusion_repository` directory in your current location.

### 2. Add Faces to the Repository

```bash
python facefusion.py repo-add --person "John" -s path/to/john_face.jpg
python facefusion.py repo-add --person "Jane" -s path/to/jane_face.jpg
```

You can add multiple faces for the same person:

```bash
python facefusion.py repo-add --person "John" -s path/to/john_face2.jpg
python facefusion.py repo-add --person "John" -s path/to/john_face3.jpg
```

### 3. List Repository Contents

```bash
python facefusion.py repo-list
```

Example output:
```
Repository contains 2 person(s):

  • John: 3 face(s)
    [1] Quality: 0.95 - faces/John/john_face.jpg
    [2] Quality: 0.92 - faces/John/john_face2.jpg
    [3] Quality: 0.89 - faces/John/john_face3.jpg
  • Jane: 1 face(s)
    [1] Quality: 0.97 - faces/Jane/jane_face.jpg
```

### 4. Execute Face Swapping

```bash
python facefusion.py repo-execute --person "John" -t target_video.mp4 -o output_video.mp4
```

This uses all of John's faces from the repository as source for the face swap operation.

## CLI Commands

### repo-init

Initialize a new face repository.

```bash
python facefusion.py repo-init [--repository-path PATH]
```

**Options:**
- `--repository-path`: Path to the repository directory (default: `.facefusion_repository`)

### repo-add

Add a face to the repository for a person.

```bash
python facefusion.py repo-add --person NAME -s SOURCE_IMAGE [--repository-path PATH]
```

**Required Options:**
- `--person`: Name of the person
- `-s, --source-paths`: Path to the face image

**Optional:**
- `--repository-path`: Path to the repository directory (default: `.facefusion_repository`)

### repo-list

List all persons and their faces in the repository.

```bash
python facefusion.py repo-list [--repository-path PATH]
```

**Options:**
- `--repository-path`: Path to the repository directory (default: `.facefusion_repository`)

### repo-execute

Execute face swapping using repository faces.

```bash
python facefusion.py repo-execute --person NAME -t TARGET -o OUTPUT [OPTIONS]
```

**Required Options:**
- `--person`: Name of the person whose faces to use
- `-t, --target-path`: Path to target image or video
- `-o, --output-path`: Path for output file

**Optional:**
- `--repository-path`: Path to the repository directory (default: `.facefusion_repository`)
- All standard FaceFusion options (processors, execution providers, etc.)

## Repository Structure

```
.facefusion_repository/
├── repository.json          # Repository metadata and index
└── faces/                   # Face image storage
    ├── John/
    │   ├── john_face.jpg
    │   ├── john_face2.jpg
    │   └── john_face3.jpg
    └── Jane/
        └── jane_face.jpg
```

## Data Model

The repository stores:
- **Person metadata**: Name, creation/update dates
- **Face data**: Image path, embedding vector, quality score, addition date
- **Version information**: For future compatibility

## Integration with FaceFusion

The `repo-execute` command:
1. Loads all faces for the specified person from the repository
2. Passes them as source images to FaceFusion's existing processing pipeline
3. Uses the standard `conditional_process()` function for face swapping
4. Supports all standard FaceFusion options (GPU acceleration, processors, etc.)

## Best Practices

1. **Use high-quality face images**: Clear, well-lit, frontal face photos work best
2. **Multiple angles**: Add faces from different angles for better results
3. **Quality over quantity**: A few high-quality faces are better than many poor ones
4. **Person naming**: Use consistent, descriptive names for persons
5. **Organization**: Keep repository in project root for easy access

## Troubleshooting

**"No face detected in image"**
- Ensure the image contains a clear, visible face
- Try a different image with better lighting or angle

**"Person not found in repository"**
- Check the person name spelling
- Use `repo-list` to see available persons

**"Repository does not exist"**
- Run `repo-init` first to create the repository
- Check that you're in the correct directory

## Technical Details

- **Storage format**: JSON for metadata, filesystem for images
- **Embeddings**: 128-dimensional vectors from FaceFusion's face analyzer
- **Quality scores**: Based on face detector confidence scores
- **Thread-safe**: Operations are atomic for concurrent access

## Future Enhancements

Planned features for future versions:
- GUI integration with drag-drop interface
- Face preview before adding to repository
- Batch import from directories
- Face quality filtering and auto-selection
- Export/import repository archives
