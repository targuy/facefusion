"""
Main destination analyzer coordinating all destination processing components.

Provides high-level interface for analyzing destination media (images/videos),
matching faces with repository, and creating processing queues.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from facefusion.filesystem import is_image, is_video
from facefusion.types import Face
from facefusion_repository.destination.extractor import FaceExtractor
from facefusion_repository.destination.matcher import FaceMatch, RepositoryMatcher
from facefusion_repository.destination.queue_manager import QueueManager
from facefusion_repository.destination.video_processor import VideoProcessor
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.types import QualityMetrics, QualityThresholds


class DestinationAnalysisResult:
    """Result of destination media analysis."""

    def __init__(
        self,
        source_file: str,
        total_faces_detected: int,
        total_faces_matched: int,
        matches: List[FaceMatch],
        processing_time: float = 0.0
    ):
        """
        Initialize analysis result.

        Args:
            source_file: Source media file path
            total_faces_detected: Total faces detected
            total_faces_matched: Total faces successfully matched
            matches: List of FaceMatch objects
            processing_time: Processing time in seconds
        """
        self.source_file = source_file
        self.total_faces_detected = total_faces_detected
        self.total_faces_matched = total_faces_matched
        self.matches = matches
        self.processing_time = processing_time

    def get_summary(self) -> Dict:
        """Get analysis summary."""
        match_by_face: Dict[str, int] = {}
        for match in self.matches:
            face_id = match.repository_face.id
            match_by_face[face_id] = match_by_face.get(face_id, 0) + 1

        return {
            'source_file': self.source_file,
            'total_detected': self.total_faces_detected,
            'total_matched': self.total_faces_matched,
            'match_rate': (
                self.total_faces_matched / self.total_faces_detected
                if self.total_faces_detected > 0 else 0.0
            ),
            'processing_time': self.processing_time,
            'matches_by_face': match_by_face
        }


class DestinationAnalyzer:
    """Main analyzer for destination media processing."""

    def __init__(
        self,
        repository_manager: Optional[RepositoryManager] = None,
        queue_manager: Optional[QueueManager] = None
    ):
        """
        Initialize destination analyzer.

        Args:
            repository_manager: Repository manager instance
            queue_manager: Queue manager instance
        """
        self.repository_manager = repository_manager or RepositoryManager()
        self.queue_manager = queue_manager or QueueManager()
        self.matcher = RepositoryMatcher(self.repository_manager)

    def analyze_image(
        self,
        image_path: str,
        quality_thresholds: Optional[QualityThresholds] = None,
        orientation_tolerance: int = 22,
        min_confidence: float = 0.5,
        create_queues: bool = True
    ) -> DestinationAnalysisResult:
        """
        Analyze an image file.

        Args:
            image_path: Path to image file
            quality_thresholds: Optional quality thresholds
            orientation_tolerance: Maximum orientation difference
            min_confidence: Minimum match confidence
            create_queues: Whether to create processing queues

        Returns:
            DestinationAnalysisResult object
        """
        import time
        start_time = time.time()

        # Extract faces
        faces = FaceExtractor.extract_from_image(
            image_path,
            quality_thresholds=quality_thresholds
        )

        if not faces:
            return DestinationAnalysisResult(
                source_file=image_path,
                total_faces_detected=0,
                total_faces_matched=0,
                matches=[],
                processing_time=time.time() - start_time
            )

        # Get quality metrics for each face
        from facefusion.vision import read_static_image
        vision_frame = read_static_image(image_path)
        faces_with_quality = [
            (face, FaceExtractor.get_face_quality(vision_frame, face))
            for face in faces
        ]

        # Match with repository
        matches = self.matcher.find_all_matches(
            faces_with_quality,
            orientation_tolerance=orientation_tolerance,
            min_confidence=min_confidence
        )

        # Create queues if requested
        if create_queues and matches:
            self.queue_manager.create_queues_from_matches(
                matches=matches,
                source_file=image_path
            )

        processing_time = time.time() - start_time

        return DestinationAnalysisResult(
            source_file=image_path,
            total_faces_detected=len(faces),
            total_faces_matched=len(matches),
            matches=matches,
            processing_time=processing_time
        )

    def analyze_video(
        self,
        video_path: str,
        frame_sample_rate: int = 1,
        quality_thresholds: Optional[QualityThresholds] = None,
        orientation_tolerance: int = 22,
        min_confidence: float = 0.5,
        create_queues: bool = True,
        progress_callback: Optional[callable] = None
    ) -> DestinationAnalysisResult:
        """
        Analyze a video file.

        Args:
            video_path: Path to video file
            frame_sample_rate: Process every Nth frame
            quality_thresholds: Optional quality thresholds
            orientation_tolerance: Maximum orientation difference
            min_confidence: Minimum match confidence
            create_queues: Whether to create processing queues
            progress_callback: Optional progress callback

        Returns:
            DestinationAnalysisResult object
        """
        import time
        start_time = time.time()

        # Process video frames
        frame_results = VideoProcessor.process_video_frames(
            video_path=video_path,
            frame_sample_rate=frame_sample_rate,
            quality_thresholds=quality_thresholds,
            progress_callback=progress_callback
        )

        # Collect all faces with metadata
        all_matches = []
        total_faces = 0

        for frame_number, timestamp, faces, quality_metrics in frame_results:
            total_faces += len(faces)

            # Match faces with repository
            faces_with_quality = list(zip(faces, quality_metrics))
            matches = self.matcher.find_all_matches(
                faces_with_quality,
                orientation_tolerance=orientation_tolerance,
                min_confidence=min_confidence
            )

            # Store frame metadata with matches
            for match in matches:
                all_matches.append((match, frame_number, timestamp))

        # Create queues if requested
        if create_queues and all_matches:
            matches_only = [m[0] for m in all_matches]
            frame_numbers = [m[1] for m in all_matches]
            timestamps = [m[2] for m in all_matches]

            self.queue_manager.create_queues_from_matches(
                matches=matches_only,
                source_file=video_path,
                frame_numbers=frame_numbers,
                timestamps=timestamps
            )

        processing_time = time.time() - start_time

        return DestinationAnalysisResult(
            source_file=video_path,
            total_faces_detected=total_faces,
            total_faces_matched=len(all_matches),
            matches=[m[0] for m in all_matches],
            processing_time=processing_time
        )

    def analyze_media(
        self,
        media_path: str,
        **kwargs
    ) -> Optional[DestinationAnalysisResult]:
        """
        Analyze media file (auto-detect image or video).

        Args:
            media_path: Path to media file
            **kwargs: Additional arguments passed to specific analyzer

        Returns:
            DestinationAnalysisResult or None if unsupported format
        """
        if is_image(media_path):
            return self.analyze_image(media_path, **kwargs)
        elif is_video(media_path):
            return self.analyze_video(media_path, **kwargs)
        else:
            print(f'Unsupported media format: {media_path}')
            return None
