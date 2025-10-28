"""
Batch execution engine for FaceFusion Repository System.
"""

# Import components individually to avoid circular imports during testing
from facefusion_repository.execution.error_handler import ErrorHandler
from facefusion_repository.execution.progress_tracker import ProgressTracker
from facefusion_repository.execution.queue_processor import QueueProcessor
from facefusion_repository.execution.result_manager import ResultManager
from facefusion_repository.execution.video_assembler import VideoAssembler

# Import batch executor last as it depends on other components
# Note: This may require FaceFusion dependencies to be installed
try:
    from facefusion_repository.execution.batch_executor import BatchExecutor
    from facefusion_repository.execution.facefusion_interface import FaceFusionInterface
    
    __all__ = [
        'BatchExecutor',
        'ErrorHandler',
        'FaceFusionInterface',
        'ProgressTracker',
        'QueueProcessor',
        'ResultManager',
        'VideoAssembler'
    ]
except ImportError:
    # If FaceFusion dependencies not available, only export core components
    __all__ = [
        'ErrorHandler',
        'ProgressTracker',
        'QueueProcessor',
        'ResultManager',
        'VideoAssembler'
    ]
