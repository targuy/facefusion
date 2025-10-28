"""
Queue manager for batch processing with FaceFusion integration.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.types import DestinationSelectionSettings, QueueEntry


class QueueManager:
    """Manages processing queues with FaceFusion destination selection."""

    def __init__(self, queues_dir: Optional[str] = None) -> None:
        """
        Initialize queue manager.

        Args:
            queues_dir: Path to queues directory. If None, uses default.
        """
        if queues_dir is None:
            repo_path = Path.home() / '.facefusion_repository'
            queues_dir = str(repo_path / 'queues')
        
        self.queues_dir = Path(queues_dir)
        self.queues_dir.mkdir(parents=True, exist_ok=True)
        
        self._queues: Dict[str, QueueEntry] = {}
        self._loaded = False

    def create_queue(
        self,
        person: str,
        face_id: str,
        destination_media: str,
        face_selector_mode: str = 'reference',
        face_index: Optional[int] = None,
        reference_face_position: int = 0,
        reference_face_distance: float = 0.6,
        reference_frame_number: int = 0,
        processing_settings: Optional[str] = None
    ) -> str:
        """
        Create a new processing queue entry.

        Args:
            person: Person name
            face_id: Source face ID
            destination_media: Path to destination media (video or image)
            face_selector_mode: FaceFusion face selector mode
            face_index: Specific face index (for 'one' mode)
            reference_face_position: Reference face position
            reference_face_distance: Reference face distance threshold
            reference_frame_number: Reference frame number
            processing_settings: Optional settings profile name

        Returns:
            Queue ID
        """
        queue_id = str(uuid.uuid4())
        
        destination_selection = DestinationSelectionSettings(
            face_selector_mode=face_selector_mode,
            face_index=face_index,
            reference_face_position=reference_face_position,
            reference_face_distance=reference_face_distance,
            reference_frame_number=reference_frame_number
        )
        
        queue_entry = QueueEntry(
            queue_id=queue_id,
            source_person=person,
            source_face_id=face_id,
            destination_media=destination_media,
            destination_selection=destination_selection,
            processing_settings=processing_settings,
            created_date=datetime.utcnow().isoformat() + 'Z',
            status='pending'
        )
        
        # Save queue entry to file
        queue_file = self.queues_dir / f'{queue_id}.json'
        
        try:
            data = {
                'queue_id': queue_entry.queue_id,
                'source_person': queue_entry.source_person,
                'source_face_id': queue_entry.source_face_id,
                'destination_media': queue_entry.destination_media,
                'destination_selection': {
                    'face_selector_mode': destination_selection.face_selector_mode,
                    'face_index': destination_selection.face_index,
                    'reference_face_position': destination_selection.reference_face_position,
                    'reference_face_distance': destination_selection.reference_face_distance,
                    'reference_frame_number': destination_selection.reference_frame_number
                },
                'processing_settings': queue_entry.processing_settings,
                'created_date': queue_entry.created_date,
                'status': queue_entry.status
            }
            
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            self._queues[queue_id] = queue_entry
            
            return queue_id
            
        except Exception as e:
            print(f'Error creating queue: {e}')
            raise

    def get_queue(self, queue_id: str) -> Optional[QueueEntry]:
        """
        Get queue entry by ID.

        Args:
            queue_id: Queue identifier

        Returns:
            QueueEntry or None
        """
        queue_file = self.queues_dir / f'{queue_id}.json'
        
        if not queue_file.exists():
            return None
        
        try:
            with open(queue_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            dest_sel = data['destination_selection']
            destination_selection = DestinationSelectionSettings(
                face_selector_mode=dest_sel['face_selector_mode'],
                face_index=dest_sel.get('face_index'),
                reference_face_position=dest_sel.get('reference_face_position', 0),
                reference_face_distance=dest_sel.get('reference_face_distance', 0.6),
                reference_frame_number=dest_sel.get('reference_frame_number', 0)
            )
            
            return QueueEntry(
                queue_id=data['queue_id'],
                source_person=data['source_person'],
                source_face_id=data['source_face_id'],
                destination_media=data['destination_media'],
                destination_selection=destination_selection,
                processing_settings=data.get('processing_settings'),
                created_date=data.get('created_date'),
                status=data.get('status', 'pending')
            )
            
        except Exception as e:
            print(f'Error loading queue {queue_id}: {e}')
            return None

    def list_queues(self, status: Optional[str] = None) -> List[QueueEntry]:
        """
        List all queue entries.

        Args:
            status: Optional status filter ('pending', 'processing', 'completed', 'failed')

        Returns:
            List of QueueEntry objects
        """
        queues = []
        
        # Find all queue JSON files
        for queue_file in self.queues_dir.glob('*.json'):
            queue_id = queue_file.stem
            queue_entry = self.get_queue(queue_id)
            
            if queue_entry:
                if status is None or queue_entry.status == status:
                    queues.append(queue_entry)
        
        # Sort by created date
        queues.sort(key=lambda q: q.created_date or '', reverse=True)
        
        return queues

    def update_queue_status(self, queue_id: str, status: str) -> bool:
        """
        Update queue status.

        Args:
            queue_id: Queue identifier
            status: New status ('pending', 'processing', 'completed', 'failed')

        Returns:
            True if successful
        """
        queue_entry = self.get_queue(queue_id)
        
        if not queue_entry:
            return False
        
        queue_entry.status = status
        
        # Save updated entry
        queue_file = self.queues_dir / f'{queue_id}.json'
        
        try:
            data = {
                'queue_id': queue_entry.queue_id,
                'source_person': queue_entry.source_person,
                'source_face_id': queue_entry.source_face_id,
                'destination_media': queue_entry.destination_media,
                'destination_selection': {
                    'face_selector_mode': queue_entry.destination_selection.face_selector_mode,
                    'face_index': queue_entry.destination_selection.face_index,
                    'reference_face_position': queue_entry.destination_selection.reference_face_position,
                    'reference_face_distance': queue_entry.destination_selection.reference_face_distance,
                    'reference_frame_number': queue_entry.destination_selection.reference_frame_number
                },
                'processing_settings': queue_entry.processing_settings,
                'created_date': queue_entry.created_date,
                'status': queue_entry.status
            }
            
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f'Error updating queue {queue_id}: {e}')
            return False

    def delete_queue(self, queue_id: str) -> bool:
        """
        Delete queue entry.

        Args:
            queue_id: Queue identifier

        Returns:
            True if successful
        """
        queue_file = self.queues_dir / f'{queue_id}.json'
        
        if not queue_file.exists():
            return False
        
        try:
            queue_file.unlink()
            if queue_id in self._queues:
                del self._queues[queue_id]
            return True
        except Exception as e:
            print(f'Error deleting queue {queue_id}: {e}')
            return False

    def get_queue_statistics(self) -> Dict[str, any]:
        """
        Get queue statistics.

        Returns:
            Dictionary with statistics
        """
        all_queues = self.list_queues()
        
        stats = {
            'total': len(all_queues),
            'by_status': {},
            'by_person': {}
        }
        
        for queue in all_queues:
            # Count by status
            status = queue.status
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Count by person
            person = queue.source_person
            stats['by_person'][person] = stats['by_person'].get(person, 0) + 1
        
        return stats
