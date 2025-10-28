"""
Repository manager for face storage and retrieval.
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy

from facefusion import face_analyser, state_manager
from facefusion.vision import read_static_image
from facefusion_repository.repository.orientation_matcher import OrientationMatcher
from facefusion_repository.repository.quality_assessor import QualityAssessor
from facefusion_repository.types import (
    DEFAULT_QUALITY_THRESHOLDS,
    FaceEntry,
    FaceMetadata,
    QualityThresholds,
    RepositoryStats
)


class RepositoryManager:
    """Manages face repository CRUD operations."""

    def __init__(self, repository_path: Optional[str] = None) -> None:
        """
        Initialize repository manager.

        Args:
            repository_path: Path to repository directory. If None, uses default.
        """
        if repository_path is None:
            repository_path = os.path.expanduser('~/.facefusion_repository')

        self.repository_path = Path(repository_path)
        self.repository_file = self.repository_path / 'repository.json'
        self.faces_dir = self.repository_path / 'faces'

        self._faces: Dict[str, FaceEntry] = {}
        self._loaded = False

    def initialize_repository(self) -> bool:
        """
        Create new repository structure.

        Returns:
            True if initialization successful
        """
        try:
            # Create directories
            self.repository_path.mkdir(parents=True, exist_ok=True)
            self.faces_dir.mkdir(parents=True, exist_ok=True)

            # Create empty repository file if it doesn't exist
            if not self.repository_file.exists():
                repository_data = {
                    'version': '1.0.0',
                    'created_date': datetime.utcnow().isoformat() + 'Z',
                    'last_modified': datetime.utcnow().isoformat() + 'Z',
                    'faces': []
                }
                with open(self.repository_file, 'w', encoding='utf-8') as f:
                    json.dump(repository_data, f, indent=2)

            return True
        except Exception as e:
            print(f'Error initializing repository: {e}')
            return False

    def _load_repository(self) -> bool:
        """
        Load repository from disk.

        Returns:
            True if load successful
        """
        if self._loaded:
            return True

        if not self.repository_file.exists():
            return False

        try:
            with open(self.repository_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._faces = {}
            for face_data in data.get('faces', []):
                face_entry = FaceEntry.from_dict(face_data)
                self._faces[face_entry.id] = face_entry

            self._loaded = True
            return True
        except Exception as e:
            print(f'Error loading repository: {e}')
            return False

    def _save_repository(self) -> bool:
        """
        Save repository to disk.

        Returns:
            True if save successful
        """
        try:
            # Load current data to preserve metadata
            if self.repository_file.exists():
                with open(self.repository_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    'version': '1.0.0',
                    'created_date': datetime.utcnow().isoformat() + 'Z'
                }

            # Update faces and modification time
            data['last_modified'] = datetime.utcnow().isoformat() + 'Z'
            data['faces'] = [face.to_dict() for face in self._faces.values()]

            # Write to file
            with open(self.repository_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f'Error saving repository: {e}')
            return False

    def add_face(
        self,
        image_path: str,
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        quality_thresholds: Optional[QualityThresholds] = None
    ) -> Optional[str]:
        """
        Add new face to repository.

        Args:
            image_path: Path to face image
            name: Optional name for the face
            tags: Optional tags for categorization
            quality_thresholds: Optional custom quality thresholds

        Returns:
            Face ID if successful, None otherwise
        """
        # Load repository
        if not self._load_repository():
            if not self.initialize_repository():
                return None
            self._load_repository()

        # Use default thresholds if not provided
        if quality_thresholds is None:
            quality_thresholds = DEFAULT_QUALITY_THRESHOLDS

        try:
            # Read image
            vision_frame = read_static_image(image_path)
            if vision_frame is None:
                print(f'Failed to read image: {image_path}')
                return None

            # Detect faces
            faces = face_analyser.get_many_faces([vision_frame])
            if not faces:
                print(f'No face detected in image: {image_path}')
                return None

            # Use first face (or could add option to select)
            face = faces[0]

            # Assess quality
            quality_metrics = QualityAssessor.assess_face(vision_frame, face)

            # Check quality thresholds
            if not QualityAssessor.is_acceptable_quality(quality_metrics, quality_thresholds):
                print(f'Face quality below threshold in image: {image_path}')
                print(f'Quality metrics: {quality_metrics}')
                return None

            # Get orientation angle
            orientation_angle = OrientationMatcher.get_closest_standard_angle(face.angle)

            # Check for similar orientation faces (potential duplicates)
            similar_faces = [
                f for f in self._faces.values()
                if OrientationMatcher.is_orientation_similar(f.orientation_angle, orientation_angle)
            ]

            # If similar faces exist, only keep the highest quality one
            if similar_faces:
                best_existing = OrientationMatcher.get_best_quality_face(similar_faces)
                if best_existing and best_existing.quality_metrics.overall_quality > quality_metrics.overall_quality:
                    print(f'Higher quality face already exists for orientation {orientation_angle}')
                    return None

                # Remove lower quality faces
                for similar_face in similar_faces:
                    if similar_face.quality_metrics.overall_quality < quality_metrics.overall_quality:
                        self.remove_face(similar_face.id)

            # Generate unique ID
            face_id = f'face_{datetime.utcnow().strftime("%Y%m%d")}_{uuid.uuid4().hex[:8]}'

            # Copy image to repository
            image_filename = f'{face_id}{Path(image_path).suffix}'
            dest_path = self.faces_dir / image_filename

            import shutil
            shutil.copy2(image_path, dest_path)

            # Create face entry
            face_entry = FaceEntry(
                id=face_id,
                file_path=str(dest_path),
                orientation_angle=orientation_angle,
                quality_metrics=quality_metrics,
                face_embedding=face.embedding,
                face_landmarks={
                    '5': face.landmark_set['5'].tolist(),
                    '68': face.landmark_set['68'].tolist()
                },
                metadata=FaceMetadata(
                    added_date=datetime.utcnow().isoformat() + 'Z',
                    name=name,
                    tags=tags or []
                )
            )

            # Add to repository
            self._faces[face_id] = face_entry

            # Save
            if not self._save_repository():
                return None

            print(f'Successfully added face: {face_id}')
            return face_id

        except Exception as e:
            print(f'Error adding face: {e}')
            return None

    def get_face(self, face_id: str) -> Optional[FaceEntry]:
        """
        Retrieve face entry by ID.

        Args:
            face_id: Face identifier

        Returns:
            FaceEntry or None if not found
        """
        if not self._load_repository():
            return None

        return self._faces.get(face_id)

    def list_faces(
        self,
        filter_by_orientation: Optional[int] = None,
        filter_by_tags: Optional[List[str]] = None
    ) -> List[FaceEntry]:
        """
        List all faces with optional filters.

        Args:
            filter_by_orientation: Filter by specific orientation angle
            filter_by_tags: Filter by tags (face must have all specified tags)

        Returns:
            List of FaceEntry objects
        """
        if not self._load_repository():
            return []

        faces = list(self._faces.values())

        # Apply orientation filter
        if filter_by_orientation is not None:
            faces = [
                f for f in faces
                if OrientationMatcher.is_orientation_similar(f.orientation_angle, filter_by_orientation, threshold=22)
            ]

        # Apply tags filter
        if filter_by_tags:
            faces = [
                f for f in faces
                if all(tag in f.metadata.tags for tag in filter_by_tags)
            ]

        return faces

    def remove_face(self, face_id: str) -> bool:
        """
        Remove face from repository.

        Args:
            face_id: Face identifier

        Returns:
            True if removal successful
        """
        if not self._load_repository():
            return False

        if face_id not in self._faces:
            print(f'Face not found: {face_id}')
            return False

        try:
            # Remove image file
            face_entry = self._faces[face_id]
            if os.path.exists(face_entry.file_path):
                os.remove(face_entry.file_path)

            # Remove from dictionary
            del self._faces[face_id]

            # Save
            return self._save_repository()

        except Exception as e:
            print(f'Error removing face: {e}')
            return False

    def update_face(self, face_id: str, **kwargs) -> bool:
        """
        Update face metadata.

        Args:
            face_id: Face identifier
            **kwargs: Metadata fields to update (name, tags)

        Returns:
            True if update successful
        """
        if not self._load_repository():
            return False

        if face_id not in self._faces:
            return False

        try:
            face_entry = self._faces[face_id]

            # Update allowed fields
            if 'name' in kwargs:
                face_entry.metadata.name = kwargs['name']
            if 'tags' in kwargs:
                face_entry.metadata.tags = kwargs['tags']

            return self._save_repository()

        except Exception as e:
            print(f'Error updating face: {e}')
            return False

    def get_statistics(self) -> Optional[RepositoryStats]:
        """
        Get repository statistics.

        Returns:
            RepositoryStats object or None
        """
        if not self._load_repository():
            return None

        faces = list(self._faces.values())

        if not faces:
            return RepositoryStats(
                total_faces=0,
                faces_by_orientation={},
                average_quality=0.0,
                total_size_mb=0.0,
                unique_names=0
            )

        # Count faces by orientation
        faces_by_orientation: Dict[int, int] = {}
        for face in faces:
            angle = face.orientation_angle
            faces_by_orientation[angle] = faces_by_orientation.get(angle, 0) + 1

        # Calculate average quality
        total_quality = sum(f.quality_metrics.overall_quality for f in faces)
        average_quality = total_quality / len(faces)

        # Calculate total size
        total_size_bytes = sum(
            os.path.getsize(f.file_path) if os.path.exists(f.file_path) else 0
            for f in faces
        )
        total_size_mb = total_size_bytes / (1024 * 1024)

        # Count unique names
        unique_names = len(set(f.metadata.name for f in faces if f.metadata.name))

        return RepositoryStats(
            total_faces=len(faces),
            faces_by_orientation=faces_by_orientation,
            average_quality=average_quality,
            total_size_mb=total_size_mb,
            unique_names=unique_names
        )
