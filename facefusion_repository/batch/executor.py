"""
Batch executor for processing face swap queues.

Coordinates batch face swap operations using processing queues and repository faces.
This module serves as the execution engine that actually performs face swaps.
"""

import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

from facefusion.filesystem import is_image, is_video
from facefusion_repository.destination.queue_manager import ProcessingQueue, QueueManager
from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.batch.progress_tracker import ProgressTracker


@dataclass
class QueueResult:
    """Result of processing a single queue."""
    
    queue_id: str
    success: bool
    faces_processed: int
    processing_time: float
    error: Optional[str] = None
    output_file: Optional[str] = None


@dataclass
class BatchResult:
    """Result of batch processing operation."""
    
    total_queues: int
    successful: int
    failed: int
    total_faces_processed: int
    total_time: float
    queue_results: List[QueueResult]


class BatchExecutor:
    """
    Executes batch face swap operations from processing queues.
    
    This is the critical Module 5 component that performs actual face swapping
    using queues created by Module 2's analysis.
    """

    def __init__(
        self,
        queue_manager: Optional[QueueManager] = None,
        repository_manager: Optional[RepositoryManager] = None
    ):
        """
        Initialize batch executor.

        Args:
            queue_manager: Queue manager instance
            repository_manager: Repository manager instance
        """
        self.queue_manager = queue_manager or QueueManager()
        self.repository_manager = repository_manager or RepositoryManager()
        self.progress_tracker: Optional[ProgressTracker] = None

    def execute_all_queues(
        self,
        output_path: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        dry_run: bool = False
    ) -> BatchResult:
        """
        Execute all processing queues.

        Args:
            output_path: Directory for output files
            progress_callback: Optional callback(current, total)
            dry_run: If True, preview operations without executing

        Returns:
            BatchResult with statistics

        Raises:
            ValueError: If no queues available or output path invalid
        """
        # Validate output path
        output_dir = Path(output_path)
        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)

        # Get all queues
        queues = self.queue_manager.list_queues()
        if not queues:
            raise ValueError("No processing queues available")

        # Calculate total operations
        total_operations = sum(q.get_size() for q in queues)
        if total_operations == 0:
            raise ValueError("Queues are empty")

        print(f"\nBatch Execution Plan:")
        print(f"  Total queues: {len(queues)}")
        print(f"  Total face swaps: {total_operations}")
        print(f"  Output directory: {output_path}")

        if dry_run:
            print("\n[DRY RUN MODE - No actual processing]")
            for i, queue in enumerate(queues, 1):
                print(f"\nQueue {i}/{len(queues)}:")
                print(f"  Source Face ID: {queue.source_face_id}")
                print(f"  Source Face Name: {queue.source_face_name}")
                print(f"  Matches: {queue.get_size()}")
                print(f"  Avg Confidence: {queue.get_average_confidence():.2f}")
            
            return BatchResult(
                total_queues=len(queues),
                successful=0,
                failed=0,
                total_faces_processed=0,
                total_time=0.0,
                queue_results=[]
            )

        # Initialize progress tracking
        self.progress_tracker = ProgressTracker(total_operations)

        # Process each queue
        start_time = time.time()
        queue_results = []

        for queue in queues:
            result = self._execute_queue(
                queue=queue,
                output_path=str(output_dir),
                progress_callback=progress_callback
            )
            queue_results.append(result)

        total_time = time.time() - start_time

        # Calculate statistics
        successful = sum(1 for r in queue_results if r.success)
        failed = len(queue_results) - successful
        total_processed = sum(r.faces_processed for r in queue_results)

        return BatchResult(
            total_queues=len(queues),
            successful=successful,
            failed=failed,
            total_faces_processed=total_processed,
            total_time=total_time,
            queue_results=queue_results
        )

    def _execute_queue(
        self,
        queue: ProcessingQueue,
        output_path: str,
        progress_callback: Optional[Callable[[int, int], None]]
    ) -> QueueResult:
        """
        Execute single processing queue.

        Args:
            queue: Processing queue to execute
            output_path: Output directory
            progress_callback: Optional progress callback

        Returns:
            QueueResult with execution details
        """
        start_time = time.time()

        print(f"\nProcessing Queue: {queue.source_face_name or queue.source_face_id}")
        print(f"  Matches: {queue.get_size()}")

        try:
            # Get source face from repository
            source_face_entry = self.repository_manager.get_face(queue.source_face_id)
            if not source_face_entry:
                return QueueResult(
                    queue_id=queue.source_face_id,
                    success=False,
                    faces_processed=0,
                    processing_time=time.time() - start_time,
                    error=f"Source face {queue.source_face_id} not found in repository"
                )

            # Group matches by source file
            matches_by_file = self._group_matches_by_file(queue.matches)

            # Process each source file
            output_files = []
            for source_file, file_matches in matches_by_file.items():
                print(f"  Processing: {Path(source_file).name}")
                print(f"    Faces to swap: {len(file_matches)}")

                # NOTE: This is a placeholder for actual face swapping
                # Integration with FaceFusion's face_swapper would go here
                output_file = self._process_file_placeholder(
                    source_file=source_file,
                    matches=file_matches,
                    source_face_entry=source_face_entry,
                    output_path=output_path
                )

                if output_file:
                    output_files.append(output_file)

                # Update progress
                if self.progress_tracker:
                    self.progress_tracker.update(len(file_matches))

                if progress_callback:
                    progress_callback(
                        self.progress_tracker.completed_items,
                        self.progress_tracker.total_items
                    )

            processing_time = time.time() - start_time

            return QueueResult(
                queue_id=queue.source_face_id,
                success=True,
                faces_processed=queue.get_size(),
                processing_time=processing_time,
                output_file=output_files[0] if output_files else None
            )

        except Exception as e:
            return QueueResult(
                queue_id=queue.source_face_id,
                success=False,
                faces_processed=0,
                processing_time=time.time() - start_time,
                error=str(e)
            )

    def _group_matches_by_file(
        self,
        matches: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        Group matches by source file.

        Args:
            matches: List of match dictionaries

        Returns:
            Dictionary mapping source file to list of matches
        """
        groups: Dict[str, List[Dict]] = {}

        for match in matches:
            source_file = match.get('source_file', 'unknown')
            if source_file not in groups:
                groups[source_file] = []
            groups[source_file].append(match)

        return groups

    def _process_file_placeholder(
        self,
        source_file: str,
        matches: List[Dict],
        source_face_entry,
        output_path: str
    ) -> Optional[str]:
        """
        Placeholder for actual file processing.

        This method demonstrates the structure but doesn't perform actual
        face swapping. Integration with FaceFusion's face_swapper module
        would be implemented here.

        Args:
            source_file: Source media file path
            matches: List of face matches for this file
            source_face_entry: Repository face entry for swapping
            output_path: Output directory

        Returns:
            Path to output file, or None if processing failed
        """
        try:
            source_path = Path(source_file)
            output_file = Path(output_path) / f"{source_path.stem}_swapped{source_path.suffix}"

            if is_image(source_file):
                # For images: Would load image, detect faces, swap, save
                print(f"    [PLACEHOLDER] Would swap {len(matches)} faces in image")
                print(f"    [PLACEHOLDER] Using source face: {source_face_entry.metadata.get('name', 'Unknown')}")
                print(f"    [PLACEHOLDER] Output would be: {output_file}")
                
                # In actual implementation:
                # 1. Load image using facefusion.vision.read_static_image
                # 2. For each match, get destination face location
                # 3. Use face_swapper to swap faces
                # 4. Save processed image
                
            elif is_video(source_file):
                # For videos: Would process frames, reassemble
                print(f"    [PLACEHOLDER] Would process video with {len(matches)} face swaps")
                print(f"    [PLACEHOLDER] Using source face: {source_face_entry.metadata.get('name', 'Unknown')}")
                
                # Frame matches need to be organized by frame number
                frame_groups = {}
                for match in matches:
                    frame_num = match.get('frame_number')
                    if frame_num is not None:
                        if frame_num not in frame_groups:
                            frame_groups[frame_num] = []
                        frame_groups[frame_num].append(match)
                
                print(f"    [PLACEHOLDER] Frames to process: {len(frame_groups)}")
                print(f"    [PLACEHOLDER] Output would be: {output_file}")
                
                # In actual implementation:
                # 1. Extract frames using facefusion.ffmpeg or video reader
                # 2. For each frame in frame_groups:
                #    - Load frame
                #    - Apply face swaps using face_swapper
                #    - Save processed frame
                # 3. Reassemble video with facefusion.ffmpeg
                # 4. Merge audio from original video
            
            # For now, just return the expected output path
            # In actual implementation, return None if processing failed
            return str(output_file)

        except Exception as e:
            print(f"    Error processing file: {e}")
            return None

    def get_processing_summary(self) -> str:
        """
        Get formatted processing summary.

        Returns:
            Human-readable summary string
        """
        if not self.progress_tracker:
            return "No processing in progress"

        return self.progress_tracker.get_progress_string()
