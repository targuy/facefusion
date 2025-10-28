# Settings Parameters Reference

Complete reference for all FaceFusion settings parameters supported by the Settings Profile Management System.

## Parameter Categories

1. [Processors](#processors)
2. [Face Detection](#face-detection)
3. [Face Landmarker](#face-landmarker)
4. [Face Selector](#face-selector)
5. [Face Masking](#face-masking)
6. [Voice Extraction](#voice-extraction)
7. [Frame Extraction](#frame-extraction)
8. [Output Settings](#output-settings)
9. [Execution Settings](#execution-settings)

---

## Processors

Control which processing modules are active.

### `processors`

**Type**: `List[str]`

**Description**: List of active processors to apply

**Valid Values**:
- `face_swapper` - Swap faces in images/videos
- `face_enhancer` - Enhance face quality
- `face_debugger` - Debug face detection (development)
- `frame_enhancer` - Enhance overall frame quality
- `frame_colorizer` - Colorize black and white frames
- `lip_syncer` - Synchronize lip movements with audio
- `age_modifier` - Modify age appearance
- `expression_restorer` - Restore or modify facial expressions

**Example**:
```json
{
  "processors": ["face_swapper", "face_enhancer"]
}
```

---

## Face Detection

Configure how faces are detected in images and videos.

### `face_detector_model`

**Type**: `str`

**Description**: Model to use for face detection

**Valid Values**:
- `many` - Ensemble of multiple detectors
- `retinaface` - RetinaFace detector
- `scrfd` - SCRFD detector
- `yoloface` - YOLO-based face detector (recommended)
- `yunet` - YuNet detector

**Default**: `yoloface`

**Example**:
```json
{
  "face_detector_model": "yoloface"
}
```

### `face_detector_size`

**Type**: `str`

**Description**: Input size for face detector

**Valid Values**:
- `160x160` - Fastest, least accurate
- `320x320` - Fast
- `480x480` - Balanced
- `512x512` - Good
- `640x640` - Recommended balance
- `768x768` - High accuracy
- `1024x1024` - Highest accuracy, slowest

**Default**: `640x640`

**Example**:
```json
{
  "face_detector_size": "640x640"
}
```

### `face_detector_score`

**Type**: `float`

**Description**: Minimum confidence score for face detection

**Range**: `0.0` to `1.0`

**Default**: `0.5`

**Recommendations**:
- `0.3-0.4` - Accept more faces, may include false positives
- `0.5-0.6` - Balanced (recommended)
- `0.7-0.9` - Only very confident detections

**Example**:
```json
{
  "face_detector_score": 0.5
}
```

### `face_detector_angles`

**Type**: `List[int]`

**Description**: Angles to check for face detection (rotation)

**Valid Values**: List of integers from `0` to `360` (typically in 45° increments)

**Default**: `[0]`

**Example**:
```json
{
  "face_detector_angles": [0, 90, 180, 270]
}
```

---

## Face Landmarker

Configure facial landmark detection for precise face alignment.

### `face_landmarker_model`

**Type**: `str`

**Description**: Model for facial landmark detection

**Valid Values**:
- `2dfan4` - 2D FAN with 4 stacks (recommended)
- `peppa_wutz` - Alternative landmark detector

**Default**: `2dfan4`

**Example**:
```json
{
  "face_landmarker_model": "2dfan4"
}
```

### `face_landmarker_score`

**Type**: `float`

**Description**: Minimum confidence score for landmark detection

**Range**: `0.0` to `1.0`

**Default**: `0.5`

**Example**:
```json
{
  "face_landmarker_score": 0.5
}
```

---

## Face Selector

Configure which faces to process in images with multiple faces.

### `face_selector_mode`

**Type**: `str`

**Description**: How to select faces to process

**Valid Values**:
- `one` - Select one face (based on order)
- `many` - Select all detected faces
- `reference` - Select faces matching reference

**Default**: `one`

**Example**:
```json
{
  "face_selector_mode": "one"
}
```

### `face_selector_order`

**Type**: `str`

**Description**: How to order faces when selecting

**Valid Values**:
- `best-worst` - Sort by quality score
- `worst-best` - Reverse quality sort
- `left-right` - Spatial ordering (left to right)
- `right-left` - Spatial ordering (right to left)
- `small-large` - Sort by face size
- `large-small` - Reverse size sort

**Default**: `best-worst`

**Example**:
```json
{
  "face_selector_order": "best-worst"
}
```

### `face_selector_gender`

**Type**: `str` (optional)

**Description**: Filter faces by detected gender

**Valid Values**:
- `female`
- `male`

**Default**: Not set (no filter)

**Example**:
```json
{
  "face_selector_gender": "female"
}
```

### `face_selector_race`

**Type**: `str` (optional)

**Description**: Filter faces by detected race/ethnicity

**Valid Values**:
- `white`
- `black`
- `latino`
- `asian`
- `middle_eastern`
- `indian`

**Default**: Not set (no filter)

**Example**:
```json
{
  "face_selector_race": "asian"
}
```

### `face_selector_age_start`

**Type**: `int` (optional)

**Description**: Minimum age for face selection

**Range**: `0` to `100`

**Default**: Not set (no filter)

**Example**:
```json
{
  "face_selector_age_start": 25
}
```

### `face_selector_age_end`

**Type**: `int` (optional)

**Description**: Maximum age for face selection

**Range**: `0` to `100`

**Default**: Not set (no filter)

**Example**:
```json
{
  "face_selector_age_end": 45
}
```

### `reference_face_distance`

**Type**: `float` (optional)

**Description**: Maximum distance for reference face matching

**Range**: `0.0` to `1.0`

**Default**: `0.6`

**Note**: Only used when `face_selector_mode` is `reference`

**Example**:
```json
{
  "reference_face_distance": 0.6
}
```

---

## Face Masking

Configure how face regions are masked and blended.

### `face_mask_types`

**Type**: `List[str]`

**Description**: Types of masks to apply

**Valid Values**:
- `box` - Rectangular bounding box
- `occlusion` - Occlusion-aware masking
- `region` - Region-based semantic masking

**Default**: `["box"]`

**Example**:
```json
{
  "face_mask_types": ["box", "region"]
}
```

### `face_mask_regions`

**Type**: `List[str]` (optional)

**Description**: Specific facial regions to mask (used with `region` mask type)

**Valid Values**:
- `skin`
- `left-eyebrow`
- `right-eyebrow`
- `left-eye`
- `right-eye`
- `glasses`
- `nose`
- `mouth`
- `upper-lip`
- `lower-lip`

**Default**: Not set (all regions)

**Example**:
```json
{
  "face_mask_regions": ["skin", "nose", "mouth"]
}
```

### `face_mask_blur`

**Type**: `float`

**Description**: Amount of blur/feathering applied to mask edges

**Range**: `0.0` (no blur) to `1.0` (maximum blur)

**Default**: `0.3`

**Example**:
```json
{
  "face_mask_blur": 0.4
}
```

### `face_mask_padding`

**Type**: `List[int]`

**Description**: Padding around face mask [top, right, bottom, left]

**Range**: `-100` (contract) to `100` (expand) for each value

**Default**: `[0, 0, 0, 0]`

**Example**:
```json
{
  "face_mask_padding": [10, 10, 10, 10]
}
```

### `face_occluder_model`

**Type**: `str` (optional)

**Description**: Model for occlusion detection

**Valid Values**:
- `yoloface`

**Default**: Not set

**Example**:
```json
{
  "face_occluder_model": "yoloface"
}
```

### `face_parser_model`

**Type**: `str` (optional)

**Description**: Model for face parsing (segmentation)

**Valid Values**:
- `bisenet`
- `segnext`

**Default**: Not set

**Example**:
```json
{
  "face_parser_model": "bisenet"
}
```

---

## Voice Extraction

Configure voice/audio extraction settings.

### `voice_extractor_model`

**Type**: `str` (optional)

**Description**: Model for voice extraction from audio

**Valid Values**:
- `whisper`

**Default**: Not set

**Example**:
```json
{
  "voice_extractor_model": "whisper"
}
```

---

## Frame Extraction

Configure how video frames are extracted and processed.

### `trim_frame_start`

**Type**: `int` (optional)

**Description**: Start frame for video trimming

**Default**: Not set (process from beginning)

**Example**:
```json
{
  "trim_frame_start": 100
}
```

### `trim_frame_end`

**Type**: `int` (optional)

**Description**: End frame for video trimming

**Default**: Not set (process to end)

**Example**:
```json
{
  "trim_frame_end": 500
}
```

### `temp_frame_format`

**Type**: `str`

**Description**: Format for temporary extracted frames

**Valid Values**:
- `bmp` - Uncompressed, largest files
- `jpg` - Compressed, smaller files, faster (recommended)
- `png` - Lossless compression, larger files

**Default**: `jpg`

**Example**:
```json
{
  "temp_frame_format": "png"
}
```

### `keep_temp`

**Type**: `bool`

**Description**: Keep temporary files after processing

**Default**: `false`

**Example**:
```json
{
  "keep_temp": false
}
```

---

## Output Settings

Configure output quality and encoding.

### `output_image_quality`

**Type**: `int`

**Description**: Quality for output images

**Range**: `0` (lowest) to `100` (highest)

**Default**: `80`

**Recommendations**:
- `60-70` - Preview quality
- `80-90` - Standard quality
- `95-100` - Maximum quality

**Example**:
```json
{
  "output_image_quality": 95
}
```

### `output_image_scale`

**Type**: `int` (optional)

**Description**: Scale percentage for output images

**Range**: `1` to `100` (percentage)

**Default**: `100` (no scaling)

**Example**:
```json
{
  "output_image_scale": 100
}
```

### `output_video_encoder`

**Type**: `str`

**Description**: Video codec for output

**Valid Values**:
- `libx264` - H.264 (widely compatible)
- `libx265` - H.265/HEVC (better compression)
- `libvpx-vp9` - VP9 (open format)
- `h264_nvenc` - H.264 hardware encoding (NVIDIA)
- `hevc_nvenc` - H.265 hardware encoding (NVIDIA)
- `h264_amf` - H.264 hardware encoding (AMD)
- `hevc_amf` - H.265 hardware encoding (AMD)

**Default**: `libx264`

**Example**:
```json
{
  "output_video_encoder": "libx264"
}
```

### `output_video_preset`

**Type**: `str`

**Description**: Encoding speed/quality tradeoff

**Valid Values**:
- `ultrafast` - Fastest, lowest quality
- `superfast`
- `veryfast`
- `faster`
- `fast`
- `medium` - Balanced (recommended)
- `slow`
- `slower`
- `veryslow` - Slowest, highest quality

**Default**: `medium`

**Example**:
```json
{
  "output_video_preset": "slow"
}
```

### `output_video_quality`

**Type**: `int`

**Description**: Quality for output videos

**Range**: `0` (lowest) to `100` (highest)

**Default**: `80`

**Example**:
```json
{
  "output_video_quality": 90
}
```

### `output_video_scale`

**Type**: `int` (optional)

**Description**: Scale percentage for output videos

**Range**: `1` to `100`

**Default**: `100`

**Example**:
```json
{
  "output_video_scale": 100
}
```

### `output_video_fps`

**Type**: `int` (optional)

**Description**: Frame rate for output videos

**Default**: Use source video FPS

**Example**:
```json
{
  "output_video_fps": 30
}
```

### `output_audio_encoder`

**Type**: `str` (optional)

**Description**: Audio codec for output

**Valid Values**:
- `aac` - AAC codec (recommended)
- `libmp3lame` - MP3 codec
- `libopus` - Opus codec
- `libvorbis` - Vorbis codec

**Default**: Use source audio codec

**Example**:
```json
{
  "output_audio_encoder": "aac"
}
```

### `output_audio_quality`

**Type**: `int` (optional)

**Description**: Quality for output audio

**Range**: `0` to `100`

**Default**: Use source audio quality

**Example**:
```json
{
  "output_audio_quality": 90
}
```

---

## Execution Settings

Configure how processing is executed.

### `execution_providers`

**Type**: `List[str]`

**Description**: Execution providers for inference

**Valid Values**:
- `cpu` - CPU execution (universal)
- `cuda` - NVIDIA CUDA GPU
- `coreml` - Apple CoreML (Mac)
- `dml` - DirectML (Windows)
- `openvino` - Intel OpenVINO
- `tensorrt` - NVIDIA TensorRT

**Default**: `["cpu"]`

**Example**:
```json
{
  "execution_providers": ["cuda"]
}
```

### `execution_device_ids`

**Type**: `List[str]` (optional)

**Description**: Device IDs to use (for multi-GPU)

**Default**: `["0"]`

**Example**:
```json
{
  "execution_device_ids": ["0", "1"]
}
```

### `execution_thread_count`

**Type**: `int`

**Description**: Number of threads for CPU execution

**Range**: `1` to `128`

**Default**: `4`

**Recommendations**:
- Set to number of CPU cores for best performance
- Lower values reduce memory usage

**Example**:
```json
{
  "execution_thread_count": 8
}
```

### `video_memory_strategy`

**Type**: `str` (optional)

**Description**: Video memory management strategy

**Valid Values**:
- `strict` - Minimal memory usage
- `moderate` - Balanced (recommended)
- `tolerant` - Maximum performance

**Default**: `moderate`

**Example**:
```json
{
  "video_memory_strategy": "moderate"
}
```

### `system_memory_limit`

**Type**: `int` (optional)

**Description**: Maximum system memory to use (GB)

**Default**: No limit

**Example**:
```json
{
  "system_memory_limit": 16
}
```

---

## Complete Example

```json
{
  "processors": ["face_swapper", "face_enhancer"],
  "face_detector_model": "yoloface",
  "face_detector_size": "640x640",
  "face_detector_score": 0.5,
  "face_landmarker_model": "2dfan4",
  "face_landmarker_score": 0.5,
  "face_selector_mode": "one",
  "face_selector_order": "best-worst",
  "face_mask_types": ["box", "region"],
  "face_mask_regions": ["skin", "nose", "mouth"],
  "face_mask_blur": 0.3,
  "face_mask_padding": [0, 10, 0, 10],
  "temp_frame_format": "jpg",
  "keep_temp": false,
  "output_image_quality": 90,
  "output_video_encoder": "libx264",
  "output_video_preset": "slow",
  "output_video_quality": 90,
  "execution_providers": ["cuda"],
  "execution_thread_count": 8,
  "video_memory_strategy": "moderate"
}
```
