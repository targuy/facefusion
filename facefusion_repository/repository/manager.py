"""
Repository manager for face storage and retrieval.

Manages the face repository with automatic orientation detection,
quality assessment, and character associations.
"""

import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from facefusion_repository.repository.orientation_detector import OrientationDetector
from facefusion_repository.repository.orientation_matcher import OrientationMatcher
from facefusion_repository.repository.quality_assessor import QualityAssessor
from facefusion_repository.repository.character_manager import CharacterManager
from facefusion_repository.types import (
    FaceEntry,
    FaceMetadata,
    FaceOrientation,
    QualityThresholds,
    DEFAULT_QUALITY_THRESHOLDS,
    RepositoryStats
)


class RepositoryManager:
    """Manages face repository with orientation detection and quality assessment."""
    
    def __init__(self, repository_path: Optional[str] = None) -> None:
        """
        Initialize repository manager.
        
        Args:
            repository_path: Path to repository directory. If None, uses default.
        """
        if repository_path is None:
            repository_path = Path.home() / '.facefusion_repository'
        
        self.repository_path = Path(repository_path)
        self.repository_file = self.repository_path / 'repository.json'
        self.faces_dir = self.repository_path / 'faces'
        
        self._faces: Dict[str, FaceEntry] = {}
        self._loaded = False
    
    def initialize_repository(self) -> bool:
        """
        Initialize repository structure.
        
        Returns:
            True if initialization successful
        """
        try:
            # Create directories
            self.repository_path.mkdir(parents=True, exist_ok=True)
            self.faces_dir.mkdir(exist_ok=True)
            (self.repository_path / 'queues').mkdir(exist_ok=True)
            
            # Create empty repository file if it doesn't exist
            if not self.repository_file.exists():
                repo_data = {
                    'version': '2.0.0',
                    'created_date': datetime.utcnow().isoformat() + 'Z',
                    'last_modified': datetime.utcnow().isoformat() + 'Z',
                    'faces': []
                }
                with open(self.repository_file, 'w', encoding='utf-8') as f:
                    json.dump(repo_data, f, indent=2)
            
            # Initialize character manager
            char_mgr = CharacterManager(str(self.repository_path))
            char_mgr.initialize()
            
            return True
        except Exception as e:
            print(f'Error initializing repository: {e}')
            return False
    
    def _load_faces(self) -> bool:
        """Load faces from repository file."""
        if self._loaded:
            return True
        
        if not self.repository_file.exists():
            return False
        
        try:
            with open(self.repository_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._faces = {}
            for face_data in data.get('faces', []):
                face = FaceEntry.from_dict(face_data)
                self._faces[face.id] = face
            
            self._loaded = True
            return True
        except Exception as e:
            print(f'Error loading faces: {e}')
            return False
    
    def _save_faces(self) -> bool:
        """Save faces to repository file."""
        try:
            # Preserve original created date
            original_created = None
            if self.repository_file.exists():
                with open(self.repository_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    original_created = data.get('created_date')
            
            repo_data = {
                'version': '2.0.0',
                'created_date': original_created or datetime.utcnow().isoformat() + 'Z',
                'last_modified': datetime.utcnow().isoformat() + 'Z',
                'faces': [face.to_dict() for face in self._faces.values()]
            }
            
            with open(self.repository_file, 'w', encoding='utf-8') as f:
                json.dump(repo_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f'Error saving faces: {e}')
            return False
    
    def add_face(
        self,
        image_path: str,
        face_data: any,  # Face data from FaceFusion detector
        name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        character_id: Optional[str] = None,
        quality_thresholds: Optional[QualityThresholds] = None
    ) -> Optional[str]:
        """
        Add face to repository with automatic orientation detection.
        
        Args:
            image_path: Path to face image
            face_data: Face detection data from FaceFusion
            name: Optional name for the face
            tags: Optional tags
            character_id: Optional character ID
            quality_thresholds: Optional custom quality thresholds
            
        Returns:
            Face ID if successful, None otherwise
        """
        self._load_faces()
        
        if quality_thresholds is None:
            quality_thresholds = DEFAULT_QUALITY_THRESHOLDS
        
        try:
            # Assess quality
            detector_score = getattr(face_data, 'score', 0.9)
            quality_metrics, passes = QualityAssessor.assess_quality(
                image_path,
                detector_score,
                quality_thresholds
            )
            
            if not passes:
                print(f'Face quality below threshold')
                return None
            
            # Detect orientation automatically
            landmarks_68 = face_data.landmark_set.get('68') if hasattr(face_data, 'landmark_set') else None
            landmarks_5 = face_data.landmark_set.get('5') if hasattr(face_data, 'landmark_set') else None
            
            yaw, pitch, roll = OrientationDetector.calculate_orientation_from_landmarks(
                landmarks_68, landmarks_5
            )
            
            # Check if orientation is too extreme
            if OrientationDetector.is_extreme_orientation(yaw, pitch, roll):
                desc = OrientationDetector.get_orientation_description(yaw, pitch, roll)
                print(f'Face orientation too extreme: {desc}')
                print(f'Orientation: yaw={yaw:.1f}°, pitch={pitch:.1f}°, roll={roll:.1f}°')
                return None
            
            orientation = FaceOrientation(yaw=yaw, pitch=pitch, roll=roll)
            desc = OrientationDetector.get_orientation_description(yaw, pitch, roll)
            print(f'Detected orientation: {desc} (yaw={yaw:.1f}°, pitch={pitch:.1f}°, roll={roll:.1f}°)')
            
            # Check for duplicate orientations
            similar_faces = [
                f for f in self._faces.values()
                if OrientationMatcher.is_orientation_similar(
                    f.orientation_angle,
                    orientation.get_legacy_angle()
                )
            ]
            
            if similar_faces:
                best_existing = OrientationMatcher.get_best_quality_face(similar_faces)
                if best_existing and best_existing.quality_metrics.overall_quality > quality_metrics.overall_quality:
                    print(f'Higher quality face already exists for similar orientation')
                    return None
                
                # Remove lower quality faces
                for face in similar_faces:
                    if face.quality_metrics.overall_quality <= quality_metrics.overall_quality:
                        self.remove_face(face.id)
            
            # Generate face ID and copy image
            face_id = f'face_{datetime.utcnow().strftime("%Y%m%d")}_{uuid.uuid4().hex[:8]}'
            image_ext = Path(image_path).suffix
            dest_path = self.faces_dir / f'{face_id}{image_ext}'
            
            shutil.copy2(image_path, dest_path)
            
            # Extract face embedding and landmarks
            face_embedding = face_data.embedding if hasattr(face_data, 'embedding') else []
            face_landmarks = {
                '5': face_data.landmark_set.get('5', []).tolist() if hasattr(face_data, 'landmark_set') else [],
                '68': face_data.landmark_set.get('68', []).tolist() if hasattr(face_data, 'landmark_set') else []
            }
            
            # Create face entry
            face_entry = FaceEntry(
                id=face_id,
                file_path=str(dest_path),
                orientation=orientation,
                quality_metrics=quality_metrics,
                face_embedding=face_embedding,
                face_landmarks=face_landmarks,
                metadata=FaceMetadata(
                    added_date=datetime.utcnow().isoformat() + 'Z',
                    character_name=character_id,
                    face_name=name,
                    tags=tags or []
                )
            )
            
            # Add to repository
            self._faces[face_id] = face_entry
            self._save_faces()
            
            return face_id
        
        except Exception as e:
            print(f'Error adding face: {e}')
            return None
    
    def get_face(self, face_id: str) -> Optional[FaceEntry]:
        """Get face by ID."""
        self._load_faces()
        return self._faces.get(face_id)
    
    def list_faces(
        self,
        filter_by_orientation: Optional[int] = None,
        filter_by_tags: Optional[List[str]] = None,
        filter_by_character: Optional[str] = None
    ) -> List[FaceEntry]:
        """
        List faces with optional filters.
        
        Args:
            filter_by_orientation: Filter by orientation angle
            filter_by_tags: Filter by tags (must have all)
            filter_by_character: Filter by character ID
            
        Returns:
            List of face entries
        """
        self._load_faces()
        
        faces = list(self._faces.values())
        
        # Apply filters
        if filter_by_orientation is not None:
            faces = [
                f for f in faces
                if OrientationMatcher.is_orientation_similar(
                    f.orientation_angle,
                    filter_by_orientation
                )
            ]
        
        if filter_by_tags:
            faces = [
                f for f in faces
                if all(tag in f.metadata.tags for tag in filter_by_tags)
            ]
        
        if filter_by_character:
            faces = [
                f for f in faces
                if f.metadata.character_name == filter_by_character
            ]
        
        return faces
    
    def remove_face(self, face_id: str) -> bool:
        """Remove face from repository."""
        self._load_faces()
        
        if face_id not in self._faces:
            return False
        
        face = self._faces[face_id]
        
        # Delete image file
        try:
            Path(face.file_path).unlink(missing_ok=True)
        except Exception:
            pass
        
        # Remove from repository
        del self._faces[face_id]
        self._save_faces()
        
        return True
    
    def get_statistics(self) -> RepositoryStats:
        """Get repository statistics."""
        self._load_faces()
        
        if not self._faces:
            return RepositoryStats(
                total_faces=0,
                average_quality=0.0,
                total_size_mb=0.0,
                unique_names=0,
                faces_by_orientation={}
            )
        
        # Calculate stats
        total_faces = len(self._faces)
        average_quality = sum(f.quality_metrics.overall_quality for f in self._faces.values()) / total_faces
        
        # Calculate total size
        total_size = 0
        for face in self._faces.values():
            try:
                total_size += Path(face.file_path).stat().st_size
            except Exception:
                pass
        total_size_mb = total_size / (1024 * 1024)
        
        # Count unique names
        unique_names = len(set(
            f.metadata.character_name or f.metadata.face_name
            for f in self._faces.values()
            if f.metadata.character_name or f.metadata.face_name
        ))
        
        # Count faces by orientation
        faces_by_orientation = {}
        for face in self._faces.values():
            angle = face.orientation_angle
            faces_by_orientation[angle] = faces_by_orientation.get(angle, 0) + 1
        
        return RepositoryStats(
            total_faces=total_faces,
            average_quality=average_quality,
            total_size_mb=total_size_mb,
            unique_names=unique_names,
            faces_by_orientation=faces_by_orientation
        )
