"""
Backend functions for Repository UI.
"""

from pathlib import Path
from typing import Any, List, Optional, Tuple
import traceback

from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.repository.character_manager import CharacterManager
from facefusion_repository.destination.analyzer import DestinationAnalyzer
from facefusion_repository.destination.queue_manager import QueueManager


def initialize_repository() -> Tuple[bool, str]:
    """
    Initialize the repository.
    
    Returns:
        Tuple of (success, message)
    """
    try:
        repo = RepositoryManager()
        if repo.initialize_repository():
            return True, "✓ Repository initialized successfully"
        return False, "✗ Failed to initialize repository"
    except Exception as e:
        return False, f"✗ Error: {str(e)}"


def add_face_to_repository(
    image_path: Optional[str],
    name: Optional[str],
    tags: Optional[str],
    character_id: Optional[str]
) -> str:
    """
    Add face to repository.
    
    Args:
        image_path: Path to face image
        name: Face name
        tags: Comma-separated tags
        character_id: Character ID
        
    Returns:
        Status message
    """
    try:
        if not image_path:
            return "✗ Please upload a face image"
        
        # Parse tags
        tag_list = None
        if tags and tags.strip():
            tag_list = [t.strip() for t in tags.split(',')]
        
        # Parse character_id
        char_id = character_id.strip() if character_id and character_id.strip() else None
        
        repo = RepositoryManager()
        face_id = repo.add_face(
            image_path=image_path,
            name=name if name and name.strip() else None,
            tags=tag_list,
            character_id=char_id
        )
        
        if face_id:
            msg = f"✓ Face added successfully!\nID: {face_id}\n"
            if name:
                msg += f"Name: {name}\n"
            if tag_list:
                msg += f"Tags: {', '.join(tag_list)}\n"
            if char_id:
                msg += f"Character: {char_id}\n"
            return msg
        else:
            return "✗ Failed to add face. Check image quality and try again."
    except Exception as e:
        return f"✗ Error: {str(e)}\n{traceback.format_exc()}"


def list_faces_in_repository(
    orientation_filter: str,
    character_filter: Optional[str]
) -> List[List[str]]:
    """
    List faces in repository.
    
    Args:
        orientation_filter: Orientation filter ("All" or angle)
        character_filter: Character ID filter
        
    Returns:
        List of face data rows
    """
    try:
        repo = RepositoryManager()
        
        # Parse orientation filter
        orient = None
        if orientation_filter != "All":
            orient = int(orientation_filter.replace("°", ""))
        
        # Parse character filter
        char_id = character_filter.strip() if character_filter and character_filter.strip() else None
        
        faces = repo.list_faces(
            filter_by_orientation=orient,
            filter_by_character=char_id
        )
        
        if not faces:
            return [["No faces found", "", "", "", "", ""]]
        
        result = []
        for face in faces:
            orient_3d = ""
            if face.orientation_3d:
                orient_3d = f"Y:{face.orientation_3d.yaw:.1f}° P:{face.orientation_3d.pitch:.1f}° R:{face.orientation_3d.roll:.1f}°"
            
            result.append([
                face.id,
                face.metadata.name or "Unnamed",
                f"{face.orientation_angle}°",
                orient_3d,
                f"{face.quality_metrics.overall_quality:.2f}",
                face.metadata.character_id or "-"
            ])
        
        return result
    except Exception as e:
        return [[f"Error: {str(e)}", "", "", "", "", ""]]


def show_face_details(face_id: str) -> str:
    """
    Show detailed information about a face.
    
    Args:
        face_id: Face identifier
        
    Returns:
        Formatted face details
    """
    try:
        if not face_id or not face_id.strip():
            return "Please enter a face ID"
        
        repo = RepositoryManager()
        face = repo.get_face(face_id.strip())
        
        if not face:
            return f"✗ Face not found: {face_id}"
        
        details = f"Face Details\n{'=' * 60}\n\n"
        details += f"ID: {face.id}\n"
        details += f"Name: {face.metadata.name or 'Unnamed'}\n"
        details += f"File: {face.file_path}\n\n"
        
        details += f"Orientation:\n"
        details += f"  Legacy Angle: {face.orientation_angle}°\n"
        if face.orientation_3d:
            details += f"  3D Orientation:\n"
            details += f"    Yaw (horizontal): {face.orientation_3d.yaw:.2f}°\n"
            details += f"    Pitch (vertical): {face.orientation_3d.pitch:.2f}°\n"
            details += f"    Roll (tilt): {face.orientation_3d.roll:.2f}°\n"
        details += "\n"
        
        details += f"Quality Metrics:\n"
        details += f"  Overall: {face.quality_metrics.overall_quality:.2f}\n"
        details += f"  Sharpness: {face.quality_metrics.sharpness:.2f}\n"
        details += f"  Brightness: {face.quality_metrics.brightness:.2f}\n"
        details += f"  Contrast: {face.quality_metrics.contrast:.2f}\n"
        details += f"  Detector Score: {face.quality_metrics.detector_score:.2f}\n"
        details += f"  Resolution: {face.quality_metrics.resolution[0]}x{face.quality_metrics.resolution[1]}\n\n"
        
        if face.metadata.character_id:
            details += f"Character ID: {face.metadata.character_id}\n"
        if face.metadata.tags:
            details += f"Tags: {', '.join(face.metadata.tags)}\n"
        details += f"Added: {face.metadata.added_date}\n"
        
        return details
    except Exception as e:
        return f"✗ Error: {str(e)}"


def remove_face_from_repository(face_id: str) -> str:
    """
    Remove a face from repository.
    
    Args:
        face_id: Face identifier
        
    Returns:
        Status message
    """
    try:
        if not face_id or not face_id.strip():
            return "Please enter a face ID"
        
        repo = RepositoryManager()
        if repo.remove_face(face_id.strip()):
            return f"✓ Face {face_id} removed successfully"
        else:
            return f"✗ Failed to remove face {face_id}"
    except Exception as e:
        return f"✗ Error: {str(e)}"


def add_character(name: str, description: Optional[str], tags: Optional[str]) -> str:
    """
    Add a new character.
    
    Args:
        name: Character name
        description: Character description
        tags: Comma-separated tags
        
    Returns:
        Status message
    """
    try:
        if not name or not name.strip():
            return "✗ Please enter a character name"
        
        # Parse tags
        tag_list = None
        if tags and tags.strip():
            tag_list = [t.strip() for t in tags.split(',')]
        
        char_mgr = CharacterManager()
        character = char_mgr.add_character(
            name=name.strip(),
            description=description.strip() if description and description.strip() else None,
            tags=tag_list
        )
        
        if character:
            msg = f"✓ Character added successfully!\n"
            msg += f"ID: {character.id}\n"
            msg += f"Name: {character.name}\n"
            if character.description:
                msg += f"Description: {character.description}\n"
            if character.tags:
                msg += f"Tags: {', '.join(character.tags)}\n"
            return msg
        else:
            return "✗ Failed to add character. Name may already exist."
    except Exception as e:
        return f"✗ Error: {str(e)}"


def list_characters() -> List[List[str]]:
    """
    List all characters.
    
    Returns:
        List of character data rows
    """
    try:
        char_mgr = CharacterManager()
        characters = char_mgr.list_characters()
        
        if not characters:
            return [["No characters found", "", "", "", ""]]
        
        # Get face counts
        repo = RepositoryManager()
        all_faces = repo.list_faces()
        
        result = []
        for char in characters:
            face_count = sum(1 for face in all_faces if face.metadata.character_id == char.id)
            
            result.append([
                char.id,
                char.name,
                str(face_count),
                char.description or "-",
                ', '.join(char.tags) if char.tags else "-"
            ])
        
        return result
    except Exception as e:
        return [[f"Error: {str(e)}", "", "", "", ""]]


def show_character_details(char_id: str) -> str:
    """
    Show detailed information about a character.
    
    Args:
        char_id: Character identifier
        
    Returns:
        Formatted character details
    """
    try:
        if not char_id or not char_id.strip():
            return "Please enter a character ID"
        
        char_mgr = CharacterManager()
        character = char_mgr.get_character(char_id.strip())
        
        if not character:
            return f"✗ Character not found: {char_id}"
        
        # Get associated faces
        repo = RepositoryManager()
        all_faces = repo.list_faces()
        char_faces = [face for face in all_faces if face.metadata.character_id == character.id]
        
        details = f"Character Details\n{'=' * 60}\n\n"
        details += f"ID: {character.id}\n"
        details += f"Name: {character.name}\n"
        if character.description:
            details += f"Description: {character.description}\n"
        if character.tags:
            details += f"Tags: {', '.join(character.tags)}\n"
        if character.created_date:
            details += f"Created: {character.created_date}\n"
        details += f"\nAssociated Faces: {len(char_faces)}\n"
        
        if char_faces:
            details += "\nFaces:\n"
            for face in char_faces:
                details += f"  • {face.id} ({face.metadata.name or 'Unnamed'})\n"
                details += f"    Orientation: {face.orientation_angle}°"
                if face.orientation_3d:
                    details += f" (Y:{face.orientation_3d.yaw:.1f}° P:{face.orientation_3d.pitch:.1f}° R:{face.orientation_3d.roll:.1f}°)"
                details += f", Quality: {face.quality_metrics.overall_quality:.2f}\n"
        
        return details
    except Exception as e:
        return f"✗ Error: {str(e)}"


def remove_character(char_id: str) -> str:
    """
    Remove a character.
    
    Args:
        char_id: Character identifier
        
    Returns:
        Status message
    """
    try:
        if not char_id or not char_id.strip():
            return "Please enter a character ID"
        
        char_mgr = CharacterManager()
        if char_mgr.remove_character(char_id.strip()):
            return f"✓ Character {char_id} removed successfully\nNote: Associated faces are NOT removed."
        else:
            return f"✗ Failed to remove character {char_id}"
    except Exception as e:
        return f"✗ Error: {str(e)}"


def get_repository_statistics() -> Tuple[str, str]:
    """
    Get repository statistics.
    
    Returns:
        Tuple of (statistics text, coverage HTML)
    """
    try:
        repo = RepositoryManager()
        stats = repo.get_statistics()
        
        stats_text = "Repository Statistics\n"
        stats_text += "=" * 60 + "\n\n"
        stats_text += f"Total Faces: {stats.total_faces}\n"
        stats_text += f"Average Quality: {stats.average_quality:.2f}\n"
        stats_text += f"Total Size: {stats.total_size_mb:.2f} MB\n"
        stats_text += f"Unique Names: {stats.unique_names}\n\n"
        
        stats_text += "Faces by Orientation:\n"
        for angle in sorted(stats.faces_by_orientation.keys()):
            count = stats.faces_by_orientation[angle]
            stats_text += f"  {angle}°: {count} face(s)\n"
        
        # Generate coverage visualization (simple text-based for now)
        coverage_html = "<div style='font-family: monospace; padding: 20px; background: #f0f0f0; border-radius: 5px;'>"
        coverage_html += "<h3>Orientation Coverage</h3>"
        coverage_html += "<pre>"
        
        standard_angles = [0, 45, 90, 135, 180, 225, 270, 315]
        for angle in standard_angles:
            count = stats.faces_by_orientation.get(angle, 0)
            bar = "█" * count if count > 0 else "░"
            coverage_html += f"{angle:3d}°: {bar} ({count})\n"
        
        coverage_html += "</pre></div>"
        
        return stats_text, coverage_html
    except Exception as e:
        return f"Error: {str(e)}", "<p>Error generating coverage</p>"
