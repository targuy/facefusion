"""
Repository UI layout for FaceFusion Repository System.
Provides interface for managing faces, characters, and batch processing.
"""

import gradio as gr
from facefusion.uis import repository_backend as backend

# Store UI components globally for event binding
UI_COMPONENTS = {}


def pre_check() -> bool:
    """Pre-check before rendering UI."""
    return True


def render() -> None:
    """Render the repository management UI."""
    global UI_COMPONENTS
    
    gr.Markdown("# 🎭 FaceFusion Repository System")
    gr.Markdown("Manage faces with multi-axis orientation and character grouping")
    
    with gr.Tabs():
        # Tab 1: Repository Management
        with gr.Tab("📁 Repository"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Add Face")
                    UI_COMPONENTS['face_image'] = gr.Image(
                        label="Face Image",
                        type="filepath",
                        sources=["upload"]
                    )
                    UI_COMPONENTS['face_name'] = gr.Textbox(
                        label="Name (optional)",
                        placeholder="e.g., Alice Frontal"
                    )
                    UI_COMPONENTS['face_tags'] = gr.Textbox(
                        label="Tags (optional)",
                        placeholder="e.g., frontal, high-quality"
                    )
                    UI_COMPONENTS['face_character'] = gr.Textbox(
                        label="Character ID (optional)"
                    )
                    UI_COMPONENTS['add_face_btn'] = gr.Button("➕ Add Face", variant="primary")
                    UI_COMPONENTS['add_face_out'] = gr.Textbox(label="Status", interactive=False, lines=5)
                
                with gr.Column():
                    gr.Markdown("### List Faces")
                    UI_COMPONENTS['list_orientation'] = gr.Dropdown(
                        label="Filter by Orientation",
                        choices=["All", "0°", "45°", "90°", "135°", "180°", "225°", "270°", "315°"],
                        value="All"
                    )
                    UI_COMPONENTS['list_character'] = gr.Textbox(
                        label="Filter by Character ID"
                    )
                    UI_COMPONENTS['list_faces_btn'] = gr.Button("🔍 List Faces")
                    UI_COMPONENTS['faces_list'] = gr.Dataframe(
                        headers=["ID", "Name", "Orientation", "3D Orient", "Quality", "Character"],
                        label="Faces"
                    )
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Face Details")
                    UI_COMPONENTS['face_id'] = gr.Textbox(label="Face ID")
                    UI_COMPONENTS['show_face_btn'] = gr.Button("👁️ Show Details")
                    UI_COMPONENTS['face_details'] = gr.Textbox(label="Details", lines=10, interactive=False)
                
                with gr.Column():
                    gr.Markdown("### Remove Face")
                    UI_COMPONENTS['remove_face_id'] = gr.Textbox(label="Face ID to Remove")
                    UI_COMPONENTS['remove_face_btn'] = gr.Button("🗑️ Remove", variant="stop")
                    UI_COMPONENTS['remove_face_out'] = gr.Textbox(label="Status", interactive=False)
        
        # Tab 2: Character Management
        with gr.Tab("👤 Characters"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Add Character")
                    UI_COMPONENTS['char_name'] = gr.Textbox(label="Character Name")
                    UI_COMPONENTS['char_desc'] = gr.Textbox(label="Description (optional)")
                    UI_COMPONENTS['char_tags'] = gr.Textbox(label="Tags (optional)")
                    UI_COMPONENTS['add_char_btn'] = gr.Button("➕ Add Character", variant="primary")
                    UI_COMPONENTS['add_char_out'] = gr.Textbox(label="Status", interactive=False, lines=5)
                
                with gr.Column():
                    gr.Markdown("### List Characters")
                    UI_COMPONENTS['list_char_btn'] = gr.Button("🔍 List Characters")
                    UI_COMPONENTS['char_list'] = gr.Dataframe(
                        headers=["ID", "Name", "Faces", "Description", "Tags"],
                        label="Characters"
                    )
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Character Details")
                    UI_COMPONENTS['char_id'] = gr.Textbox(label="Character ID")
                    UI_COMPONENTS['show_char_btn'] = gr.Button("👁️ Show Details")
                    UI_COMPONENTS['char_details'] = gr.Textbox(label="Details", lines=10, interactive=False)
                
                with gr.Column():
                    gr.Markdown("### Remove Character")
                    UI_COMPONENTS['remove_char_id'] = gr.Textbox(label="Character ID to Remove")
                    UI_COMPONENTS['remove_char_btn'] = gr.Button("🗑️ Remove", variant="stop")
                    UI_COMPONENTS['remove_char_out'] = gr.Textbox(label="Status", interactive=False)
        
        # Tab 3: Face Swap
        with gr.Tab("🔄 Face Swap"):
            gr.Markdown("### Swap faces using characters with multiple angles")
            gr.Markdown("This feature automatically selects the best face angle from your character's faces based on the target's orientation.")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Step 1: Select Character")
                    UI_COMPONENTS['swap_character_dropdown'] = gr.Dropdown(
                        label="Select Character to Use",
                        choices=[],
                        info="Choose a character from your repository"
                    )
                    UI_COMPONENTS['refresh_char_btn'] = gr.Button("🔄 Refresh Character List")
                    UI_COMPONENTS['swap_char_info'] = gr.Textbox(
                        label="Character Info",
                        interactive=False,
                        lines=4
                    )
                    
                    gr.Markdown("#### Step 2: Upload Target Media")
                    UI_COMPONENTS['swap_target'] = gr.File(
                        label="Target Image or Video",
                        file_types=[".jpg", ".jpeg", ".png", ".mp4", ".avi", ".mov"]
                    )
                    
                    gr.Markdown("#### Step 3: Configure Swap Options")
                    UI_COMPONENTS['swap_face_selector'] = gr.Dropdown(
                        label="Face Selection Mode",
                        choices=[
                            "Auto (Best Match per Frame)",
                            "Single Face (Best Overall)",
                            "All Faces (Multi-angle)"
                        ],
                        value="Auto (Best Match per Frame)",
                        info="Auto mode uses different face angles as needed"
                    )
                    UI_COMPONENTS['swap_output_path'] = gr.Textbox(
                        label="Output Path (optional)",
                        placeholder="e.g., output/result.mp4",
                        info="Leave empty for auto-generated name"
                    )
                    
                    UI_COMPONENTS['swap_btn'] = gr.Button("🎭 Start Face Swap", variant="primary", size="lg")
                
                with gr.Column():
                    gr.Markdown("#### Swap Progress & Results")
                    UI_COMPONENTS['swap_progress'] = gr.Textbox(
                        label="Progress",
                        interactive=False,
                        lines=8
                    )
                    UI_COMPONENTS['swap_preview'] = gr.Image(
                        label="Preview (First Frame)",
                        type="filepath"
                    )
                    UI_COMPONENTS['swap_result_file'] = gr.File(
                        label="Download Result"
                    )
                    
            gr.Markdown("---")
            
            with gr.Accordion("📖 How to Use Face Swap with Multiple Angles", open=False):
                gr.Markdown("""
                ### Using Multiple Face Angles for Better Results
                
                **Why use multiple angles?**
                - When a person in the video turns their head, a single frontal face may not look natural
                - Using multiple angles (frontal, left, right, profile) ensures better results at all orientations
                
                **Workflow:**
                
                1. **Prepare Your Character:**
                   - Go to the "👤 Characters" tab
                   - Create a character (e.g., "Alice")
                   - Note the character ID (e.g., char_abc123)
                
                2. **Add Multiple Face Angles:**
                   - Go to the "📁 Repository" tab
                   - Upload frontal view → Set Character ID → Add Face
                   - Upload left profile → Set Character ID → Add Face
                   - Upload right profile → Set Character ID → Add Face
                   - Upload any other angles you have
                   
                   💡 **Tip**: The system automatically detects orientation, so you don't need to specify angles manually!
                
                3. **Perform Face Swap:**
                   - Come to this "🔄 Face Swap" tab
                   - Select your character from the dropdown
                   - Upload target video/image
                   - Choose "Auto (Best Match per Frame)" mode
                   - Click "Start Face Swap"
                
                4. **What Happens:**
                   - System analyzes each frame's face orientation
                   - Automatically selects the best matching face from your character's collection
                   - Swaps using the most appropriate angle for natural results
                   - Example: If target turns left, uses your left profile; if frontal, uses your frontal face
                
                **Best Practices:**
                - Add at least 3-5 different angles for best coverage
                - Use high-quality, well-lit photos
                - Include: frontal (0°), left quarter (45°), right quarter (315°), and profiles (90°, 270°)
                - All faces should be of the same person in similar conditions (lighting, expression)
                """)
        
        # Tab 4: Statistics
        with gr.Tab("📊 Statistics"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Repository Statistics")
                    UI_COMPONENTS['stats_btn'] = gr.Button("📈 Generate Statistics")
                    UI_COMPONENTS['stats_out'] = gr.Textbox(label="Statistics", lines=15, interactive=False)
                
                with gr.Column():
                    gr.Markdown("### Orientation Coverage")
                    UI_COMPONENTS['coverage_out'] = gr.HTML(
                        value="<p>Click 'Generate Statistics' to view coverage</p>"
                    )


def listen() -> None:
    """Set up event listeners for UI components."""
    global UI_COMPONENTS
    
    # Repository tab events
    UI_COMPONENTS['add_face_btn'].click(
        fn=backend.add_face_to_repository,
        inputs=[
            UI_COMPONENTS['face_image'],
            UI_COMPONENTS['face_name'],
            UI_COMPONENTS['face_tags'],
            UI_COMPONENTS['face_character']
        ],
        outputs=UI_COMPONENTS['add_face_out']
    )
    
    UI_COMPONENTS['list_faces_btn'].click(
        fn=backend.list_faces_in_repository,
        inputs=[
            UI_COMPONENTS['list_orientation'],
            UI_COMPONENTS['list_character']
        ],
        outputs=UI_COMPONENTS['faces_list']
    )
    
    UI_COMPONENTS['show_face_btn'].click(
        fn=backend.show_face_details,
        inputs=UI_COMPONENTS['face_id'],
        outputs=UI_COMPONENTS['face_details']
    )
    
    UI_COMPONENTS['remove_face_btn'].click(
        fn=backend.remove_face_from_repository,
        inputs=UI_COMPONENTS['remove_face_id'],
        outputs=UI_COMPONENTS['remove_face_out']
    )
    
    # Character tab events
    UI_COMPONENTS['add_char_btn'].click(
        fn=backend.add_character,
        inputs=[
            UI_COMPONENTS['char_name'],
            UI_COMPONENTS['char_desc'],
            UI_COMPONENTS['char_tags']
        ],
        outputs=UI_COMPONENTS['add_char_out']
    )
    
    UI_COMPONENTS['list_char_btn'].click(
        fn=backend.list_characters,
        outputs=UI_COMPONENTS['char_list']
    )
    
    UI_COMPONENTS['show_char_btn'].click(
        fn=backend.show_character_details,
        inputs=UI_COMPONENTS['char_id'],
        outputs=UI_COMPONENTS['char_details']
    )
    
    UI_COMPONENTS['remove_char_btn'].click(
        fn=backend.remove_character,
        inputs=UI_COMPONENTS['remove_char_id'],
        outputs=UI_COMPONENTS['remove_char_out']
    )
    
    # Face Swap tab events
    UI_COMPONENTS['refresh_char_btn'].click(
        fn=backend.get_character_list_for_swap,
        outputs=UI_COMPONENTS['swap_character_dropdown']
    )
    
    UI_COMPONENTS['swap_character_dropdown'].change(
        fn=backend.get_character_info_for_swap,
        inputs=UI_COMPONENTS['swap_character_dropdown'],
        outputs=UI_COMPONENTS['swap_char_info']
    )
    
    UI_COMPONENTS['swap_btn'].click(
        fn=backend.perform_face_swap,
        inputs=[
            UI_COMPONENTS['swap_character_dropdown'],
            UI_COMPONENTS['swap_target'],
            UI_COMPONENTS['swap_face_selector'],
            UI_COMPONENTS['swap_output_path']
        ],
        outputs=[
            UI_COMPONENTS['swap_progress'],
            UI_COMPONENTS['swap_preview'],
            UI_COMPONENTS['swap_result_file']
        ]
    )
    
    # Statistics tab events
    UI_COMPONENTS['stats_btn'].click(
        fn=backend.get_repository_statistics,
        outputs=[
            UI_COMPONENTS['stats_out'],
            UI_COMPONENTS['coverage_out']
        ]
    )


def run(ui: gr.Blocks) -> None:
    """Launch the UI."""
    pass  # Launching is handled by the main UI system
