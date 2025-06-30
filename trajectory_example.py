#!/usr/bin/env python3
"""
Simple trajectory animation example showing how to load and animate
molecular dynamics data or conformational changes
"""

import panel as pn
from panel_3dmol import Mol3DViewer

# Enable Panel extensions
pn.extension('filedropper')

def load_trajectory_from_file(filename):
    """
    Load trajectory from a multi-frame XYZ file
    (User would replace this with their actual trajectory data)
    """
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        # Split into individual frames
        frames = []
        lines = content.strip().split('\n')
        i = 0
        
        while i < len(lines):
            if lines[i].strip() and lines[i].strip().isdigit():
                natoms = int(lines[i])
                
                # Extract one frame (natoms + 2 lines for header)
                frame_lines = lines[i:i+natoms+2]
                frame = '\n'.join(frame_lines)
                frames.append(frame)
                
                i += natoms + 2
            else:
                i += 1
        
        return frames
    except FileNotFoundError:
        print(f"File {filename} not found, using demo data")
        return create_demo_trajectory()

def create_demo_trajectory():
    """Create a simple demo trajectory"""
    frames = []
    
    # Simple trajectory: methane molecule with varying C-H bonds
    for i in range(20):
        scale = 1.0 + 0.3 * (i / 19.0)  # Expand from 1.0 to 1.3
        
        frame = f"""5
Methane trajectory frame {i+1}
C    0.000000    0.000000    0.000000
H    {0.629*scale:.6f}    {0.629*scale:.6f}    {0.629*scale:.6f}
H   {-0.629*scale:.6f}   {-0.629*scale:.6f}    {0.629*scale:.6f}
H   {-0.629*scale:.6f}    {0.629*scale:.6f}   {-0.629*scale:.6f}
H    {0.629*scale:.6f}   {-0.629*scale:.6f}   {-0.629*scale:.6f}"""
        
        frames.append(frame)
    
    return frames

# Create trajectory viewer
print("Loading trajectory data...")
trajectory_frames = create_demo_trajectory()
print(f"Loaded {len(trajectory_frames)} frames")

# Create viewer and load trajectory
viewer = Mol3DViewer(width=500, height=400)
viewer.addFrames(trajectory_frames, 'xyz')
viewer.setStyle({}, {'stick': {'radius': 0.1}, 'sphere': {'radius': 0.3}})
viewer.setBackgroundColor('white')

# Add labels to track atoms
viewer.showAtomLabels(True)

print(f"Trajectory loaded: {viewer.total_frames} frames")

# Create control panel
frame_slider = pn.widgets.IntSlider(
    name="Frame", 
    start=0, 
    end=len(trajectory_frames)-1, 
    value=0,
    width=400
)

speed_slider = pn.widgets.IntSlider(
    name="Speed (ms per frame)",
    start=50,
    end=1000, 
    value=200,
    step=50,
    width=200
)

play_btn = pn.widgets.Button(name="▶️ Play", button_type="primary", width=100)
stop_btn = pn.widgets.Button(name="⏹️ Stop", button_type="danger", width=100) 
reset_btn = pn.widgets.Button(name="⏮️ Reset", button_type="light", width=100)

# Connect controls
def update_frame(event):
    viewer.setFrame(frame_slider.value)

def play_animation(event):
    viewer.setAnimationSpeed(speed_slider.value)
    viewer.startAnimation()
    
def stop_animation(event):
    viewer.stopAnimation()
    
def reset_animation(event):
    viewer.stopAnimation()
    viewer.setFrame(0)
    frame_slider.value = 0

def update_speed(event):
    viewer.setAnimationSpeed(speed_slider.value)

# Register callbacks
frame_slider.param.watch(update_frame, 'value')
play_btn.on_click(play_animation)
stop_btn.on_click(stop_animation)
reset_btn.on_click(reset_animation)
speed_slider.param.watch(update_speed, 'value')

# Information panel
info_panel = pn.pane.Markdown(f"""
### 📊 Trajectory Information
- **Total Frames**: {len(trajectory_frames)}
- **Current Frame**: Frame {viewer.current_frame + 1}
- **Animation**: {'Playing' if viewer.animate else 'Stopped'}
- **Speed**: {viewer.animation_speed}ms per frame

### 🎮 Controls
- Use the **frame slider** to manually navigate
- **Play/Stop** buttons control animation
- **Speed slider** adjusts playback rate
- **Reset** returns to first frame

### 💻 Python Usage
```python
# Load your trajectory
viewer.addFrames(your_frames, 'xyz')

# Control playback
viewer.startAnimation(100)    # 100ms per frame
viewer.setFrame(10)          # Jump to frame 10
viewer.stopAnimation()       # Stop
```
""")

# Create the app
app = pn.Column(
    "# 🎬 Molecular Trajectory Viewer",
    
    pn.Row(
        # Left panel: viewer and controls
        pn.Column(
            "## 🧬 Methane Expansion Trajectory",
            viewer,
            "### Animation Controls",
            frame_slider,
            pn.Row(play_btn, stop_btn, reset_btn),
            speed_slider,
            width=600
        ),
        
        # Right panel: information
        pn.Column(
            info_panel,
            width=400
        )
    ),
    
    sizing_mode='stretch_width'
)

app.servable()

# Example usage demonstrations
print("\n🎬 Trajectory Animation Ready!")
print("\nExample usage:")
print("1. Manual frame control:")
print(f"   viewer.setFrame(10)  # Jump to frame 10")
print(f"   current = viewer.getFrame()  # Get current frame: {viewer.getFrame()}")

print("\n2. Animation control:")
print("   viewer.startAnimation(150)  # Start with 150ms per frame")
print("   viewer.stopAnimation()      # Stop animation")

print("\n3. Speed control:")
print("   viewer.setAnimationSpeed(100)  # Set to 100ms per frame")

if __name__ == "__main__":
    print("\nRun 'panel serve trajectory_example.py --show' to view the trajectory")