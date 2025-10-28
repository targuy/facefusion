"""
Interface layer for integrating with FaceFusion core processing.
"""

from typing import Any, Dict, List, Optional

import numpy

from facefusion import face_analyser, state_manager
from facefusion.processors.core import get_processors_modules
from facefusion.types import Face, VisionFrame
from facefusion.vision import read_static_image, write_image
from facefusion_repository.types import FaceEntry


class FaceFusionInterface:
    """
    Interface for calling FaceFusion processing functions.

    This class provides a clean interface to FaceFusion's face swapping
    capabilities without modifying the core FaceFusion code.
    """

    def __init__(self) -> None:
        """Initialize FaceFusion interface."""
        self._initialized = False
        self._source_face: Optional[Face] = None

    def initialize(self, settings: Optional[Dict[str, Any]] = None) -> bool:
        """
        Initialize FaceFusion with optional settings.

        Args:
            settings: Optional settings dictionary to apply

        Returns:
            True if initialization successful
        """
        try:
            # Apply settings if provided
            if settings:
                self._apply_settings(settings)

            # Initialize face analyser
            if not face_analyser.pre_check():
                print('Failed to initialize face analyser')
                return False

            self._initialized = True
            return True

        except Exception as e:
            print(f'Error initializing FaceFusion interface: {e}')
            return False

    def _apply_settings(self, settings: Dict[str, Any]) -> None:
        """
        Apply settings to FaceFusion state manager.

        Args:
            settings: Settings dictionary
        """
        for key, value in settings.items():
            if state_manager.has_item(key):
                state_manager.set_item(key, value)

    def load_source_face(self, face_entry: FaceEntry) -> bool:
        """
        Load source face from repository entry.

        Args:
            face_entry: FaceEntry object with face data

        Returns:
            True if face loaded successfully
        """
        try:
            # Read the source image
            vision_frame = read_static_image(face_entry.file_path)
            if vision_frame is None:
                print(f'Failed to read source image: {face_entry.file_path}')
                return False

            # Get face from the image using face analyser
            faces = face_analyser.get_many_faces([vision_frame])
            if not faces:
                print(f'No face detected in source image: {face_entry.file_path}')
                return False

            # Use the first face (should only be one)
            self._source_face = faces[0]

            # Update the face with the stored embedding if available
            if face_entry.face_embedding is not None:
                self._source_face.embedding = face_entry.face_embedding

            return True

        except Exception as e:
            print(f'Error loading source face: {e}')
            return False

    def process_frame(
        self,
        target_frame: VisionFrame,
        target_face: Optional[Face] = None
    ) -> Optional[VisionFrame]:
        """
        Process a single frame with face swap.

        Args:
            target_frame: Target video frame
            target_face: Optional specific target face to swap

        Returns:
            Processed frame, or None on error
        """
        if not self._initialized:
            print('FaceFusionInterface not initialized')
            return None

        if self._source_face is None:
            print('No source face loaded')
            return None

        try:
            # Get processor modules
            processor_modules = get_processors_modules(
                state_manager.get_item('processors')
            )

            if not processor_modules:
                print('No processors configured')
                return None

            # Process the frame with each processor
            processed_frame = target_frame.copy()

            for processor_module in processor_modules:
                # Call the processor's process_frame method
                processed_frame = processor_module.process_frame(
                    source_face=self._source_face,
                    target_vision_frame=processed_frame
                )

                if processed_frame is None:
                    print('Frame processing failed')
                    return None

            return processed_frame

        except Exception as e:
            print(f'Error processing frame: {e}')
            return None

    def swap_face_in_image(
        self,
        source_entry: FaceEntry,
        target_path: str,
        output_path: str,
        target_face: Optional[Face] = None
    ) -> bool:
        """
        Swap face in a single image.

        Args:
            source_entry: Source face entry from repository
            target_path: Path to target image
            output_path: Path to save output image
            target_face: Optional specific target face

        Returns:
            True if swap successful
        """
        try:
            # Load source face
            if not self.load_source_face(source_entry):
                return False

            # Read target image
            target_frame = read_static_image(target_path)
            if target_frame is None:
                print(f'Failed to read target image: {target_path}')
                return False

            # Process the frame
            processed_frame = self.process_frame(target_frame, target_face)
            if processed_frame is None:
                return False

            # Write output image
            return write_image(output_path, processed_frame)

        except Exception as e:
            print(f'Error swapping face in image: {e}')
            return False

    def get_faces_in_frame(self, vision_frame: VisionFrame) -> List[Face]:
        """
        Detect faces in a frame.

        Args:
            vision_frame: Frame to analyze

        Returns:
            List of detected faces
        """
        try:
            return face_analyser.get_many_faces([vision_frame])
        except Exception as e:
            print(f'Error detecting faces: {e}')
            return []

    def cleanup(self) -> None:
        """Cleanup and release resources."""
        self._source_face = None
        self._initialized = False

        # Clear inference pools if available
        try:
            processor_modules = get_processors_modules(
                state_manager.get_item('processors')
            )
            for processor_module in processor_modules:
                if hasattr(processor_module, 'clear_inference_pool'):
                    processor_module.clear_inference_pool()
        except Exception:
            pass  # Ignore cleanup errors
