"""Repository UI component for person management."""

from typing import List, Optional, Tuple

import gradio

from facefusion import state_manager
from facefusion.uis.core import register_ui_component
from facefusion.uis.types import File

REPOSITORY_PERSON_NAME: Optional[gradio.Textbox] = None
REPOSITORY_FACE_FILES: Optional[gradio.File] = None
REPOSITORY_PERSON_SELECT: Optional[gradio.Dropdown] = None
REPOSITORY_STATUS: Optional[gradio.Textbox] = None
REPOSITORY_PERSON_LIST: Optional[gradio.Textbox] = None


def render() -> None:
	global REPOSITORY_PERSON_NAME
	global REPOSITORY_FACE_FILES
	global REPOSITORY_PERSON_SELECT
	global REPOSITORY_STATUS
	global REPOSITORY_PERSON_LIST

	with gradio.Accordion('Repository', open=True):
		gradio.Markdown('### Add Person to Repository')
		REPOSITORY_PERSON_NAME = gradio.Textbox(
			label='Person Name',
			placeholder='Enter person name...'
		)
		REPOSITORY_FACE_FILES = gradio.File(
			label='Face Images',
			file_count='multiple',
			file_types=['image']
		)
		add_button = gradio.Button('Add Person')
		
		gradio.Markdown('### Select Person for Processing')
		REPOSITORY_PERSON_SELECT = gradio.Dropdown(
			label='Select Person',
			choices=_get_person_names(),
			value=state_manager.get_item('repository_person') if state_manager.get_item('repository_person') else None
		)
		refresh_button = gradio.Button('Refresh List')
		
		gradio.Markdown('### Repository Status')
		REPOSITORY_STATUS = gradio.Textbox(
			label='Status',
			value='Ready',
			interactive=False
		)
		
		gradio.Markdown('### Persons in Repository')
		REPOSITORY_PERSON_LIST = gradio.Textbox(
			label='Persons',
			value=_format_person_list(),
			interactive=False,
			lines=5
		)
		
		# Connect buttons
		add_button.click(
			fn=add_person,
			inputs=[REPOSITORY_PERSON_NAME, REPOSITORY_FACE_FILES],
			outputs=[REPOSITORY_STATUS, REPOSITORY_PERSON_LIST, REPOSITORY_PERSON_SELECT]
		)
		
		refresh_button.click(
			fn=refresh_persons,
			outputs=[REPOSITORY_PERSON_SELECT, REPOSITORY_PERSON_LIST]
		)
	
	register_ui_component('repository_person_select', REPOSITORY_PERSON_SELECT)
	register_ui_component('repository_status', REPOSITORY_STATUS)


def listen() -> None:
	REPOSITORY_PERSON_SELECT.change(update_selected_person, inputs=REPOSITORY_PERSON_SELECT)


def _get_repository_manager():
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


def add_person(person_name: str, files: List[File]) -> Tuple[str, str, gradio.Dropdown]:
	"""Add a person to the repository."""
	if not person_name:
		return 'Error: Person name is required', _format_person_list(), gradio.Dropdown(choices=_get_person_names())
	
	if not files:
		return 'Error: At least one face image is required', _format_person_list(), gradio.Dropdown(choices=_get_person_names())
	
	try:
		manager = _get_repository_manager()
		file_paths = [file.name for file in files]
		person = manager.create_person(person_name, file_paths)
		
		status = f"Successfully added '{person_name}' with {person['face_count']} faces"
		person_list = _format_person_list()
		person_names = _get_person_names()
		
		return status, person_list, gradio.Dropdown(choices=person_names)
	except Exception as e:
		return f'Error: {str(e)}', _format_person_list(), gradio.Dropdown(choices=_get_person_names())


def refresh_persons() -> Tuple[gradio.Dropdown, str]:
	"""Refresh the person list."""
	person_names = _get_person_names()
	person_list = _format_person_list()
	return gradio.Dropdown(choices=person_names), person_list


def update_selected_person(person_name: Optional[str]) -> None:
	"""Update the selected person in state."""
	if person_name:
		state_manager.set_item('repository_person', person_name)
		
		# Get face paths for this person and update source_paths
		manager = _get_repository_manager()
		person = manager.get_person_by_name(person_name)
		if person:
			state_manager.set_item('source_paths', person['face_paths'])
	else:
		state_manager.clear_item('repository_person')
