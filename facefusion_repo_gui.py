#!/usr/bin/env python3
"""
Gradio GUI for FaceFusion Repository System.

Provides a visual interface for managing the person-based face repository,
settings profiles, and presets for FaceFusion.
"""

import gradio as gr
from typing import List, Tuple

from facefusion_repository.repository.manager import RepositoryManager
from facefusion_repository.settings.manager import SettingsManager
from facefusion_repository.presets.manager import PresetsManager


class RepositoryGUI:
    """Gradio GUI for repository management."""

    def __init__(self) -> None:
        """Initialize the GUI."""
        self.repo_manager = RepositoryManager()
        self.settings_manager = SettingsManager()
        self.presets_manager = PresetsManager()

    def initialize_repository(self) -> str:
        """Initialize the repository."""
        if self.repo_manager.initialize_repository():
            return "✓ Repository initialized successfully!"
        return "✗ Failed to initialize repository"

    def add_person(self, person_id: str, display_name: str) -> str:
        """Add a new person."""
        if not person_id:
            return "Error: Person ID is required"
        
        display_name = display_name or person_id
        if self.repo_manager.add_person(person_id, display_name):
            return f"✓ Person '{person_id}' added successfully!"
        return "✗ Failed to add person"

    def list_people(self) -> str:
        """List all people."""
        people = self.repo_manager.list_people()
        if not people:
            return "No people in repository."
        
        result = [f"People ({len(people)}):"]
        for person in people:
            result.append(f"\n  {person.id}")
            result.append(f"    Name: {person.display_name}")
            result.append(f"    Faces: {len(person.face_ids)}")
        
        return "\n".join(result)

    def add_face(self, image, person_id: str, name: str) -> str:
        """Add a face for a person."""
        if not image:
            return "Error: Please upload an image"
        if not person_id:
            return "Error: Person ID is required"
        
        # Save temporary image
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp_path = tmp.name
            # Gradio provides image as numpy array or filepath
            if isinstance(image, str):
                import shutil
                shutil.copy(image, tmp_path)
            else:
                from PIL import Image
                import numpy as np
                if isinstance(image, np.ndarray):
                    Image.fromarray(image).save(tmp_path)
        
        try:
            face_id = self.repo_manager.add_face(
                image_path=tmp_path,
                person_id=person_id,
                name=name or None
            )
            
            if face_id:
                return f"✓ Face added successfully!\nFace ID: {face_id}"
            return "✗ Failed to add face (check quality requirements)"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def list_faces(self, person_filter: str) -> str:
        """List faces, optionally filtered by person."""
        faces = self.repo_manager.list_faces()
        
        if person_filter:
            faces = [f for f in faces if f.metadata.person_id == person_filter]
        
        if not faces:
            return "No faces found."
        
        result = [f"Faces ({len(faces)}):"]
        
        # Group by person
        from collections import defaultdict
        faces_by_person = defaultdict(list)
        for face in faces:
            faces_by_person[face.metadata.person_id].append(face)
        
        for person_id, person_faces in sorted(faces_by_person.items()):
            result.append(f"\n  Person: {person_id} ({len(person_faces)} faces)")
            for face in person_faces:
                result.append(f"    - {face.id}")
                result.append(f"      Orientation: {face.orientation_angle}°")
                result.append(f"      Quality: {face.quality_metrics.overall_quality:.2f}")
        
        return "\n".join(result)

    def get_stats(self) -> str:
        """Get repository statistics."""
        stats = self.repo_manager.get_statistics()
        if not stats:
            return "No statistics available"
        
        result = [
            "Repository Statistics",
            "=" * 40,
            f"Total People: {stats.total_people}",
            f"Total Faces: {stats.total_faces}",
            f"Average Quality: {stats.average_quality:.2f}",
            f"Storage Used: {stats.total_size_mb:.2f} MB",
            ""
        ]
        
        if stats.faces_by_person:
            result.append("Faces by Person:")
            for person_id, count in sorted(stats.faces_by_person.items()):
                result.append(f"  {person_id}: {count} faces")
        
        return "\n".join(result)

    def create_settings(self, name: str, description: str, template: str) -> str:
        """Create a settings profile."""
        if not name:
            return "Error: Settings name is required"
        
        if self.settings_manager.create_settings(
            name=name,
            description=description,
            parameters={},
            template=template or None
        ):
            return f"✓ Settings profile '{name}' created successfully!"
        return "✗ Failed to create settings profile"

    def list_settings(self) -> str:
        """List all settings profiles."""
        profiles = self.settings_manager.list_settings()
        if not profiles:
            return "No settings profiles found."
        
        result = [f"Settings Profiles ({len(profiles)}):"]
        for profile in profiles:
            result.append(f"\n  {profile.name}")
            result.append(f"    Description: {profile.description or 'No description'}")
            result.append(f"    Parameters: {len(profile.parameters)} configured")
        
        return "\n".join(result)

    def create_preset(self, name: str, description: str, person_id: str, settings_name: str) -> str:
        """Create a preset."""
        if not name:
            return "Error: Preset name is required"
        if not person_id:
            return "Error: Person ID is required"
        if not settings_name:
            return "Error: Settings name is required"
        
        if self.presets_manager.create_preset(
            name=name,
            description=description,
            person_id=person_id,
            settings_name=settings_name
        ):
            return f"✓ Preset '{name}' created successfully!"
        return "✗ Failed to create preset"

    def list_presets(self) -> str:
        """List all presets."""
        presets = self.presets_manager.list_presets()
        if not presets:
            return "No presets found."
        
        result = [f"Presets ({len(presets)}):"]
        for preset in presets:
            result.append(f"\n  {preset.name}")
            result.append(f"    Person: {preset.person_id}")
            result.append(f"    Settings: {preset.settings_name}")
            result.append(f"    Usage Count: {preset.usage_count}")
        
        return "\n".join(result)

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface."""
        with gr.Blocks(title="FaceFusion Repository System") as interface:
            gr.Markdown("# FaceFusion Repository System")
            gr.Markdown("Person-based face repository management with orientation matching")

            with gr.Tabs():
                # Repository Tab
                with gr.Tab("Repository"):
                    gr.Markdown("## Person & Face Management")
                    
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### Initialize Repository")
                            init_btn = gr.Button("Initialize Repository")
                            init_output = gr.Textbox(label="Result", lines=2)
                            init_btn.click(self.initialize_repository, outputs=init_output)
                        
                        with gr.Column():
                            gr.Markdown("### Repository Statistics")
                            stats_btn = gr.Button("Show Statistics")
                            stats_output = gr.Textbox(label="Statistics", lines=10)
                            stats_btn.click(self.get_stats, outputs=stats_output)
                    
                    gr.Markdown("### Add Person")
                    with gr.Row():
                        person_id_input = gr.Textbox(label="Person ID (alphanumeric)", placeholder="john_doe")
                        display_name_input = gr.Textbox(label="Display Name (optional)", placeholder="John Doe")
                    add_person_btn = gr.Button("Add Person")
                    add_person_output = gr.Textbox(label="Result", lines=2)
                    add_person_btn.click(
                        self.add_person,
                        inputs=[person_id_input, display_name_input],
                        outputs=add_person_output
                    )
                    
                    gr.Markdown("### Add Face")
                    with gr.Row():
                        with gr.Column():
                            face_image = gr.Image(label="Upload Face Image", type="filepath")
                            face_person_id = gr.Textbox(label="Person ID", placeholder="john_doe")
                            face_name = gr.Textbox(label="Face Name (optional)", placeholder="John Frontal")
                            add_face_btn = gr.Button("Add Face")
                        with gr.Column():
                            add_face_output = gr.Textbox(label="Result", lines=5)
                    add_face_btn.click(
                        self.add_face,
                        inputs=[face_image, face_person_id, face_name],
                        outputs=add_face_output
                    )
                    
                    gr.Markdown("### List People & Faces")
                    with gr.Row():
                        with gr.Column():
                            list_people_btn = gr.Button("List All People")
                            people_output = gr.Textbox(label="People", lines=10)
                            list_people_btn.click(self.list_people, outputs=people_output)
                        
                        with gr.Column():
                            person_filter = gr.Textbox(label="Filter by Person (optional)")
                            list_faces_btn = gr.Button("List Faces")
                            faces_output = gr.Textbox(label="Faces", lines=10)
                            list_faces_btn.click(
                                self.list_faces,
                                inputs=person_filter,
                                outputs=faces_output
                            )
                
                # Settings Tab
                with gr.Tab("Settings"):
                    gr.Markdown("## FaceFusion Settings Profiles")
                    
                    gr.Markdown("### Create Settings Profile")
                    with gr.Row():
                        settings_name = gr.Textbox(label="Profile Name", placeholder="my_high_quality")
                        settings_desc = gr.Textbox(label="Description (optional)")
                        settings_template = gr.Dropdown(
                            label="Template",
                            choices=["", "high_quality", "fast", "gpu_accelerated", "cpu_optimized"]
                        )
                    create_settings_btn = gr.Button("Create Settings Profile")
                    create_settings_output = gr.Textbox(label="Result", lines=2)
                    create_settings_btn.click(
                        self.create_settings,
                        inputs=[settings_name, settings_desc, settings_template],
                        outputs=create_settings_output
                    )
                    
                    gr.Markdown("### List Settings Profiles")
                    list_settings_btn = gr.Button("List All Settings")
                    settings_list_output = gr.Textbox(label="Settings Profiles", lines=10)
                    list_settings_btn.click(self.list_settings, outputs=settings_list_output)
                
                # Presets Tab
                with gr.Tab("Presets"):
                    gr.Markdown("## Person + Settings Presets")
                    
                    gr.Markdown("### Create Preset")
                    with gr.Row():
                        preset_name = gr.Textbox(label="Preset Name", placeholder="john_hq")
                        preset_desc = gr.Textbox(label="Description (optional)")
                    with gr.Row():
                        preset_person = gr.Textbox(label="Person ID", placeholder="john_doe")
                        preset_settings = gr.Textbox(label="Settings Profile Name", placeholder="my_high_quality")
                    create_preset_btn = gr.Button("Create Preset")
                    create_preset_output = gr.Textbox(label="Result", lines=2)
                    create_preset_btn.click(
                        self.create_preset,
                        inputs=[preset_name, preset_desc, preset_person, preset_settings],
                        outputs=create_preset_output
                    )
                    
                    gr.Markdown("### List Presets")
                    list_presets_btn = gr.Button("List All Presets")
                    presets_list_output = gr.Textbox(label="Presets", lines=10)
                    list_presets_btn.click(self.list_presets, outputs=presets_list_output)

            gr.Markdown("---")
            gr.Markdown("FaceFusion Repository System v2.0 - Person-Based Architecture")

        return interface


def main() -> None:
    """Launch the GUI."""
    gui = RepositoryGUI()
    interface = gui.create_interface()
    interface.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        inbrowser=True
    )


if __name__ == "__main__":
    main()
