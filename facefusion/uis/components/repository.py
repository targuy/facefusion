"""Repository UI component for person management."""

from typing import Any, List, Optional, Tuple

import gradio

from facefusion import state_manager
from facefusion.uis.core import register_ui_component
from facefusion.uis.types import File

REPOSITORY_PERSON_NAME: Optional[gradio.Textbox] = None
REPOSITORY_FACE_FILES: Optional[gradio.File] = None
REPOSITORY_PERSON_SELECT: Optional[gradio.Dropdown] = None
REPOSITORY_STATUS: Optional[gradio.Textbox] = None
REPOSITORY_PERSON_LIST: Optional[gradio.Textbox] = None
REPOSITORY_FACE_GALLERY: Optional[gradio.Gallery] = None
REPOSITORY_COVERAGE_STATS: Optional[gradio.Textbox] = None

# Preview Modal components
PREVIEW_MODAL: Optional[gradio.Column] = None
PREVIEW_RESULTS: Optional[gradio.HTML] = None
PREVIEW_GALLERY: Optional[gradio.Gallery] = None
PREVIEW_CONFIRM_BTN: Optional[gradio.Button] = None
PREVIEW_CANCEL_BTN: Optional[gradio.Button] = None

# 3D Visualization components
COVERAGE_3D_MODAL: Optional[gradio.Column] = None
COVERAGE_3D_PLOT: Optional[gradio.Plot] = None
COVERAGE_3D_CLOSE_BTN: Optional[gradio.Button] = None

# Test Swap Preview components
TEST_SWAP_MODAL: Optional[gradio.Column] = None
TEST_SWAP_IMAGE: Optional[gradio.Image] = None
TEST_SWAP_INFO: Optional[gradio.HTML] = None
TEST_SWAP_CLOSE_BTN: Optional[gradio.Button] = None


def render() -> None:
	global REPOSITORY_PERSON_NAME
	global REPOSITORY_FACE_FILES
	global REPOSITORY_PERSON_SELECT
	global REPOSITORY_STATUS
	global REPOSITORY_PERSON_LIST
	global REPOSITORY_FACE_GALLERY
	global REPOSITORY_COVERAGE_STATS
	global PREVIEW_MODAL
	global PREVIEW_RESULTS
	global PREVIEW_GALLERY
	global PREVIEW_CONFIRM_BTN
	global PREVIEW_CANCEL_BTN
	global COVERAGE_3D_MODAL
	global COVERAGE_3D_PLOT
	global COVERAGE_3D_CLOSE_BTN
	global TEST_SWAP_MODAL
	global TEST_SWAP_IMAGE
	global TEST_SWAP_INFO
	global TEST_SWAP_CLOSE_BTN

	with gradio.Accordion('Repository', open=True):
		# === SECTION 1: Import & Crop Preview ===
		gradio.Markdown('### 📥 Import Faces to Repository')
		
		with gradio.Row():
			with gradio.Column(scale=2):
				REPOSITORY_PERSON_NAME = gradio.Textbox(
					label='New Person Name (or leave empty to add to existing)',
					placeholder='Enter new person name or leave empty...'
				)
			with gradio.Column(scale=1):
				gradio.Markdown('<br>')  # Spacing
				use_existing_checkbox = gradio.Checkbox(
					label='Add to existing person',
					value=False
				)
		
		REPOSITORY_FACE_FILES = gradio.File(
			label='Upload Face Images',
			file_count='multiple',
			file_types=['image']
		)
		preview_button = gradio.Button('🔍 Preview Detected Faces', variant='primary', size='lg')
		
		gradio.Markdown('---')
		
		# === SECTION 2: Manage Repository ===
		gradio.Markdown('### 📚 Repository Management')
		
		REPOSITORY_PERSON_SELECT = gradio.Dropdown(
			label='Select Person',
			choices=_get_person_names(),
			value=state_manager.get_item('repository_person_name') if state_manager.get_item('repository_person_name') else None
		)
		with gradio.Row():
			refresh_button = gradio.Button('🔄 Refresh', variant='secondary')
			delete_button = gradio.Button('🗑️ Delete Person', variant='stop')
		
		gradio.Markdown('---')
		
		# === SECTION 3: Person Details ===
		gradio.Markdown('### 👤 Selected Person Details')
		
		REPOSITORY_PERSON_LIST = gradio.Textbox(
			label='All Persons in Repository',
			value=_format_person_list(),
			interactive=False,
			lines=3
		)
		
		REPOSITORY_FACE_GALLERY = gradio.Gallery(
			label='Face Gallery',
			show_label=True,
			columns=4,
			rows=2,
			height=300,
			object_fit='cover',
			value=[]
		)
		
		REPOSITORY_COVERAGE_STATS = gradio.Textbox(
			label='Orientation Coverage',
			value='No person selected',
			interactive=False,
			lines=2
		)
		
		with gradio.Row():
			view_3d_button = gradio.Button('🌐 3D Coverage', variant='secondary')
			test_swap_button = gradio.Button('� Test Swap Quality', variant='primary')
		
		gradio.Markdown('---')
		
		# === SECTION 4: Status ===
		REPOSITORY_STATUS = gradio.Textbox(
			label='Status',
			value='Ready',
			interactive=False,
			lines=2
		)
	
	# Preview Modal - Show cropped faces with accept/reject
	with gradio.Column(visible=False) as PREVIEW_MODAL:
		gradio.Markdown('## 🔍 Detected Faces - Review Before Adding')
		PREVIEW_RESULTS = gradio.HTML(value='<p>Analyzing faces...</p>')
		PREVIEW_GALLERY = gradio.Gallery(
			label='Detected & Cropped Faces',
			columns=3,
			rows=2,
			height=400,
			object_fit='contain',
			value=[]
		)
		with gradio.Row():
			PREVIEW_CANCEL_BTN = gradio.Button('❌ Cancel', variant='secondary', size='lg')
			PREVIEW_CONFIRM_BTN = gradio.Button('✅ Add to Repository', variant='primary', size='lg')
	
	# 3D Visualization Modal
	with gradio.Column(visible=False) as COVERAGE_3D_MODAL:
		gradio.Markdown('## 🌐 3D Orientation Coverage')
		COVERAGE_3D_PLOT = gradio.Plot()
		COVERAGE_3D_CLOSE_BTN = gradio.Button('Close', variant='secondary')
	
	# Test Swap Modal
	with gradio.Column(visible=False) as TEST_SWAP_MODAL:
		gradio.Markdown('## 👁️ Preview Face Swap')
		TEST_SWAP_IMAGE = gradio.Image(label='Swap Preview', type='numpy')
		TEST_SWAP_INFO = gradio.HTML(value='')
		TEST_SWAP_CLOSE_BTN = gradio.Button('Close', variant='secondary')
	
	# Connect buttons
	preview_button.click(
		fn=show_preview,
		inputs=[REPOSITORY_PERSON_NAME, REPOSITORY_FACE_FILES],
		outputs=[PREVIEW_MODAL, PREVIEW_RESULTS, PREVIEW_GALLERY]
	)
	
	PREVIEW_CONFIRM_BTN.click(
		fn=confirm_add_person,
		inputs=[REPOSITORY_PERSON_NAME, REPOSITORY_FACE_FILES],
		outputs=[REPOSITORY_STATUS, REPOSITORY_PERSON_LIST, REPOSITORY_PERSON_SELECT, REPOSITORY_FACE_GALLERY, REPOSITORY_COVERAGE_STATS, PREVIEW_MODAL]
	)
	
	PREVIEW_CANCEL_BTN.click(
		fn=lambda: gradio.update(visible=False),
		outputs=PREVIEW_MODAL
	)
	
	view_3d_button.click(
		fn=show_3d_coverage,
		inputs=REPOSITORY_PERSON_SELECT,
		outputs=[COVERAGE_3D_MODAL, COVERAGE_3D_PLOT]
	)
	
	COVERAGE_3D_CLOSE_BTN.click(
		fn=lambda: gradio.update(visible=False),
		outputs=COVERAGE_3D_MODAL
	)
	
	test_swap_button.click(
		fn=show_test_swap,
		inputs=REPOSITORY_PERSON_SELECT,
		outputs=[TEST_SWAP_MODAL, TEST_SWAP_IMAGE, TEST_SWAP_INFO]
	)
	
	TEST_SWAP_CLOSE_BTN.click(
		fn=lambda: gradio.update(visible=False),
		outputs=TEST_SWAP_MODAL
	)
	
	delete_button.click(
		fn=delete_person,
		inputs=[REPOSITORY_PERSON_SELECT],
		outputs=[REPOSITORY_STATUS, REPOSITORY_PERSON_LIST, REPOSITORY_PERSON_SELECT]
	)
	
	refresh_button.click(
		fn=refresh_persons,
		outputs=[REPOSITORY_PERSON_SELECT, REPOSITORY_PERSON_LIST]
	)
	
	register_ui_component('repository_person_select', REPOSITORY_PERSON_SELECT)
	register_ui_component('repository_status', REPOSITORY_STATUS)


def listen() -> None:
	REPOSITORY_PERSON_SELECT.change(
		update_selected_person_ui,
		inputs=REPOSITORY_PERSON_SELECT,
		outputs=[REPOSITORY_FACE_GALLERY, REPOSITORY_COVERAGE_STATS]
	)


def _get_repository_manager(): # type: ignore[no-untyped-def]
	"""Get repository manager instance."""
	from facefusion_repository.manager import RepositoryManager
	repository_path = state_manager.get_item('repository_path') or '.face_repository'
	return RepositoryManager(repository_path)


def _get_person_names() -> List[str]:
	"""Get list of person names from repository."""
	try:
		manager = _get_repository_manager()
		persons = manager.list_persons()
		return [person['display_name'] for person in persons]
	except Exception:
		return []


def _format_person_list() -> str:
	"""Format person list for display."""
	try:
		manager = _get_repository_manager()
		persons = manager.list_persons()
		if not persons:
			return 'No persons in repository'
		
		lines = []
		for person in persons:
			lines.append(f"• {person['display_name']} ({person['face_count']} faces)")
		return '\n'.join(lines)
	except Exception as e:
		return f'Error: {str(e)}'


def show_preview(person_name: str, files: List[File]) -> Tuple:
	"""Crop and show detected faces for review before adding to repository."""
	
	if not person_name or not files:
		return gradio.update(visible=False), '<p>Please enter a person name and upload images.</p>', []
	
	try:
		from facefusion import vision, face_detector
		
		file_paths = [file.name for file in files]
		cropped_faces = []
		detection_info = []
		
		total_files = len(files)
		total_faces = 0
		
		for i, file_path in enumerate(file_paths):
			filename = file_path.split("/")[-1]
			
			# Read image
			frame = vision.read_static_image(file_path)
			if frame is None:
				detection_info.append(f'❌ {filename}: Could not read image')
				continue
			
			# Detect faces - returns (bounding_boxes, scores, landmarks_5)
			bboxes, scores, landmarks = face_detector.detect_faces(frame)
			
			if not bboxes or len(bboxes) == 0:
				detection_info.append(f'❌ {filename}: No face detected')
				continue
			
			# Process each detected face (usually 1 per image)
			for j, bbox in enumerate(bboxes):
				# Extract bounding box coordinates
				x1, y1, x2, y2 = map(int, bbox)
				
				# Add some margin (10%)
				height, width = frame.shape[:2]
				margin_x = int((x2 - x1) * 0.1)
				margin_y = int((y2 - y1) * 0.1)
				
				x1 = max(0, x1 - margin_x)
				y1 = max(0, y1 - margin_y)
				x2 = min(width, x2 + margin_x)
				y2 = min(height, y2 + margin_y)
				
				# Crop face
				face_crop = frame[y1:y2, x1:x2]
				
				if face_crop.size > 0:
					cropped_faces.append(face_crop)
					total_faces += 1
					score = scores[j] if j < len(scores) else 0.0
					detection_info.append(f'✅ {filename}: Face {j+1} detected (confidence: {score:.2f})')
		
		# Generate summary HTML
		results_html = f'<div style="padding: 15px; background: #f8f9fa; border-radius: 8px;">'
		results_html += f'<h3 style="color: #2c3e50;">👤 Person: {person_name}</h3>'
		results_html += f'<p><strong>Files processed:</strong> {total_files}</p>'
		results_html += f'<p><strong>Faces detected:</strong> {total_faces}</p>'
		results_html += '<hr>'
		
		if detection_info:
			results_html += '<div style="max-height: 200px; overflow-y: auto; padding: 10px; background: white; border-radius: 4px;">'
			for info in detection_info:
				color = '#28a745' if '✅' in info else '#dc3545'
				results_html += f'<p style="margin: 5px 0; color: {color};">{info}</p>'
			results_html += '</div>'
		
		results_html += '</div>'
		
		if total_faces == 0:
			results_html += '<p style="color: red; margin-top: 10px;"><strong>⚠️ No faces detected. Please upload images with clear faces.</strong></p>'
		else:
			results_html += f'<p style="color: green; margin-top: 10px;"><strong>Review the cropped faces below and click "✅ Add to Repository" to confirm.</strong></p>'
		
		return gradio.update(visible=True), results_html, cropped_faces
		
	except Exception as e:
		import traceback
		error_html = f'<div style="padding: 15px; background: #fee; border-radius: 8px;">'
		error_html += f'<h3 style="color: #d32f2f;">❌ Error</h3>'
		error_html += f'<p>{str(e)}</p>'
		error_html += f'<details><summary>Technical Details</summary><pre>{traceback.format_exc()}</pre></details>'
		error_html += '</div>'
		return gradio.update(visible=True), error_html, []


def confirm_add_person(person_name: str, files: List[File]) -> Tuple:
	"""Confirm and add person after preview."""
	status, person_list, dropdown, gallery, coverage_stats = add_person(person_name, files)
	return status, person_list, dropdown, gallery, coverage_stats, gradio.update(visible=False)


def show_3d_coverage(person_name: Optional[str]) -> Tuple:
	"""Show 3D coverage visualization for a person."""
	if not person_name:
		import plotly.graph_objects as go
		empty_fig = go.Figure()
		empty_fig.add_annotation(text="No person selected", showarrow=False)
		return gradio.update(visible=False), empty_fig
	
	try:
		import plotly.graph_objects as go
		import numpy as np
		
		manager = _get_repository_manager()
		person = manager.get_person_by_normalized_name(person_name)
		
		if not person:
			empty_fig = go.Figure()
			empty_fig.add_annotation(text=f"Person '{person_name}' not found", showarrow=False)
			return gradio.update(visible=False), empty_fig
		
		# Extract orientations from face metadata
		face_metadata = person.get('face_metadata', {})
		orientations = []
		qualities = []
		
		for face_path, metadata in face_metadata.items():
			pose = metadata.get('pose')
			quality = metadata.get('quality', {}).get('overall', 0.5)
			if pose:
				orientations.append(pose)
				qualities.append(quality)
		
		if not orientations:
			empty_fig = go.Figure()
			empty_fig.add_annotation(text="No orientation data available", showarrow=False)
			return gradio.update(visible=True), empty_fig
		
		# Convert orientations to 3D coordinates
		def orientation_to_xyz(pitch: float, yaw: float) -> Tuple[float, float, float]:
			"""Convert pitch/yaw to 3D sphere coordinates."""
			pitch_rad = np.radians(pitch)
			yaw_rad = np.radians(yaw)
			x = np.cos(pitch_rad) * np.sin(yaw_rad)
			y = np.cos(pitch_rad) * np.cos(yaw_rad)
			z = np.sin(pitch_rad)
			return x, y, z
		
		# Plot faces on sphere
		x_coords, y_coords, z_coords = [], [], []
		hover_texts = []
		colors = []
		
		for orientation, quality in zip(orientations, qualities):
			x, y, z = orientation_to_xyz(orientation['pitch'], orientation['yaw'])
			x_coords.append(x)
			y_coords.append(y)
			z_coords.append(z)
			hover_texts.append(
				f"Pitch: {orientation['pitch']:.1f}°<br>"
				f"Yaw: {orientation['yaw']:.1f}°<br>"
				f"Roll: {orientation['roll']:.1f}°<br>"
				f"Quality: {quality:.2f}"
			)
			colors.append(quality)
		
		# Create 3D sphere surface
		u = np.linspace(0, 2 * np.pi, 50)
		v = np.linspace(0, np.pi, 50)
		x_sphere = np.outer(np.cos(u), np.sin(v))
		y_sphere = np.outer(np.sin(u), np.sin(v))
		z_sphere = np.outer(np.ones(np.size(u)), np.cos(v))
		
		fig = go.Figure()
		
		# Add semi-transparent sphere
		fig.add_trace(go.Surface(
			x=x_sphere, y=y_sphere, z=z_sphere,
			opacity=0.1,
			colorscale='Greys',
			showscale=False,
			hoverinfo='skip'
		))
		
		# Add face points
		fig.add_trace(go.Scatter3d(
			x=x_coords, y=y_coords, z=z_coords,
			mode='markers',
			marker=dict(
				size=10,
				color=colors,
				colorscale='RdYlGn',
				colorbar=dict(title='Quality'),
				showscale=True,
				cmin=0,
				cmax=1
			),
			text=hover_texts,
			hoverinfo='text',
			name='Faces'
		))
		
		fig.update_layout(
			title=f'3D Orientation Coverage - {person_name}',
			scene=dict(
				xaxis=dict(title='X (Yaw)'),
				yaxis=dict(title='Y'),
				zaxis=dict(title='Z (Pitch)'),
				aspectmode='cube'
			),
			width=800,
			height=600
		)
		
		return gradio.update(visible=True), fig
		
	except ImportError:
		empty_fig = go.Figure()
		empty_fig.add_annotation(text="Plotly not installed. Run: pip install plotly", showarrow=False)
		return gradio.update(visible=True), empty_fig
	except Exception as e:
		import plotly.graph_objects as go
		import traceback
		error_msg = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
		empty_fig = go.Figure()
		empty_fig.add_annotation(text=error_msg, showarrow=False, font=dict(size=10))
		return gradio.update(visible=True), empty_fig


def show_test_swap(person_name: Optional[str]) -> Tuple:
	"""Test swap quality by showing how repository faces match test images."""
	
	if not person_name:
		info_html = '<div style="padding: 15px; background: #fff3cd; border-radius: 8px;">'
		info_html += '<h3>⚠️ No Person Selected</h3>'
		info_html += '<p>Please select a person from the repository to test swap quality.</p>'
		info_html += '</div>'
		return gradio.update(visible=True), None, info_html
	
	try:
		from facefusion import vision, face_detector
		from facefusion_repository.test_faces import get_test_faces
		
		manager = _get_repository_manager()
		person = manager.get_person_by_normalized_name(person_name)
		
		if not person or not person['face_paths']:
			info_html = f'<p style="color: red;">❌ Person "{person_name}" has no faces in repository.</p>'
			return gradio.update(visible=True), None, info_html
		
		# Get best quality face from repository
		face_metadata = person.get('face_metadata', {})
		best_face_path = None
		best_quality = -1.0
		
		for face_path in person['face_paths']:
			metadata = face_metadata.get(face_path, {})
			quality = metadata.get('quality', {}).get('overall', 0.5)
			if quality > best_quality:
				best_quality = quality
				best_face_path = face_path
		
		if not best_face_path:
			best_face_path = person['face_paths'][0]
		
		# Get test face images
		test_faces = get_test_faces()
		
		if not test_faces:
			info_html = '<p style="color: orange;">⚠️ No test faces found. Please add test images to the "test_faces" directory.</p>'
			info_html += '<p>Create a folder named "test_faces" in the project root and add face images there.</p>'
			return gradio.update(visible=True), None, info_html
		
		# Use the first test face as target
		target_image_path = test_faces[0]
		
		# Read source and target images
		source_frame = vision.read_static_image(best_face_path)
		target_frame = vision.read_static_image(target_image_path)
		
		if source_frame is None or target_frame is None:
			info_html = '<p style="color: red;">❌ Error reading source or target images.</p>'
			return gradio.update(visible=True), None, info_html
		
		# Detect faces - returns (bounding_boxes, scores, landmarks_5)
		source_bboxes, source_scores, source_landmarks = face_detector.detect_faces(source_frame)
		target_bboxes, target_scores, target_landmarks = face_detector.detect_faces(target_frame)
		
		if not source_bboxes or len(source_bboxes) == 0:
			info_html = '<p style="color: red;">❌ No face detected in repository image.</p>'
			return gradio.update(visible=True), None, info_html
		
		if not target_bboxes or len(target_bboxes) == 0:
			info_html = '<p style="color: red;">❌ No face detected in test image.</p>'
			return gradio.update(visible=True), None, info_html
		
		# Build comprehensive info HTML
		info_html = '<div style="padding: 15px; background: #e3f2fd; border-radius: 8px;">'
		info_html += f'<h3 style="color: #1976d2;">🔄 Swap Quality Test: {person_name}</h3>'
		info_html += '<hr>'
		
		# Person info
		info_html += '<div style="background: white; padding: 10px; border-radius: 4px; margin-bottom: 10px;">'
		info_html += f'<p><strong>Repository:</strong> {len(person["face_paths"])} face(s) stored</p>'
		info_html += f'<p><strong>Best quality:</strong> {best_quality:.2f}</p>'
		
		# Orientation coverage if available
		face_metadata = person.get('face_metadata', {})
		orientations = [m.get('pose') for m in face_metadata.values() if m.get('pose')]
		if orientations:
			info_html += f'<p><strong>Orientations:</strong> {len(orientations)} face(s) with orientation data</p>'
		else:
			info_html += '<p style="color: orange;"><strong>⚠️ No orientation data</strong> - consider re-importing faces</p>'
		
		info_html += '</div>'
		
		# Test image info
		info_html += '<div style="background: white; padding: 10px; border-radius: 4px; margin-bottom: 10px;">'
		info_html += f'<p><strong>Test image:</strong> {target_image_path.split("/")[-1]}</p>'
		info_html += f'<p><strong>Faces detected:</strong> {len(target_bboxes)} in test, {len(source_bboxes)} in repository</p>'
		
		if len(target_bboxes) > 1:
			info_html += '<p style="color: orange;">⚠️ Multiple faces in test image - using first detected</p>'
		
		info_html += '</div>'
		
		# Instructions
		info_html += '<div style="background: #fff9c4; padding: 10px; border-radius: 4px;">'
		info_html += '<p><strong>📌 To perform actual swaps:</strong></p>'
		info_html += '<ol style="margin: 5px 0; padding-left: 20px;">'
		info_html += '<li>Go to main FaceFusion tab</li>'
		info_html += '<li>Your repository person is automatically available</li>'
		info_html += '<li>Upload target and run swap</li>'
		info_html += '</ol>'
		info_html += '<p style="margin-top: 10px;"><em>This preview helps you verify detection quality before running full swaps.</em></p>'
		info_html += '</div>'
		
		info_html += '</div>'
		
		# Show the repository face as preview
		result_frame = source_frame
		
		return gradio.update(visible=True), result_frame, info_html
		
	except Exception as e:
		import traceback
		error_details = traceback.format_exc()
		info_html = f'<p style="color: red;">❌ Error during face swap: {str(e)}</p>'
		info_html += f'<details><summary>Details</summary><pre>{error_details}</pre></details>'
		return gradio.update(visible=True), None, info_html


def add_person(person_name: str, files: List[File]) -> Tuple[str, str, gradio.Dropdown, gradio.Gallery, str]:
	"""Add a person to the repository or add faces to existing person."""
	empty_gallery = gradio.Gallery(value=[])
	empty_stats = 'No person selected'
	
	if not person_name:
		return '❌ Error: Person name is required', _format_person_list(), gradio.Dropdown(choices=_get_person_names()), empty_gallery, empty_stats
	
	if not files:
		return '❌ Error: At least one face image is required', _format_person_list(), gradio.Dropdown(choices=_get_person_names()), empty_gallery, empty_stats
	
	try:
		manager = _get_repository_manager()
		file_paths = [file.name for file in files]
		
		# Get initial face count if person exists
		existing_person = manager.get_person_by_normalized_name(person_name)
		initial_face_count = existing_person['face_count'] if existing_person else 0
		
		# Use create_or_update_person (auto-detects if person exists)
		person = manager.create_or_update_person(person_name, file_paths)
		
		# Calculate results
		final_face_count = person['face_count']
		faces_added = final_face_count - initial_face_count
		files_uploaded = len(files)
		faces_skipped = files_uploaded - faces_added
		
		# Build status message with detailed feedback
		if faces_skipped > 0:
			status = f"✅ Added {faces_added}/{files_uploaded} faces to '{person_name}' "
			status += f"({faces_skipped} skipped: low quality or duplicate orientation)"
		else:
			status = f"✅ Successfully added {faces_added} face(s) to '{person_name}'"
		
		person_list = _format_person_list()
		person_names = _get_person_names()
		
		# Update gallery and stats for the person that was just updated
		gallery = gradio.Gallery(value=person['face_paths'])
		coverage_stats = _format_coverage_stats(person_name)
		
		return status, person_list, gradio.Dropdown(choices=person_names), gallery, coverage_stats
	except ValueError as e:
		# Handle validation errors
		return f'❌ Error: {str(e)}', _format_person_list(), gradio.Dropdown(choices=_get_person_names()), empty_gallery, empty_stats
	except Exception as e:
		return f'❌ Error: {str(e)}', _format_person_list(), gradio.Dropdown(choices=_get_person_names()), empty_gallery, empty_stats


def refresh_persons() -> Tuple[gradio.Dropdown, str]:
	"""Refresh the person list."""
	person_names = _get_person_names()
	person_list = _format_person_list()
	return gradio.Dropdown(choices=person_names), person_list


def delete_person(person_name: Optional[str]) -> Tuple[str, str, gradio.Dropdown]:
	"""Delete a person from the repository."""
	if not person_name:
		return '❌ Error: Please select a person to delete', _format_person_list(), gradio.Dropdown(choices=_get_person_names())
	
	try:
		manager = _get_repository_manager()
		person = manager.get_person_by_normalized_name(person_name)
		
		if not person:
			return f'❌ Error: Person "{person_name}" not found', _format_person_list(), gradio.Dropdown(choices=_get_person_names())
		
		# Remove person
		success = manager.remove_person(person['person_id'])
		
		if success:
			# Clear selection if deleted person was selected
			if state_manager.get_item('repository_person_name') == person_name:
				state_manager.set_item('repository_mode', False)
				state_manager.set_item('repository_person_id', '')
				state_manager.set_item('repository_person_name', '')
				state_manager.set_item('repository_source_faces', [])
			
			status = f"✅ Successfully deleted '{person_name}'"
			person_list = _format_person_list()
			person_names = _get_person_names()
			return status, person_list, gradio.Dropdown(choices=person_names, value=None)
		else:
			return f'❌ Error: Failed to delete "{person_name}"', _format_person_list(), gradio.Dropdown(choices=_get_person_names())
	except Exception as e:
		return f'❌ Error: {str(e)}', _format_person_list(), gradio.Dropdown(choices=_get_person_names())


def update_selected_person(person_name: Optional[str]) -> List[str]:
	"""
	Update the selected person in state.
	
	Note: Does NOT clear source_paths to allow direct upload to have priority.
	If user has both direct upload AND repository selection, direct upload wins.
	
	Returns:
		List of face image paths for gallery display
	"""
	if person_name:
		# Activate repository mode
		state_manager.set_item('repository_mode', True)
		state_manager.set_item('repository_person_name', person_name)
		
		# Get face paths for this person
		manager = _get_repository_manager()
		person = manager.get_person_by_normalized_name(person_name)
		if person:
			state_manager.set_item('repository_person_id', person['person_id'])
			state_manager.set_item('repository_source_faces', person['face_paths'])
			# NOTE: We do NOT clear source_paths here!
			# If user has uploaded faces directly, they should have priority
			# The repository_helper.get_effective_source_paths() handles priority
			return person['face_paths']
	else:
		# Deactivate repository mode
		state_manager.set_item('repository_mode', False)
		state_manager.set_item('repository_person_id', '')
		state_manager.set_item('repository_person_name', '')
		state_manager.set_item('repository_source_faces', [])
	
	return []


def update_selected_person_ui(person_name: Optional[str]) -> Tuple[gradio.Gallery, str]:
	"""Update UI when person selection changes."""
	face_paths = update_selected_person(person_name)
	coverage_stats = _format_coverage_stats(person_name)
	return gradio.Gallery(value=face_paths), coverage_stats


def _format_coverage_stats(person_name: Optional[str]) -> str:
	"""Format coverage statistics for display."""
	if not person_name:
		return 'No person selected'
	
	try:
		manager = _get_repository_manager()
		person = manager.get_person_by_normalized_name(person_name)
		if not person:
			return 'Person not found'
		
		stats = manager.calculate_coverage_stats(person['person_id'])
		
		if not stats.get('success'):
			return f"Error: {stats.get('message', 'Unknown error')}"
		
		total_faces = stats.get('total_faces', 0)
		unique_zones = stats.get('unique_zones', 0)
		coverage_pct = stats.get('coverage_percentage', 0.0)
		ideal_zones = stats.get('ideal_zones', 24)
		
		# Generate visual indicator
		filled_blocks = int(coverage_pct / 10)  # 10 blocks for 0-100%
		empty_blocks = 10 - filled_blocks
		visual = '◼' * filled_blocks + '◻' * empty_blocks
		
		result = f"Coverage: {coverage_pct}% {visual}\n"
		result += f"Faces: {total_faces} | Unique zones: {unique_zones}/{ideal_zones}\n"
		
		# Show missing zones if any
		missing_zones = stats.get('missing_zones', [])
		if missing_zones and len(missing_zones) > 0:
			missing_str = ', '.join([f"{z['yaw']}°/{z['pitch']}°" for z in missing_zones[:3]])
			result += f"Missing: {missing_str}"
		else:
			result += "✅ Excellent coverage!"
		
		return result
	except Exception as e:
		return f'Error calculating stats: {str(e)}'
