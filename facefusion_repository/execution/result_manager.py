"""
Result manager for output organization and validation.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.types import BatchResult, QueueResult


class ResultManager:
    """
    Manages batch processing results and output organization.

    Handles result storage, quality validation, and output file organization.
    """

    def __init__(self, output_dir: Optional[str] = None) -> None:
        """
        Initialize result manager.

        Args:
            output_dir: Base directory for outputs. If None, uses default.
        """
        if output_dir is None:
            output_dir = os.path.expanduser('~/.facefusion_repository/outputs')

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._current_batch: Optional[str] = None
        self._results: List[BatchResult] = []

    def create_batch_output_directory(self, batch_id: Optional[str] = None) -> str:
        """
        Create output directory for a batch.

        Args:
            batch_id: Optional batch identifier. If None, generates timestamp-based ID.

        Returns:
            Path to batch output directory
        """
        if batch_id is None:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            batch_id = f'batch_{timestamp}'

        batch_dir = self.output_dir / batch_id
        batch_dir.mkdir(parents=True, exist_ok=True)

        self._current_batch = batch_id
        return str(batch_dir)

    def get_output_path(
        self,
        filename: str,
        batch_id: Optional[str] = None,
        subdirectory: Optional[str] = None
    ) -> str:
        """
        Get output path for a file.

        Args:
            filename: Output filename
            batch_id: Batch identifier. If None, uses current batch.
            subdirectory: Optional subdirectory within batch

        Returns:
            Full path for output file
        """
        if batch_id is None:
            batch_id = self._current_batch or 'default'

        batch_dir = self.output_dir / batch_id

        if subdirectory:
            output_dir = batch_dir / subdirectory
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = batch_dir

        return str(output_dir / filename)

    def save_batch_result(self, batch_result: BatchResult, batch_id: Optional[str] = None) -> bool:
        """
        Save batch processing result.

        Args:
            batch_result: BatchResult object to save
            batch_id: Optional batch identifier

        Returns:
            True if save successful
        """
        if batch_id is None:
            batch_id = self._current_batch or 'default'

        try:
            result_path = self.get_output_path('batch_result.json', batch_id)

            result_data = {
                'batch_id': batch_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'total_queues': batch_result.total_queues,
                'successful_queues': batch_result.successful_queues,
                'failed_queues': batch_result.failed_queues,
                'total_swaps': batch_result.total_swaps,
                'successful_swaps': batch_result.successful_swaps,
                'failed_swaps': batch_result.failed_swaps,
                'total_time': batch_result.total_time,
                'queue_results': [
                    {
                        'face_id': qr.face_id,
                        'total_swaps': qr.total_swaps,
                        'successful_swaps': qr.successful_swaps,
                        'failed_swaps': qr.failed_swaps,
                        'processing_time': qr.processing_time,
                        'errors': qr.errors
                    }
                    for qr in batch_result.queue_results
                ]
            }

            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2)

            self._results.append(batch_result)
            return True

        except Exception as e:
            print(f'Error saving batch result: {e}')
            return False

    def load_batch_result(self, batch_id: str) -> Optional[BatchResult]:
        """
        Load batch result from disk.

        Args:
            batch_id: Batch identifier

        Returns:
            BatchResult object, or None if not found
        """
        try:
            result_path = self.output_dir / batch_id / 'batch_result.json'

            if not result_path.exists():
                return None

            with open(result_path, 'r', encoding='utf-8') as f:
                result_data = json.load(f)

            queue_results = [
                QueueResult(
                    face_id=qr['face_id'],
                    total_swaps=qr['total_swaps'],
                    successful_swaps=qr['successful_swaps'],
                    failed_swaps=qr['failed_swaps'],
                    processing_time=qr['processing_time'],
                    errors=qr.get('errors', [])
                )
                for qr in result_data.get('queue_results', [])
            ]

            return BatchResult(
                total_queues=result_data['total_queues'],
                successful_queues=result_data['successful_queues'],
                failed_queues=result_data['failed_queues'],
                total_swaps=result_data['total_swaps'],
                successful_swaps=result_data['successful_swaps'],
                failed_swaps=result_data['failed_swaps'],
                total_time=result_data['total_time'],
                queue_results=queue_results
            )

        except Exception as e:
            print(f'Error loading batch result: {e}')
            return None

    def list_batches(self) -> List[str]:
        """
        List all batch directories.

        Returns:
            List of batch IDs
        """
        try:
            return [
                d.name for d in self.output_dir.iterdir()
                if d.is_dir() and d.name.startswith('batch_')
            ]
        except Exception as e:
            print(f'Error listing batches: {e}')
            return []

    def validate_output(self, output_path: str) -> Dict[str, bool]:
        """
        Validate output file.

        Args:
            output_path: Path to output file

        Returns:
            Dictionary with validation results
        """
        validation = {
            'exists': os.path.exists(output_path),
            'readable': False,
            'non_empty': False,
            'valid_format': False
        }

        if validation['exists']:
            try:
                # Check if file is readable
                validation['readable'] = os.access(output_path, os.R_OK)

                # Check if file is non-empty
                file_size = os.path.getsize(output_path)
                validation['non_empty'] = file_size > 0

                # Check if format is valid (basic check)
                file_ext = os.path.splitext(output_path)[1].lower()
                valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.jpg', '.png', '.jpeg']
                validation['valid_format'] = file_ext in valid_extensions

            except Exception as e:
                print(f'Error validating output: {e}')

        return validation

    def generate_summary_report(self, batch_id: str) -> str:
        """
        Generate summary report for a batch.

        Args:
            batch_id: Batch identifier

        Returns:
            Formatted summary report
        """
        batch_result = self.load_batch_result(batch_id)

        if batch_result is None:
            return f'No results found for batch: {batch_id}'

        report = f'Batch Processing Summary: {batch_id}\n'
        report += '=' * 60 + '\n\n'

        report += f'Total Queues: {batch_result.total_queues}\n'
        report += f'Successful Queues: {batch_result.successful_queues}\n'
        report += f'Failed Queues: {batch_result.failed_queues}\n\n'

        report += f'Total Swaps: {batch_result.total_swaps}\n'
        report += f'Successful Swaps: {batch_result.successful_swaps}\n'
        report += f'Failed Swaps: {batch_result.failed_swaps}\n\n'

        success_rate = 0.0
        if batch_result.total_swaps > 0:
            success_rate = (batch_result.successful_swaps / batch_result.total_swaps) * 100.0

        report += f'Success Rate: {success_rate:.1f}%\n\n'

        hours, remainder = divmod(int(batch_result.total_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        report += f'Processing Time: {hours}h {minutes}m {seconds}s\n\n'

        if batch_result.queue_results:
            report += 'Queue Details:\n'
            report += '-' * 60 + '\n'

            for qr in batch_result.queue_results:
                report += f'\nFace ID: {qr.face_id}\n'
                report += f'  Total: {qr.total_swaps}, '
                report += f'Success: {qr.successful_swaps}, '
                report += f'Failed: {qr.failed_swaps}\n'
                report += f'  Time: {qr.processing_time:.1f}s\n'

                if qr.errors:
                    report += f'  Errors: {len(qr.errors)}\n'

        return report

    def cleanup_batch(self, batch_id: str, keep_results: bool = True) -> bool:
        """
        Clean up batch output directory.

        Args:
            batch_id: Batch identifier
            keep_results: Whether to keep result JSON files

        Returns:
            True if cleanup successful
        """
        try:
            batch_dir = self.output_dir / batch_id

            if not batch_dir.exists():
                return True

            # Remove files except results if keep_results is True
            for file_path in batch_dir.iterdir():
                if file_path.is_file():
                    if keep_results and file_path.name.endswith('.json'):
                        continue
                    file_path.unlink()

            # Remove empty subdirectories
            for subdir in batch_dir.iterdir():
                if subdir.is_dir() and not any(subdir.iterdir()):
                    subdir.rmdir()

            # Remove batch directory if empty
            if not keep_results and not any(batch_dir.iterdir()):
                batch_dir.rmdir()

            return True

        except Exception as e:
            print(f'Error cleaning up batch: {e}')
            return False
