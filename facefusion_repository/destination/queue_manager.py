"""
Processing queue management for destination faces.

Organizes matched destination faces into processing queues grouped by
source repository face, with persistence and statistics.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.destination.matcher import FaceMatch
from facefusion_repository.types import QueueStats


class ProcessingQueue:
    """Represents a processing queue for a single source face."""

    def __init__(
        self,
        source_face_id: str,
        source_face_name: Optional[str] = None
    ):
        """
        Initialize processing queue.

        Args:
            source_face_id: Repository face ID
            source_face_name: Optional name of source face
        """
        self.source_face_id = source_face_id
        self.source_face_name = source_face_name
        self.matches: List[Dict] = []
        self.created_date = datetime.utcnow().isoformat() + 'Z'

    def add_match(
        self,
        match: FaceMatch,
        frame_number: Optional[int] = None,
        timestamp: Optional[float] = None,
        source_file: Optional[str] = None
    ) -> None:
        """
        Add a face match to the queue.

        Args:
            match: FaceMatch object
            frame_number: Optional frame number for video
            timestamp: Optional timestamp for video
            source_file: Source media file path
        """
        match_data = {
            'confidence': float(match.confidence),
            'orientation_difference': int(match.orientation_difference),
            'source_file': source_file,
            'frame_number': frame_number,
            'timestamp': timestamp
        }
        self.matches.append(match_data)

    def get_size(self) -> int:
        """Get number of matches in queue."""
        return len(self.matches)

    def get_average_confidence(self) -> float:
        """Get average confidence of matches in queue."""
        if not self.matches:
            return 0.0
        total = sum(m['confidence'] for m in self.matches)
        return total / len(self.matches)

    def to_dict(self) -> Dict:
        """Serialize queue to dictionary."""
        return {
            'source_face_id': self.source_face_id,
            'source_face_name': self.source_face_name,
            'created_date': self.created_date,
            'match_count': len(self.matches),
            'average_confidence': self.get_average_confidence(),
            'matches': self.matches
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ProcessingQueue':
        """Deserialize queue from dictionary."""
        queue = cls(
            source_face_id=data['source_face_id'],
            source_face_name=data.get('source_face_name')
        )
        queue.created_date = data.get('created_date', queue.created_date)
        queue.matches = data.get('matches', [])
        return queue


class QueueManager:
    """Manages processing queues for destination face matches."""

    def __init__(self, repository_path: Optional[str] = None):
        """
        Initialize queue manager.

        Args:
            repository_path: Path to repository directory
        """
        if repository_path is None:
            repository_path = os.path.expanduser('~/.facefusion_repository')

        self.repository_path = Path(repository_path)
        self.queues_dir = self.repository_path / 'queues'
        self.queues_file = self.queues_dir / 'processing_queues.json'

        # Ensure queues directory exists
        self.queues_dir.mkdir(parents=True, exist_ok=True)

        self._queues: Dict[str, ProcessingQueue] = {}
        self._loaded = False

    def _load_queues(self) -> bool:
        """Load queues from disk."""
        if self._loaded:
            return True

        if not self.queues_file.exists():
            return True

        try:
            with open(self.queues_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._queues = {}
            for queue_data in data.get('queues', []):
                queue = ProcessingQueue.from_dict(queue_data)
                self._queues[queue.source_face_id] = queue

            self._loaded = True
            return True
        except Exception as e:
            print(f'Error loading queues: {e}')
            return False

    def _save_queues(self) -> bool:
        """Save queues to disk."""
        try:
            data = {
                'version': '1.0.0',
                'last_updated': datetime.utcnow().isoformat() + 'Z',
                'queues': [queue.to_dict() for queue in self._queues.values()]
            }

            with open(self.queues_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f'Error saving queues: {e}')
            return False

    def create_queues_from_matches(
        self,
        matches: List[FaceMatch],
        source_file: str,
        frame_numbers: Optional[List[int]] = None,
        timestamps: Optional[List[float]] = None
    ) -> bool:
        """
        Create or update processing queues from face matches.

        Args:
            matches: List of FaceMatch objects
            source_file: Path to source media file
            frame_numbers: Optional list of frame numbers
            timestamps: Optional list of timestamps

        Returns:
            True if successful
        """
        self._load_queues()

        for i, match in enumerate(matches):
            face_id = match.repository_face.id
            face_name = match.repository_face.metadata.name

            # Create queue if doesn't exist
            if face_id not in self._queues:
                self._queues[face_id] = ProcessingQueue(face_id, face_name)

            # Add match to queue
            frame_num = frame_numbers[i] if frame_numbers else None
            timestamp = timestamps[i] if timestamps else None

            self._queues[face_id].add_match(
                match=match,
                frame_number=frame_num,
                timestamp=timestamp,
                source_file=source_file
            )

        return self._save_queues()

    def get_queue(self, source_face_id: str) -> Optional[ProcessingQueue]:
        """
        Get a specific processing queue.

        Args:
            source_face_id: Repository face ID

        Returns:
            ProcessingQueue or None
        """
        self._load_queues()
        return self._queues.get(source_face_id)

    def list_queues(self) -> List[ProcessingQueue]:
        """
        List all processing queues.

        Returns:
            List of ProcessingQueue objects
        """
        self._load_queues()
        return list(self._queues.values())

    def clear_queue(self, source_face_id: str) -> bool:
        """
        Clear a specific processing queue.

        Args:
            source_face_id: Repository face ID

        Returns:
            True if successful
        """
        self._load_queues()

        if source_face_id in self._queues:
            del self._queues[source_face_id]
            return self._save_queues()

        return False

    def clear_all_queues(self) -> bool:
        """
        Clear all processing queues.

        Returns:
            True if successful
        """
        self._queues = {}
        return self._save_queues()

    def get_statistics(self) -> QueueStats:
        """
        Get queue statistics.

        Returns:
            QueueStats object
        """
        self._load_queues()

        total_faces = sum(q.get_size() for q in self._queues.values())
        faces_per_queue = {
            face_id: queue.get_size()
            for face_id, queue in self._queues.items()
        }

        return QueueStats(
            total_queues=len(self._queues),
            total_faces=total_faces,
            faces_per_queue=faces_per_queue
        )

    def export_queue(
        self,
        source_face_id: str,
        output_path: str
    ) -> bool:
        """
        Export a specific queue to JSON file.

        Args:
            source_face_id: Repository face ID
            output_path: Path to output JSON file

        Returns:
            True if successful
        """
        self._load_queues()

        queue = self._queues.get(source_face_id)
        if not queue:
            return False

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(queue.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f'Error exporting queue: {e}')
            return False
