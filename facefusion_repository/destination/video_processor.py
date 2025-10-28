"""
Video processing for destination face analysis.

Handles frame-by-frame video analysis with frame sampling, progress tracking,
and metadata extraction.
"""

from typing import List, Optional, Tuple
import cv2

from facefusion.types import Face, VisionFrame
from facefusion.vision import read_video_frame
from facefusion.video_manager import get_video_capture
from facefusion_repository.destination.extractor import FaceExtractor
from facefusion_repository.types import QualityMetrics, QualityThresholds


class VideoMetadata:
    """Video metadata for frame processing and reassembly."""

    def __init__(
        self,
        video_path: str,
        total_frames: int,
        fps: float,
        width: int,
        height: int,
        duration: float
    ):
        """
        Initialize video metadata.

        Args:
            video_path: Path to video file
            total_frames: Total number of frames
            fps: Frames per second
            width: Frame width in pixels
            height: Frame height in pixels
            duration: Duration in seconds
        """
        self.video_path = video_path
        self.total_frames = total_frames
        self.fps = fps
        self.width = width
        self.height = height
        self.duration = duration


class VideoProcessor:
    """Processes videos for destination face analysis."""

    @staticmethod
    def get_video_metadata(video_path: str) -> Optional[VideoMetadata]:
        """
        Extract metadata from video file.

        Args:
            video_path: Path to video file

        Returns:
            VideoMetadata object or None if failed
        """
        try:
            video_capture = get_video_capture(video_path)

            if not video_capture.isOpened():
                return None

            total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = video_capture.get(cv2.CAP_PROP_FPS)
            width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0

            video_capture.release()

            return VideoMetadata(
                video_path=video_path,
                total_frames=total_frames,
                fps=fps,
                width=width,
                height=height,
                duration=duration
            )
        except Exception as e:
            print(f'Error getting video metadata: {e}')
            return None

    @staticmethod
    def process_video_frames(
        video_path: str,
        frame_sample_rate: int = 1,
        quality_thresholds: Optional[QualityThresholds] = None,
        progress_callback: Optional[callable] = None
    ) -> List[Tuple[int, float, List[Face], List[QualityMetrics]]]:
        """
        Process video frames and extract faces.

        Args:
            video_path: Path to video file
            frame_sample_rate: Process every Nth frame (1 = all frames)
            quality_thresholds: Optional quality thresholds
            progress_callback: Optional callback(current, total, message)

        Returns:
            List of (frame_number, timestamp, faces, quality_metrics) tuples
        """
        # Get video metadata
        metadata = VideoProcessor.get_video_metadata(video_path)
        if not metadata:
            return []

        results = []
        video_capture = get_video_capture(video_path)

        if not video_capture.isOpened():
            return []

        try:
            frame_number = 0
            processed_frames = 0

            while True:
                ret, vision_frame = video_capture.read()
                if not ret:
                    break

                # Sample frames
                if frame_number % frame_sample_rate == 0:
                    # Extract faces from frame
                    faces = FaceExtractor.extract_from_frame(
                        vision_frame,
                        quality_thresholds=quality_thresholds
                    )

                    # Get quality metrics for each face
                    quality_metrics = []
                    for face in faces:
                        quality = FaceExtractor.get_face_quality(vision_frame, face)
                        quality_metrics.append(quality)

                    # Calculate timestamp
                    timestamp = frame_number / metadata.fps if metadata.fps > 0 else 0

                    if faces:  # Only store frames with detected faces
                        results.append((frame_number, timestamp, faces, quality_metrics))

                    processed_frames += 1

                    # Progress callback
                    if progress_callback:
                        progress_callback(
                            frame_number,
                            metadata.total_frames,
                            f'Processing frame {frame_number}/{metadata.total_frames}'
                        )

                frame_number += 1

        finally:
            video_capture.release()

        return results

    @staticmethod
    def calculate_frame_timestamp(frame_number: int, fps: float) -> float:
        """
        Calculate timestamp for a frame number.

        Args:
            frame_number: Frame number
            fps: Frames per second

        Returns:
            Timestamp in seconds
        """
        if fps <= 0:
            return 0.0
        return frame_number / fps

    @staticmethod
    def get_frame_at_timestamp(
        video_path: str,
        timestamp: float
    ) -> Optional[VisionFrame]:
        """
        Get video frame at specific timestamp.

        Args:
            video_path: Path to video file
            timestamp: Timestamp in seconds

        Returns:
            VisionFrame or None
        """
        metadata = VideoProcessor.get_video_metadata(video_path)
        if not metadata:
            return None

        # Calculate frame number
        frame_number = int(timestamp * metadata.fps)

        # Read frame
        return read_video_frame(video_path, frame_number)
