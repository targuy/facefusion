"""
Repository manager for face storage and retrieval.
"""

import json
import os
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.repository.orientation_matcher import OrientationMatcher
from facefusion_repository.repository.quality_assessor import QualityAssessor
from facefusion_repository.types import (
    DEFAULT_QUALITY_THRESHOLDS,
    FaceEntry,
    FaceMetadata,
    PersonEntry,
    QualityThresholds,
    RepositoryStats
)

from facefusion import face_analyser
from facefusion.vision import read_static_image


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
        self.metadata_file = self.repository_path / 'metadata.json'
        self.faces_dir = self.repository_path / 'faces'
        self.settings_dir = self.repository_path / 'settings'
        self.presets_dir = self.repository_path / 'presets'
        self.queues_dir = self.repository_path / 'queues'
        self.test_images_dir = self.repository_path / 'test_images'

        self._faces: Dict[str, FaceEntry] = {}
        self._people: Dict[str, PersonEntry] = {}
        self._loaded = False

    def initialize_repository(self) -> bool:
        """
        Create new repository structure with person-based directories.

        Returns:
            True if initialization successful
        """
        try:
            # Create main directories
            self.repository_path.mkdir(parents=True, exist_ok=True)
            self.faces_dir.mkdir(parents=True, exist_ok=True)
            self.settings_dir.mkdir(parents=True, exist_ok=True)
            self.presets_dir.mkdir(parents=True, exist_ok=True)
            self.queues_dir.mkdir(parents=True, exist_ok=True)
            self.test_images_dir.mkdir(parents=True, exist_ok=True)

            # Create repository file if it doesn't exist
            if not self.repository_file.exists():
                repository_data = {
                    'version': '2.0.0',  # Version 2.0 for person-based architecture
                    'created_date': datetime.utcnow().isoformat() + 'Z',
                    'last_modified': datetime.utcnow().isoformat() + 'Z',
                    'people': [],
                    'faces': []
                }
                with open(self.repository_file, 'w', encoding='utf-8') as f:
                    json.dump(repository_data, f, indent=2)
            
            # Create metadata file if it doesn't exist
            if not self.metadata_file.exists():
                metadata = {
                    'version': '2.0.0',
                    'architecture': 'person-based',
                    'created_date': datetime.utcnow().isoformat() + 'Z'
                }
                with open(self.metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)

            return True
        except Exception as e:
            print(f'Error initializing repository: {e}')
            return False

    def _load_repository(self) -> bool:
        """
        Load repository from disk (supports both v1 and v2 formats).

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

            # Load people (v2 format)
            self._people = {}
            for person_data in data.get('people', []):
                person_entry = PersonEntry.from_dict(person_data)
                self._people[person_entry.id] = person_entry

            # Load faces
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
        Save repository to disk (v2 format with people).

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
                    'version': '2.0.0',
                    'created_date': datetime.utcnow().isoformat() + 'Z'
                }

            # Update last modified
            data['last_modified'] = datetime.utcnow().isoformat() + 'Z'

            # Save people
            data['people'] = [person.to_dict() for person in self._people.values()]

            # Save faces
            data['faces'] = [face.to_dict() for face in self._faces.values()]

            # Write to file
            with open(self.repository_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f'Error saving repository: {e}')
            return False

    def add_person(self, person_id: str, display_name: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a new person to the repository.

        Args:
            person_id: Unique identifier for the person (alphanumeric, no spaces)
            display_name: Human-readable name for the person
            metadata: Optional additional metadata

        Returns:
            True if successful, False otherwise
        """
        # Load repository
        if not self._load_repository():
            if not self.initialize_repository():
                return False
            self._load_repository()

        # Validate person_id format (alphanumeric and underscores only)
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', person_id):
            print(f'Invalid person_id: {person_id}. Must be alphanumeric with underscores only.')
            return False

        # Check if person already exists
        if person_id in self._people:
            print(f'Person with id "{person_id}" already exists.')
            return False

        try:
            # Create person directory
            person_dir = self.faces_dir / person_id
            person_dir.mkdir(parents=True, exist_ok=True)

            # Create person entry
            person = PersonEntry(
                id=person_id,
                display_name=display_name,
                face_ids=[],
                created_date=datetime.utcnow().isoformat() + 'Z',
                last_modified=datetime.utcnow().isoformat() + 'Z',
                metadata=metadata or {}
            )

            self._people[person_id] = person
            return self._save_repository()
        except Exception as e:
            print(f'Error adding person: {e}')
            return False

    def get_person(self, person_id: str) -> Optional[PersonEntry]:
        """
        Get a person by ID.

        Args:
            person_id: Person identifier

        Returns:
            PersonEntry if found, None otherwise
        """
        if not self._load_repository():
            return None
        return self._people.get(person_id)

    def list_people(self) -> List[PersonEntry]:
        """
        List all people in the repository.

        Returns:
            List of PersonEntry objects
        """
        if not self._load_repository():
            return []
        return list(self._people.values())

    def remove_person(self, person_id: str, remove_faces: bool = True) -> bool:
        """
        Remove a person from the repository.

        Args:
            person_id: Person identifier
            remove_faces: If True, also remove all faces for this person

        Returns:
            True if successful, False otherwise
        """
        if not self._load_repository():
            return False

        person = self._people.get(person_id)
        if not person:
            print(f'Person not found: {person_id}')
            return False

        try:
            # Remove faces if requested
            if remove_faces:
                for face_id in person.face_ids[:]:  # Copy list to avoid modification during iteration
                    self.remove_face(face_id)

            # Remove person directory
            person_dir = self.faces_dir / person_id
            if person_dir.exists():
                shutil.rmtree(person_dir)

            # Remove person entry
            del self._people[person_id]
            return self._save_repository()
        except Exception as e:
            print(f'Error removing person: {e}')
            return False

    def add_face(
        self,
        image_path: str,
        person_id: str,  # Now MANDATORY
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        quality_thresholds: Optional[QualityThresholds] = None
    ) -> Optional[str]:
        """
        Add new face to repository for a specific person.

        Args:
            image_path: Path to face image
            person_id: Person this face belongs to (MANDATORY)
            name: Optional descriptive name for this specific face
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

        # Ensure person exists, create if not
        if person_id not in self._people:
            print(f'Person "{person_id}" does not exist. Creating person...')
            if not self.add_person(person_id, person_id):  # Use person_id as display name
                return None

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

            # Check for similar orientation faces (potential duplicates) within same person
            similar_faces = [
                f for f in self._faces.values()
                if f.metadata.person_id == person_id and OrientationMatcher.is_orientation_similar(f.orientation_angle, orientation_angle)
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

            # Copy image to person directory
            image_filename = f'{face_id}{Path(image_path).suffix}'
            person_dir = self.faces_dir / person_id
            person_dir.mkdir(parents=True, exist_ok=True)
            dest_path = person_dir / image_filename

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
                    person_id=person_id,
                    name=name,
                    tags=tags or []
                )
            )

            # Add to repository
            self._faces[face_id] = face_entry

            # Update person entry
            person = self._people[person_id]
            person.face_ids.append(face_id)
            person.last_modified = datetime.utcnow().isoformat() + 'Z'

            # Save
            if not self._save_repository():
                return None

            print(f'Successfully added face: {face_id} for person: {person_id}')
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
        Remove face from repository and update person entry.

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
            # Get face entry
            face_entry = self._faces[face_id]
            
            # Remove image file
            if os.path.exists(face_entry.file_path):
                os.remove(face_entry.file_path)

            # Update person entry
            person_id = face_entry.metadata.person_id
            if person_id in self._people:
                person = self._people[person_id]
                if face_id in person.face_ids:
                    person.face_ids.remove(face_id)
                person.last_modified = datetime.utcnow().isoformat() + 'Z'

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
        Get repository statistics including person-based metrics.

        Returns:
            RepositoryStats object or None
        """
        if not self._load_repository():
            return None

        faces = list(self._faces.values())

        if not faces:
            return RepositoryStats(
                total_faces=0,
                total_people=len(self._people),
                faces_by_orientation={},
                faces_by_person={},
                average_quality=0.0,
                total_size_mb=0.0,
                unique_names=0
            )

        # Count faces by orientation
        faces_by_orientation: Dict[int, int] = {}
        for face in faces:
            angle = face.orientation_angle
            faces_by_orientation[angle] = faces_by_orientation.get(angle, 0) + 1

        # Count faces by person
        faces_by_person: Dict[str, int] = {}
        for face in faces:
            person_id = face.metadata.person_id
            faces_by_person[person_id] = faces_by_person.get(person_id, 0) + 1

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
            total_people=len(self._people),
            faces_by_orientation=faces_by_orientation,
            faces_by_person=faces_by_person,
            average_quality=average_quality,
            total_size_mb=total_size_mb,
            unique_names=unique_names
        )
