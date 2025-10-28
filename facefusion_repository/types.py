"""Type definitions for FaceFusion Repository System"""

from typing import Any, Dict, List, Literal, Optional, TypeAlias, TypedDict

import numpy
from numpy.typing import NDArray


# Basic Types
FaceId : TypeAlias = str
PersonId : TypeAlias = str
Score : TypeAlias = float
Angle : TypeAlias = float

# 3D Pose Analysis
Pose3D = TypedDict('Pose3D',
{
	'yaw': Angle,
	'pitch': Angle,
	'roll': Angle,
	'confidence': Score
})

# Face Quality Metrics
QualityMetrics = TypedDict('QualityMetrics',
{
	'sharpness': Score,
	'brightness': Score,
	'overall_quality': Score,
	'has_occlusion': bool
})

# Person Face Entry
PersonFace = TypedDict('PersonFace',
{
	'face_id': FaceId,
	'person_id': PersonId,
	'image_path': str,
	'face_path': str,
	'pose_3d': Pose3D,
	'quality': QualityMetrics,
	'embedding': NDArray[numpy.float64],
	'added_date': str,
	'tags': List[str]
})

# Repository Entry
RepositoryEntry = TypedDict('RepositoryEntry',
{
	'person_id': PersonId,
	'person_name': str,
	'faces': List[PersonFace],
	'created_date': str,
	'modified_date': str
})

# Repository Database
RepositoryDatabase = TypedDict('RepositoryDatabase',
{
	'version': str,
	'persons': List[RepositoryEntry]
})

# Preset Configuration
PresetConfig = TypedDict('PresetConfig',
{
	'preset_id': str,
	'preset_name': str,
	'person_id': PersonId,
	'face_id': Optional[FaceId],
	'processors': List[str],
	'settings': Dict[str, Any]
})

# Repository Status
RepositoryStatus = Literal['initialized', 'empty', 'not_found']

# Operation Results
OperationResult = TypedDict('OperationResult',
{
	'success': bool,
	'message': str,
	'data': Optional[Dict[str, Any]]
})
