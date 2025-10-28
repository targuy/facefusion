"""
Batch executor for coordinating face swap operations.
"""

import hashlib
import os
import time
from typing import Any, Callable, Dict, List, Optional

from facefusion import ffmpeg, state_manager, video_manager
from facefusion.vision import read_static_video_frame
from facefusion_repository.execution.error_handler import ErrorHandler
from facefusion_repository.execution.facefusion_interface import FaceFusionInterface
from facefusion_repository.execution.progress_tracker import ProgressTracker
from facefusion_repository.execution.queue_processor import QueueProcessor
from facefusion_repository.execution.result_manager import ResultManager
from facefusion_repository.execution.video_assembler import VideoAssembler
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.types import BatchResult, QueueResult


class BatchExecutor:
    """
    Main batch execution coordinator.

    Orchestrates the complete batch processing pipeline including queue
    processing, face swapping, video assembly, and result management.
    """

    def __init__(
        self,
        repository_manager: Optional[RepositoryManager] = None,
        queue_processor: Optional[QueueProcessor] = None,
        output_dir: Optional[str] = None
    ) -> None:
        """
        Initialize batch executor.

        Args:
            repository_manager: Repository manager instance
            queue_processor: Queue processor instance
            output_dir: Output directory path
        """
        self.repository_manager = repository_manager or RepositoryManager()
        self.queue_processor = queue_processor or QueueProcessor()
        self.result_manager = ResultManager(output_dir)
        self.video_assembler = VideoAssembler()
        self.error_handler = ErrorHandler()
        self.facefusion_interface = FaceFusionInterface()

        self._is_paused = False
        self._is_cancelled = False

    def execute_batch(
        self,
        settings: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> BatchResult:
        """
        Execute all queued face swaps.

        Args:
            settings: Optional FaceFusion settings to apply
            progress_callback: Optional callback for progress updates

        Returns:
            BatchResult with processing statistics
        """
        start_time = time.time()

        # Initialize FaceFusion interface
        if not self.facefusion_interface.initialize(settings):
            print('Failed to initialize FaceFusion interface')
            return self._create_empty_batch_result(start_time)

        # Get all queues
        all_queues = self.queue_processor.get_all_queues()

        if not all_queues:
            print('No queues to process')
            return self._create_empty_batch_result(start_time)

        # Create batch output directory
        batch_id = self.result_manager.create_batch_output_directory()

        # Initialize progress tracking
        total_items = self.queue_processor.get_total_items()
        progress_tracker = ProgressTracker(total_items)

        # Process each queue
        queue_results: List[QueueResult] = []
        successful_queues = 0
        failed_queues = 0

        for face_id in self.queue_processor.get_queue_priority_order():
            if self._is_cancelled:
                print('Batch execution cancelled')
                break

            # Wait if paused
            while self._is_paused and not self._is_cancelled:
                progress_tracker.pause()
                time.sleep(0.5)

            if progress_tracker.is_paused():
                progress_tracker.resume()

            # Process queue
            queue_result = self.execute_queue(
                face_id,
                batch_id,
                progress_tracker,
                progress_callback
            )

            queue_results.append(queue_result)

            if queue_result.failed_swaps < queue_result.total_swaps:
                successful_queues += 1
            else:
                failed_queues += 1

        # Cleanup
        self.facefusion_interface.cleanup()

        # Create batch result
        total_time = time.time() - start_time
        total_swaps = sum(qr.total_swaps for qr in queue_results)
        successful_swaps = sum(qr.successful_swaps for qr in queue_results)
        failed_swaps = sum(qr.failed_swaps for qr in queue_results)

        batch_result = BatchResult(
            total_queues=len(all_queues),
            successful_queues=successful_queues,
            failed_queues=failed_queues,
            total_swaps=total_swaps,
            successful_swaps=successful_swaps,
            failed_swaps=failed_swaps,
            total_time=total_time,
            queue_results=queue_results
        )

        # Save result
        self.result_manager.save_batch_result(batch_result, batch_id)

        # Print summary
        print(f'\nBatch execution complete!')
        print(self.result_manager.generate_summary_report(batch_id))

        return batch_result

    def execute_queue(
        self,
        face_id: str,
        batch_id: str,
        progress_tracker: Optional[ProgressTracker] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> QueueResult:
        """
        Execute face swaps for a specific queue.

        Args:
            face_id: Source face ID
            batch_id: Batch identifier for output
            progress_tracker: Optional progress tracker
            progress_callback: Optional callback for progress updates

        Returns:
            QueueResult with processing statistics
        """
        start_time = time.time()

        # Get face from repository
        face_entry = self.repository_manager.get_face(face_id)
        if face_entry is None:
            error_msg = f'Face not found in repository: {face_id}'
            self.error_handler.log_error(error_msg)
            return QueueResult(
                face_id=face_id,
                total_swaps=0,
                successful_swaps=0,
                failed_swaps=0,
                processing_time=0.0,
                errors=[error_msg]
            )

        # Load source face
        if not self.facefusion_interface.load_source_face(face_entry):
            error_msg = f'Failed to load source face: {face_id}'
            self.error_handler.log_error(error_msg)
            return QueueResult(
                face_id=face_id,
                total_swaps=0,
                successful_swaps=0,
                failed_swaps=0,
                processing_time=0.0,
                errors=[error_msg]
            )

        # Get queue
        queue = self.queue_processor.get_queue(face_id)
        if not queue:
            return QueueResult(
                face_id=face_id,
                total_swaps=0,
                successful_swaps=0,
                failed_swaps=0,
                processing_time=0.0,
                errors=[]
            )

        # Organize by video
        videos_to_process = self.queue_processor.organize_by_video(face_id)

        # Process each video
        successful_swaps = 0
        failed_swaps = 0

        for video_path, frame_faces in videos_to_process.items():
            result = self._process_video_queue(
                video_path,
                frame_faces,
                batch_id,
                progress_tracker,
                progress_callback
            )

            successful_swaps += result['successful']
            failed_swaps += result['failed']

        processing_time = time.time() - start_time

        return QueueResult(
            face_id=face_id,
            total_swaps=len(queue),
            successful_swaps=successful_swaps,
            failed_swaps=failed_swaps,
            processing_time=processing_time,
            errors=self.error_handler.get_errors()
        )

    def _process_video_queue(
        self,
        video_path: str,
        frame_faces: List,
        batch_id: str,
        progress_tracker: Optional[ProgressTracker] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, int]:
        """
        Process all frames for a video.

        Args:
            video_path: Path to source video
            frame_faces: List of FrameFace objects for this video
            batch_id: Batch identifier
            progress_tracker: Optional progress tracker
            progress_callback: Optional progress callback

        Returns:
            Dictionary with 'successful' and 'failed' counts
        """
        successful = 0
        failed = 0

        # Generate video ID
        video_id = self._generate_video_id(video_path)

        # Get video metadata
        fps = video_manager.detect_video_fps(video_path) or 30.0

        # Process each frame
        for frame_face in frame_faces:
            if self._is_cancelled:
                break

            # Read frame
            frame = read_static_video_frame(video_path, frame_face.frame_number)
            if frame is None:
                failed += 1
                if progress_tracker:
                    progress_tracker.update(0, 1)
                continue

            # Process frame with retry
            def process_frame_func():
                return self.facefusion_interface.process_frame(frame)

            processed_frame = self.error_handler.execute_with_retry(
                process_frame_func,
                operation_name=f'Process frame {frame_face.frame_number}'
            )

            if processed_frame is not None:
                # Save processed frame
                frame_path = self.video_assembler.save_frame(
                    processed_frame,
                    frame_face.frame_number,
                    video_id
                )

                if frame_path:
                    successful += 1
                else:
                    failed += 1
            else:
                failed += 1

            # Update progress
            if progress_tracker:
                if processed_frame is not None:
                    progress_tracker.update(1, 0)
                else:
                    progress_tracker.update(0, 1)

            if progress_callback:
                total = progress_tracker.total_items if progress_tracker else len(frame_faces)
                completed = progress_tracker.completed_items if progress_tracker else successful
                status = progress_tracker.get_progress_string() if progress_tracker else ''
                progress_callback(completed, total, status)

        # Assemble video if any frames were processed successfully
        if successful > 0:
            output_filename = os.path.basename(video_path)
            output_path = self.result_manager.get_output_path(output_filename, batch_id)

            if self.video_assembler.assemble_video(
                video_id,
                output_path,
                source_video_path=video_path,
                fps=fps,
                preserve_audio=True
            ):
                print(f'✓ Video assembled: {output_path}')
            else:
                print(f'✗ Failed to assemble video: {output_path}')

            # Cleanup temporary frames
            self.video_assembler.cleanup_frames(video_id)

        return {'successful': successful, 'failed': failed}

    def _generate_video_id(self, video_path: str) -> str:
        """
        Generate unique ID for a video.

        Args:
            video_path: Path to video file

        Returns:
            Unique video identifier
        """
        # Use hash of video path as ID
        return hashlib.md5(video_path.encode()).hexdigest()[:16]

    def _create_empty_batch_result(self, start_time: float) -> BatchResult:
        """
        Create empty batch result for failed initialization.

        Args:
            start_time: Batch start time

        Returns:
            Empty BatchResult
        """
        return BatchResult(
            total_queues=0,
            successful_queues=0,
            failed_queues=0,
            total_swaps=0,
            successful_swaps=0,
            failed_swaps=0,
            total_time=time.time() - start_time,
            queue_results=[]
        )

    def pause(self) -> None:
        """Pause batch execution."""
        self._is_paused = True

    def resume(self) -> None:
        """Resume batch execution."""
        self._is_paused = False

    def cancel(self) -> None:
        """Cancel batch execution."""
        self._is_cancelled = True

    def is_paused(self) -> bool:
        """Check if execution is paused."""
        return self._is_paused

    def is_cancelled(self) -> bool:
        """Check if execution is cancelled."""
        return self._is_cancelled

    def cleanup_temp_files(self) -> bool:
        """
        Clean up all temporary files.

        Returns:
            True if cleanup successful
        """
        return self.video_assembler.cleanup_all()
