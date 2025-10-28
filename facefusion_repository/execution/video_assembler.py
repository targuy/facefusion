"""
Video assembler for frame sequence reconstruction.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional

from facefusion import ffmpeg
from facefusion.types import VisionFrame
from facefusion.vision import write_image


class VideoAssembler:
    """
    Assembles processed video frames into output video.

    Handles frame sequencing, timecode preservation, and audio track handling.
    """

    def __init__(self, temp_dir: Optional[str] = None) -> None:
        """
        Initialize video assembler.

        Args:
            temp_dir: Temporary directory for frame storage. If None, uses default.
        """
        if temp_dir is None:
            temp_dir = os.path.expanduser('~/.facefusion_repository/temp')

        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def save_frame(
        self,
        frame: VisionFrame,
        frame_number: int,
        video_id: str
    ) -> Optional[str]:
        """
        Save a processed frame to temporary storage.

        Args:
            frame: Processed video frame
            frame_number: Frame number in video sequence
            video_id: Unique identifier for the video

        Returns:
            Path to saved frame, or None on error
        """
        try:
            # Create video-specific temp directory
            video_temp_dir = self.temp_dir / video_id
            video_temp_dir.mkdir(parents=True, exist_ok=True)

            # Generate frame filename with zero-padding
            frame_filename = f'frame_{frame_number:08d}.png'
            frame_path = video_temp_dir / frame_filename

            # Write frame to disk
            if write_image(str(frame_path), frame):
                return str(frame_path)
            else:
                print(f'Failed to write frame {frame_number}')
                return None

        except Exception as e:
            print(f'Error saving frame {frame_number}: {e}')
            return None

    def assemble_video(
        self,
        video_id: str,
        output_path: str,
        source_video_path: Optional[str] = None,
        fps: float = 30.0,
        preserve_audio: bool = True
    ) -> bool:
        """
        Assemble frames into output video.

        Args:
            video_id: Unique identifier for the video
            output_path: Path to save output video
            source_video_path: Optional source video for audio/metadata
            fps: Frames per second for output video
            preserve_audio: Whether to preserve audio from source video

        Returns:
            True if assembly successful
        """
        try:
            video_temp_dir = self.temp_dir / video_id

            if not video_temp_dir.exists():
                print(f'No frames found for video ID: {video_id}')
                return False

            # Get list of frame files
            frame_files = sorted(video_temp_dir.glob('frame_*.png'))
            if not frame_files:
                print(f'No frame files found in {video_temp_dir}')
                return False

            # Use FaceFusion's ffmpeg module to merge frames
            # This preserves compatibility with FaceFusion's video handling
            temp_video_path = str(video_temp_dir / 'temp_output.mp4')

            # Create frame pattern path
            frame_pattern = str(video_temp_dir / 'frame_%08d.png')

            # Use ffmpeg to create video from frames
            success = self._create_video_from_frames(
                frame_pattern,
                temp_video_path,
                fps
            )

            if not success:
                print('Failed to create video from frames')
                return False

            # If source video provided and audio preservation requested
            if source_video_path and preserve_audio and os.path.exists(source_video_path):
                # Copy audio from source to output
                if ffmpeg.replace_audio(temp_video_path, source_video_path, output_path):
                    # Clean up temp video
                    if os.path.exists(temp_video_path):
                        os.remove(temp_video_path)
                    return True
                else:
                    # If audio replacement fails, use video without audio
                    print('Failed to preserve audio, using video without audio')
                    if os.path.exists(temp_video_path):
                        os.rename(temp_video_path, output_path)
                    return True
            else:
                # No audio preservation, just move the video
                if os.path.exists(temp_video_path):
                    os.rename(temp_video_path, output_path)
                return True

        except Exception as e:
            print(f'Error assembling video: {e}')
            return False

    def _create_video_from_frames(
        self,
        frame_pattern: str,
        output_path: str,
        fps: float
    ) -> bool:
        """
        Create video from frame pattern using ffmpeg.

        Args:
            frame_pattern: Path pattern for frames (e.g., 'frame_%08d.png')
            output_path: Path to save output video
            fps: Frames per second

        Returns:
            True if successful
        """
        try:
            # Build ffmpeg command
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output file
                '-framerate', str(fps),
                '-i', frame_pattern,
                '-c:v', 'libx264',  # H.264 codec
                '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
                '-crf', '23',  # Quality (lower is better, 23 is default)
                '-preset', 'medium',  # Encoding speed vs compression
                output_path
            ]

            # Run ffmpeg
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                print(f'FFmpeg error: {result.stderr}')
                return False

            return os.path.exists(output_path)

        except Exception as e:
            print(f'Error creating video from frames: {e}')
            return False

    def cleanup_frames(self, video_id: str) -> bool:
        """
        Clean up temporary frames for a video.

        Args:
            video_id: Unique identifier for the video

        Returns:
            True if cleanup successful
        """
        try:
            video_temp_dir = self.temp_dir / video_id

            if video_temp_dir.exists():
                # Remove all files in the directory
                for file_path in video_temp_dir.iterdir():
                    if file_path.is_file():
                        file_path.unlink()

                # Remove the directory
                video_temp_dir.rmdir()

            return True

        except Exception as e:
            print(f'Error cleaning up frames: {e}')
            return False

    def cleanup_all(self) -> bool:
        """
        Clean up all temporary files.

        Returns:
            True if cleanup successful
        """
        try:
            if self.temp_dir.exists():
                # Remove all subdirectories
                for video_dir in self.temp_dir.iterdir():
                    if video_dir.is_dir():
                        self.cleanup_frames(video_dir.name)

            return True

        except Exception as e:
            print(f'Error cleaning up all frames: {e}')
            return False

    def get_frame_count(self, video_id: str) -> int:
        """
        Get number of frames saved for a video.

        Args:
            video_id: Unique identifier for the video

        Returns:
            Number of frames
        """
        video_temp_dir = self.temp_dir / video_id

        if not video_temp_dir.exists():
            return 0

        return len(list(video_temp_dir.glob('frame_*.png')))
