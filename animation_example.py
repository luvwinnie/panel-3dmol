#!/usr/bin/env python3
"""
Animation example for panel_3dmol using 3Dmol.js setFrame functionality
Demonstrates molecular dynamics, conformational changes, and trajectory visualization
"""

import panel as pn
from panel_3dmol import Mol3DViewer
import numpy as np

# Enable Panel extensions
pn.extension('filedropper')
pn.config.sizing_mode = 'stretch_width'

def create_rotating_molecule_frames():
    """Create a simple rotating benzene molecule for animation demo"""
    
    # Base benzene structure
    base_coords = np.array([
        [0.0000, 1.3970, 0.0000],   # C1
        [1.2098, 0.6985, 0.0000],   # C2
        [1.2098, -0.6985, 0.0000],  # C3
        [0.0000, -1.3970, 0.0000],  # C4
        [-1.2098, -0.6985, 0.0000], # C5
        [-1.2098, 0.6985, 0.0000]   # C6
    ])
    
    frames = []
    n_frames = 20
    
    for i in range(n_frames):
        # Rotate around Z-axis
        angle = 2 * np.pi * i / n_frames
        rotation_matrix = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
        
        rotated_coords = base_coords @ rotation_matrix.T
        
        # Create XYZ format
        xyz_frame = f"6\nFrame {i+1} - Rotating Benzene\n"
        for j, coord in enumerate(rotated_coords):
            xyz_frame += f"C    {coord[0]:.4f}    {coord[1]:.4f}    {coord[2]:.4f}\n"
        
        frames.append(xyz_frame)
    
    return frames

def create_vibrating_molecule_frames():
    """Create vibrating molecule for animation demo"""
    
    # Water molecule base coordinates
    base_coords = np.array([
        [0.000000, 0.000000, 0.119262],   # O
        [0.000000, 0.763239, -0.477047],  # H1
        [0.000000, -0.763239, -0.477047]  # H2
    ])
    
    frames = []
    n_frames = 30
    symbols = ['O', 'H', 'H']
    
    for i in range(n_frames):
        # Create vibration effect
        vibration = 0.1 * np.sin(2 * np.pi * i / n_frames)
        
        # Modify coordinates with vibration
        vibrated_coords = base_coords.copy()
        vibrated_coords[1, 1] += vibration  # H1 vibration
        vibrated_coords[2, 1] -= vibration  # H2 vibration in opposite direction
        
        # Create XYZ format
        xyz_frame = f"3\nFrame {i+1} - Vibrating Water\n"
        for j, (symbol, coord) in enumerate(zip(symbols, vibrated_coords)):
            xyz_frame += f"{symbol}    {coord[0]:.6f}    {coord[1]:.6f}    {coord[2]:.6f}\n"
        
        frames.append(xyz_frame)
    
    return frames

def create_reaction_pathway_frames():
    """Create frames showing a simple reaction pathway"""
    
    frames = []
    n_frames = 25
    
    for i in range(n_frames):
        # Simulate bond breaking/forming
        progress = i / (n_frames - 1)
        
        # Start: H-H close together, End: H-H far apart
        h1_x = -0.5 + progress * 1.0  # Move from -0.5 to 0.5
        h2_x = 0.5 - progress * 1.0   # Move from 0.5 to -0.5
        
        xyz_frame = f"2\nFrame {i+1} - H2 Dissociation (progress: {progress:.2f})\n"
        xyz_frame += f"H    {h1_x:.4f}    0.0000    0.0000\n"
        xyz_frame += f"H    {h2_x:.4f}    0.0000    0.0000\n"
        
        frames.append(xyz_frame)
    
    return frames

# Create different animation examples
print("Creating animation frames...")

rotating_frames = create_rotating_molecule_frames()
vibrating_frames = create_vibrating_molecule_frames()
reaction_frames = create_reaction_pathway_frames()

print(f"Created {len(rotating_frames)} rotating frames")
print(f"Created {len(vibrating_frames)} vibrating frames") 
print(f"Created {len(reaction_frames)} reaction frames")

# Example 1: Rotating molecule
viewer1 = Mol3DViewer(width=400, height=300)
viewer1.addFrames(rotating_frames, 'xyz')
viewer1.setStyle({}, {'stick': {'radius': 0.1}, 'sphere': {'radius': 0.3}})
viewer1.setBackgroundColor('white')

# Example 2: Vibrating molecule  
viewer2 = Mol3DViewer(width=400, height=300)
viewer2.addFrames(vibrating_frames, 'xyz')
viewer2.setStyle({}, {'stick': {'radius': 0.15}, 'sphere': {'radius': 0.4}})
viewer2.setBackgroundColor('lightgray')

# Example 3: Reaction pathway
viewer3 = Mol3DViewer(width=400, height=300)
viewer3.addFrames(reaction_frames, 'xyz')
viewer3.setStyle({}, {'sphere': {'radius': 0.5}})
viewer3.setBackgroundColor('black')

# Animation control widgets
animation_controls1 = pn.Column(
    pn.widgets.IntSlider(name="Frame", start=0, end=len(rotating_frames)-1, value=0),
    pn.Row(
        pn.widgets.Button(name="Play", button_type="primary"),
        pn.widgets.Button(name="Stop", button_type="danger"),
        pn.widgets.IntInput(name="Speed (ms)", value=100, start=50, end=2000, step=50)
    )
)

animation_controls2 = pn.Column(
    pn.widgets.IntSlider(name="Frame", start=0, end=len(vibrating_frames)-1, value=0),
    pn.Row(
        pn.widgets.Button(name="Play", button_type="primary"),
        pn.widgets.Button(name="Stop", button_type="danger"),
        pn.widgets.IntInput(name="Speed (ms)", value=100, start=50, end=2000, step=50)
    )
)

animation_controls3 = pn.Column(
    pn.widgets.IntSlider(name="Frame", start=0, end=len(reaction_frames)-1, value=0),
    pn.Row(
        pn.widgets.Button(name="Play", button_type="primary"),
        pn.widgets.Button(name="Stop", button_type="danger"),
        pn.widgets.IntInput(name="Speed (ms)", value=200, start=50, end=2000, step=50)
    )
)

# Connect controls to viewers
def setup_animation_controls(viewer, controls):
    """Connect animation controls to viewer"""
    frame_slider = controls[0]
    play_btn = controls[1][0]
    stop_btn = controls[1][1] 
    speed_input = controls[1][2]
    
    # Frame slider control
    def update_frame(event):
        viewer.setFrame(frame_slider.value)
        
    # Play button
    def start_animation(event):
        viewer.setAnimationSpeed(speed_input.value)
        viewer.startAnimation()
        
    # Stop button
    def stop_animation(event):
        viewer.stopAnimation()
        
    # Speed control
    def update_speed(event):
        viewer.setAnimationSpeed(speed_input.value)
    
    # Connect callbacks
    frame_slider.param.watch(update_frame, 'value')
    play_btn.on_click(start_animation)
    stop_btn.on_click(stop_animation)
    speed_input.param.watch(update_speed, 'value')

# Setup controls for all viewers
setup_animation_controls(viewer1, [animation_controls1[0], animation_controls1[1].objects])
setup_animation_controls(viewer2, [animation_controls2[0], animation_controls2[1].objects])
setup_animation_controls(viewer3, [animation_controls3[0], animation_controls3[1].objects])

# Method demonstration
print("\nDemonstrating py3dmol-compatible animation methods:")

# Method 1: Direct control
print("Method 1: Direct frame control")
viewer1.setFrame(5)  # Jump to frame 5
print(f"Current frame: {viewer1.getFrame()}")

# Method 2: Animation control
print("Method 2: Animation control")
# viewer2.startAnimation(150)  # Start with 150ms per frame
print("Animation started (commented out for demo)")

# Method 3: Speed control
print("Method 3: Speed control")
viewer3.setAnimationSpeed(200)
print(f"Animation speed set to {viewer3.animation_speed}ms")

# Create the main application
app = pn.Column(
    "# 🎬 Molecular Animation Examples",
    
    pn.pane.Markdown("""
    **Animation Features:**
    - **setFrame(n)**: Jump to specific frame
    - **startAnimation(speed)**: Start animation playback  
    - **stopAnimation()**: Stop animation
    - **addFrames(structures)**: Load multiple structures as frames
    - **setAnimationSpeed(ms)**: Control playback speed
    
    **Use Cases:**
    - Molecular dynamics trajectories
    - Conformational changes
    - Reaction pathways
    - Vibrational modes
    """),
    
    # Example 1: Rotating Benzene
    pn.Row(
        pn.Column(
            "### 🔄 Rotating Benzene",
            f"**{len(rotating_frames)} frames** - Rotation around Z-axis",
            viewer1,
            animation_controls1
        ),
        # Example 2: Vibrating Water
        pn.Column(
            "### 🌊 Vibrating Water", 
            f"**{len(vibrating_frames)} frames** - H-O-H bending vibration",
            viewer2,
            animation_controls2
        )
    ),
    
    # Example 3: Reaction Pathway
    pn.Column(
        "### ⚗️ H₂ Dissociation Pathway",
        f"**{len(reaction_frames)} frames** - Bond breaking simulation",
        pn.Row(viewer3, animation_controls3)
    ),
    
    pn.pane.Markdown("""
    ---
    **Usage in Python:**
    ```python
    # Load multiple frames
    viewer.addFrames(trajectory_frames, 'xyz')
    
    # Control animation
    viewer.startAnimation(100)  # 100ms per frame
    viewer.setFrame(10)         # Jump to frame 10
    viewer.stopAnimation()      # Stop playback
    ```
    """),
    
    sizing_mode='stretch_width'
)

app.servable()

if __name__ == "__main__":
    print("\n🎉 Animation examples ready!")
    print("Features implemented:")
    print("- ✅ Multi-frame structure loading")
    print("- ✅ Frame-by-frame control (setFrame)")
    print("- ✅ Animation playback (start/stop)")
    print("- ✅ Speed control")
    print("- ✅ py3dmol-compatible API")
    print("\nRun 'panel serve animation_example.py --show' to see the animations")