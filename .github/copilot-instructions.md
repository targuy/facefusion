# FaceFusion AI Coding Agent Instructions

## Project Architecture Overview

FaceFusion is an industry-leading face manipulation platform with a modular architecture comprising:

- **Core System**: State-managed processing pipeline with CLI/GUI interfaces
- **Processors**: Pluggable face manipulation modules (swapping, enhancement, etc.)
- **Jobs System**: Async task management with status tracking
- **Repository**: Person-based face library with quality assessment and pose-aware selection
- **Inference Engine**: ONNX-based ML model execution with memory management

### Key Entry Points
- `facefusion.py` → `facefusion/core.py#cli()` - Main CLI entry
- `facefusion/uis/core.py` - Gradio-based web interface
- `facefusion_repository/manager.py` - Face repository operations

## Critical Patterns & Conventions

### State Management Pattern
All application state flows through `facefusion/state_manager.py` with separate CLI/UI states:
```python
# Always use state_manager for configuration
state_manager.set_item('face_selector_mode', 'best-quality')
value = state_manager.get_item('face_detector_model')
```

### Processor Module Pattern
All processors in `facefusion/processors/modules/` must implement these methods:
```python
PROCESSORS_METHODS = [
    'get_inference_pool', 'clear_inference_pool', 'register_args', 
    'apply_args', 'pre_check', 'pre_process', 'post_process', 'process_frame'
]
```

### Error Handling Convention
Use `facefusion/exit_helper.py` for graceful termination:
```python
from facefusion.exit_helper import hard_exit
if not validation_result:
    hard_exit(2)  # Use specific exit codes
```

### Configuration System
Uses INI-based config in `facefusion.ini` accessed via `facefusion/config.py`:
```python
# Config follows section/option pattern
face_detector_model = get_str_value('face_detector', 'face_detector_model', 'yoloface')
```

## Repository System Architecture

### Face Storage & Organization
- JSON-based metadata in `.face_repository/persons.json`
- Images organized as `.face_repository/faces/{person_id}/{uuid}.{ext}`
- Quality assessment using multi-metric scoring (sharpness, brightness, contrast, resolution)

### Quality Assessment Integration
When adding faces, always consider quality filtering:
```python
# CLI pattern
python facefusion.py repo-add --person "Name" --face-paths *.jpg --quality-threshold 0.7

# API pattern  
manager.create_person("Name", face_paths, quality_threshold=0.7)
```

## Development Workflows

### Testing Convention
- Unit tests in `tests/` use pytest with fixture-based setup
- Test files follow `test_{module}.py` naming
- Use `tests/helper.py` for common test utilities
- Integration tests use subprocess calls to `facefusion.py`

### Adding New Processors
1. Create module in `facefusion/processors/modules/{name}.py`
2. Implement all required methods from `PROCESSORS_METHODS`
3. Add to `facefusion/processors/choices.py`
4. Create corresponding test file `tests/test_cli_{name}.py`

### Memory Management Pattern
Critical for ML inference - always use memory limits:
```python
from facefusion.memory import limit_system_memory
limit_system_memory()  # Call before heavy operations
```

## Job System Integration

### Job Lifecycle
Jobs progress through states: `drafted` → `queued` → `processing` → `completed/failed`
- Create with `job_manager.create_job(job_id)`
- Add steps with `job_manager.add_step(job_id, step)`
- Execute with `job_runner.run_job(job_id)`

### CLI Job Commands
```bash
# Job management workflow
python facefusion.py job-create --job-id "task1"
python facefusion.py job-add-step --job-id "task1" --step-name "process"
python facefusion.py job-submit --job-id "task1"
python facefusion.py job-run --job-id "task1"
```

## Key Integration Points

### FFMPEG Operations
All video/audio processing uses `facefusion/ffmpeg.py` wrapper:
- `extract_frames()` for video → frames
- `merge_video()` for frames → video  
- `replace_audio()` for audio handling

### Vision Processing
Core computer vision in `facefusion/vision.py`:
- Use `read_static_image()` for single images
- Use `read_static_images()` for batch processing
- Always call `restrict_image_resolution()` before processing

### Face Analysis Pipeline
1. `face_detector.py` - Detect face bounding boxes
2. `face_landmarker.py` - Extract 68-point landmarks  
3. `face_recognizer.py` - Generate embeddings
4. Processor modules - Apply transformations

## Repository-Specific Development

### Face Selection Logic
Repository selector uses fallback chains:
```python
# Primary → fallback → default selection
selector = RepositorySelector()
faces = selector.select_faces(
    person="Primary", 
    fallback_persons=["Backup1", "Backup2"],
    selection_mode="best-quality"
)
```

### Pose-Aware Selection
3D pose calculation for intelligent face matching:
```python
from facefusion_repository.pose_calculator import calculate_pose_from_landmarks
pose = calculate_pose_from_landmarks(landmarks_68)  # Returns (pitch, yaw, roll)
```

## Common Debugging Patterns

### CLI Testing
Always test CLI commands with proper job paths:
```bash
python facefusion.py headless-run --jobs-path /tmp/test-jobs --processors face_swapper
```

### State Debugging
Check state inconsistencies:
```python
print(f"Current state: {state_manager.get_state()}")
state_manager.sync_state()  # Sync CLI ↔ UI states
```

### Memory Issues
Monitor inference pools:
```python
processor_module.clear_inference_pool()  # Clear ONNX sessions
```

This codebase emphasizes modularity, state management, and graceful error handling. Always consider memory constraints when working with ML models, and use the established patterns for configuration, state management, and processor integration.