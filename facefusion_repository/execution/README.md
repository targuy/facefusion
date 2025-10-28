# Module 5: Batch Execution Engine

## Overview

Module 5 provides the final execution system for processing face swap queues using the existing FaceFusion code. It brings together all previous modules (Repository Management, Destination Analysis, Settings Management, and Presets) into a cohesive, automated face swapping pipeline.

## Features

### Core Functionality

- **Batch Processing**: Execute face swap operations using organized queues
- **FaceFusion Integration**: Clean interface with existing FaceFusion processing pipeline
- **Settings Application**: Apply settings profiles to processing operations
- **Preset Execution**: Process using named presets for complete configurations
- **Video Reassembly**: Reconstruct processed video frames with proper sequencing
- **Progress Tracking**: Real-time monitoring with ETA calculation
- **Error Recovery**: Handle failures gracefully with retry mechanisms

### Components

#### 1. BatchExecutor (`batch_executor.py`)

Main processing coordinator that orchestrates the complete batch execution pipeline.

```python
from facefusion_repository.execution import BatchExecutor

executor = BatchExecutor()
result = executor.execute_batch()
```

**Key Features:**
- Queue-based processing
- Progress tracking with callbacks
- Pause/resume/cancel support
- Automatic cleanup

#### 2. ProgressTracker (`progress_tracker.py`)

Real-time progress monitoring with comprehensive statistics.

```python
from facefusion_repository.execution import ProgressTracker

tracker = ProgressTracker(total_items=100)
tracker.update(completed=10, failed=2)
print(tracker.get_progress_string())
# Output: "12/100 (12.0%) - Success: 10, Failed: 2 - Elapsed: 5s - ETA: 37s"
```

**Features:**
- Progress percentage calculation
- ETA estimation
- Success rate tracking
- Pause/resume support
- Detailed statistics

#### 3. ErrorHandler (`error_handler.py`)

Robust error handling with automatic retry logic.

```python
from facefusion_repository.execution import ErrorHandler

handler = ErrorHandler(max_retries=3, retry_delay=1.0)
result = handler.execute_with_retry(
    func=my_operation,
    operation_name="Face Swap"
)
```

**Features:**
- Exponential backoff retry
- Retry callbacks
- Error logging
- Fallback mechanisms
- Retryable error detection

#### 4. QueueProcessor (`queue_processor.py`)

Manages processing queues organized by source face.

```python
from facefusion_repository.execution import QueueProcessor

processor = QueueProcessor()
processor.add_to_queue(face_id='face_001', frame_face=frame)
queues = processor.organize_by_video(face_id='face_001')
```

**Features:**
- Queue organization by face ID
- Video-based grouping
- Priority ordering
- Queue persistence
- Statistics tracking

#### 5. VideoAssembler (`video_assembler.py`)

Assembles processed frames into output videos.

```python
from facefusion_repository.execution import VideoAssembler

assembler = VideoAssembler()
assembler.save_frame(frame, frame_number=1, video_id='video1')
assembler.assemble_video(
    video_id='video1',
    output_path='output.mp4',
    source_video_path='source.mp4',
    preserve_audio=True
)
```

**Features:**
- Frame storage and sequencing
- FFmpeg video assembly
- Audio preservation
- Multiple codec support
- Automatic cleanup

#### 6. ResultManager (`result_manager.py`)

Manages batch processing results and output organization.

```python
from facefusion_repository.execution import ResultManager

manager = ResultManager()
batch_dir = manager.create_batch_output_directory()
manager.save_batch_result(batch_result)
print(manager.generate_summary_report(batch_id))
```

**Features:**
- Output directory organization
- Result persistence
- Summary report generation
- Quality validation
- Batch cleanup

#### 7. FaceFusionInterface (`facefusion_interface.py`)

Clean integration layer with FaceFusion core.

```python
from facefusion_repository.execution import FaceFusionInterface

interface = FaceFusionInterface()
interface.initialize(settings=my_settings)
interface.load_source_face(face_entry)
processed_frame = interface.process_frame(target_frame)
```

**Features:**
- Settings application
- Face loading from repository
- Frame processing
- Batch optimization
- Resource cleanup

## CLI Commands

### Execute Batch

Execute all queued face swaps:

```bash
python facefusion_repo_cli.py execute-batch [--output-dir DIR] [--settings PROFILE]
```

### Execute Queue

Execute specific queue by face ID:

```bash
python facefusion_repo_cli.py execute-queue --face-id FACE_ID [--output-dir DIR]
```

### Validate Output

Validate batch processing results:

```bash
python facefusion_repo_cli.py validate-output --batch-id BATCH_ID
```

### Cleanup Temporary Files

Remove temporary processing files:

```bash
python facefusion_repo_cli.py cleanup-temp
```

## Usage Examples

### Example 1: Simple Batch Execution

```python
from facefusion_repository.execution import BatchExecutor
from facefusion_repository.repository import RepositoryManager
from facefusion_repository.execution import QueueProcessor

# Initialize components
repo_manager = RepositoryManager()
queue_processor = QueueProcessor()
executor = BatchExecutor(repo_manager, queue_processor)

# Execute batch
result = executor.execute_batch()

print(f"Processed {result.total_swaps} swaps")
print(f"Success rate: {result.successful_swaps/result.total_swaps*100:.1f}%")
```

### Example 2: With Progress Tracking

```python
from facefusion_repository.execution import BatchExecutor

executor = BatchExecutor()

def progress_callback(completed, total, status):
    print(f"\rProgress: {status}", end='', flush=True)

result = executor.execute_batch(progress_callback=progress_callback)
```

### Example 3: With Custom Settings

```python
from facefusion_repository.execution import BatchExecutor

settings = {
    'processors': ['face_swapper'],
    'face_detector_model': 'yolo_face',
    'face_detector_size': '640x640'
}

executor = BatchExecutor()
result = executor.execute_batch(settings=settings)
```

### Example 4: Error Handling

```python
from facefusion_repository.execution import ErrorHandler

handler = ErrorHandler(max_retries=5, retry_delay=2.0)

def process_frame():
    # Your processing logic
    pass

result = handler.execute_with_retry(
    process_frame,
    operation_name="Frame Processing"
)

if result is None:
    print("Processing failed after all retries")
    print(handler.get_error_summary())
```

## Architecture

### Processing Pipeline

```
1. Queue Loading
   ↓
2. Settings Application
   ↓
3. Batch Organization
   ↓
4. FaceFusion Execution (per frame)
   ↓
5. Output Collection
   ↓
6. Video Assembly
   ↓
7. Quality Validation
```

### Component Interactions

```
BatchExecutor
├── QueueProcessor (manages queues)
├── RepositoryManager (loads faces)
├── FaceFusionInterface (processes frames)
├── ErrorHandler (handles failures)
├── ProgressTracker (monitors progress)
├── VideoAssembler (creates videos)
└── ResultManager (organizes outputs)
```

## Configuration

### Default Settings

```python
# Error handling
max_retries = 3
retry_delay = 1.0  # seconds
backoff_multiplier = 2.0

# Video assembly
default_fps = 30.0
preserve_audio = True
video_codec = 'libx264'
video_quality = 23  # CRF value

# Output organization
output_dir = '~/.facefusion_repository/outputs'
temp_dir = '~/.facefusion_repository/temp'
```

### Custom Configuration

```python
from facefusion_repository.execution import (
    BatchExecutor,
    ErrorHandler,
    VideoAssembler,
    ResultManager
)

# Custom error handling
error_handler = ErrorHandler(
    max_retries=5,
    retry_delay=2.0,
    backoff_multiplier=1.5
)

# Custom output management
result_manager = ResultManager(
    output_dir='/custom/output/path'
)

# Custom video assembly
video_assembler = VideoAssembler(
    temp_dir='/custom/temp/path'
)

# Use in executor
executor = BatchExecutor()
executor.error_handler = error_handler
executor.result_manager = result_manager
executor.video_assembler = video_assembler
```

## Performance Considerations

### Optimization Tips

1. **Batch Size**: Process queues in optimal sizes to balance memory and throughput
2. **GPU Utilization**: Leverage FaceFusion's GPU acceleration for faster processing
3. **Parallel Processing**: Future enhancement for multi-GPU support
4. **Memory Streaming**: Handle large videos without loading entire frames into memory
5. **Checkpoint System**: Save progress for interrupted processing recovery

### Expected Performance

- **Frame Processing**: 1-5 seconds per frame (depending on resolution and GPU)
- **Video Assembly**: ~real-time speed with FFmpeg
- **Batch Overhead**: Minimal (<5% of total processing time)
- **Memory Usage**: ~2GB base + ~50MB per cached face

## Error Handling

### Graceful Failures

- Individual frame failures don't stop batch processing
- Automatic retry for transient errors
- Comprehensive error logging
- Partial recovery completion

### Error Types

1. **Retryable**: IOError, ConnectionError, TimeoutError, temporary failures
2. **Fatal**: Invalid face data, missing source files, out of memory
3. **Warnings**: Low quality frames, missing audio, codec issues

### Recovery Strategies

```python
# Strategy 1: Retry with exponential backoff
handler.execute_with_retry(operation, max_retries=3)

# Strategy 2: Fallback to alternative method
handler.execute_with_fallback(
    primary_func=gpu_process,
    fallback_func=cpu_process
)

# Strategy 3: Wrap with error handling
result = handler.wrap_with_error_handling(
    operation,
    error_message="Frame processing failed",
    return_on_error=None
)
```

## Testing

### Unit Tests

Located in `tests/test_execution/`:

```bash
pytest tests/test_execution/test_progress_tracker.py
pytest tests/test_execution/test_error_handler.py
pytest tests/test_execution/test_queue_processor.py
```

### Integration Tests

```python
# Test complete workflow
from facefusion_repository.execution import BatchExecutor

executor = BatchExecutor()
# ... setup queues ...
result = executor.execute_batch()

assert result.successful_swaps > 0
assert result.failed_swaps == 0
```

### Demo Script

Run the demonstration:

```bash
python examples/execution_demo.py
```

## Limitations

### Current Limitations

1. **Single-threaded**: Currently processes frames sequentially
2. **No distributed processing**: Single machine execution only
3. **Memory constraints**: Large batches may require more RAM
4. **Dependency on FaceFusion**: Requires FaceFusion installation

### Future Enhancements

- Multi-threaded frame processing
- Distributed processing support
- Advanced queue scheduling algorithms
- Real-time processing mode
- Cloud storage integration

## Integration with Other Modules

### Module 1: Face Repository

```python
from facefusion_repository.repository import RepositoryManager
from facefusion_repository.execution import BatchExecutor

repo = RepositoryManager()
executor = BatchExecutor(repository_manager=repo)
```

### Module 2: Destination Analysis

```python
# Analyze destination video and create queues
# Then execute with Module 5
executor = BatchExecutor()
result = executor.execute_batch()
```

### Module 3: Settings Management

```python
from facefusion_repository.settings import SettingsManager

settings_mgr = SettingsManager()
settings = settings_mgr.get_profile('high_quality')

executor = BatchExecutor()
result = executor.execute_batch(settings=settings)
```

### Module 4: Named Presets

```python
from facefusion_repository.presets import PresetManager

preset_mgr = PresetManager()
preset = preset_mgr.get_preset('mary_profile')

# Apply preset settings and face
executor = BatchExecutor()
# ... use preset configuration ...
```

## Contributing

When contributing to Module 5:

1. Follow existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Consider performance impact
5. Maintain backward compatibility

## License

Same as FaceFusion (OpenRAIL-AS)

## Support

For issues or questions:
- Check documentation in `facefusion_repository/`
- Review examples in `examples/`
- Report issues on GitHub

---

**Module 5 Status**: ✅ Implementation Complete  
**Last Updated**: October 28, 2025
