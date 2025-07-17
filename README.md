# Panel-3Dmol

[![Github Action Tests](https://github.com/luvwinnie/panel-3dmol/actions/workflows/test.yml/badge.svg)](https://github.com/luvwinnie/panel-3dmol/actions)

A Panel extension for 3D molecular visualization using 3Dmol.js. Create interactive molecular viewers with animation support, labeling capabilities, and seamless Panel dashboard integration.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/luvwinnie/panel-3dmol.git
```

## Quick Start

### Basic Usage

```python
import panel as pn
from panel_3dmol import Mol3DViewer

# Enable Panel
pn.extension()

# Create a molecular viewer
viewer = Mol3DViewer()

# Load molecular data
xyz_data = """6
Benzene molecule
C    0.0000    1.3970    0.0000
C    1.2098    0.6985    0.0000  
C    1.2098   -0.6985    0.0000
C    0.0000   -1.3970    0.0000
C   -1.2098   -0.6985    0.0000
C   -1.2098    0.6985    0.0000"""

viewer.structure = xyz_data
viewer.filetype = "xyz"

# Create a Panel app
app = pn.Column("# Molecular Viewer", viewer)
app.servable()
```

### Panel Dashboard with File Upload

```python
import panel as pn
from panel_3dmol import Mol3DViewer

# Enable Panel
pn.extension()

# Create viewers
reactant_viewer = Mol3DViewer()
product_viewer = Mol3DViewer()

# Create file upload widgets
reactant_dropper = pn.widgets.FileDropper(
    name="🧪 Drop Reactant File (.xyz, .pdb, .mol, .sdf)",
    height=100
)

product_dropper = pn.widgets.FileDropper(
    name="🎯 Drop Product File (.xyz, .pdb, .mol, .sdf)", 
    height=100
)

# File upload handlers
def on_reactant_drop(event):
    if reactant_dropper.value:
        filename, file_content = next(iter(reactant_dropper.value.items()))
        if isinstance(file_content, bytes):
            file_content = file_content.decode('utf-8', errors='ignore')
        
        extension = filename.split('.')[-1].lower()
        reactant_viewer.filetype = extension
        reactant_viewer.structure = file_content
        print(f"✅ Loaded {filename}")

def on_product_drop(event):
    if product_dropper.value:
        filename, file_content = next(iter(product_dropper.value.items()))
        if isinstance(file_content, bytes):
            file_content = file_content.decode('utf-8', errors='ignore')
        
        extension = filename.split('.')[-1].lower()
        product_viewer.filetype = extension
        product_viewer.structure = file_content
        print(f"✅ Loaded {filename}")

# Register callbacks
reactant_dropper.param.watch(on_reactant_drop, 'value')
product_dropper.param.watch(on_product_drop, 'value')

# Create dashboard layout
dashboard = pn.Column(
    "## 🧬 Dual Molecular Viewer",
    
    # File upload section
    pn.Row(reactant_dropper, product_dropper),
    
    # Molecular viewers side-by-side
    pn.Row(
        pn.Column("### 🧪 Reactant", reactant_viewer),
        pn.Column("### 🎯 Product", product_viewer)
    ),
    
    sizing_mode='stretch_width'
)

dashboard.servable()
```

### Animation and Trajectory Visualization

```python
import panel as pn
from panel_3dmol import Mol3DViewer

# Enable Panel
pn.extension()

# Create viewer with animation support
viewer = Mol3DViewer(width=600, height=400)

# Load multiple frames for animation
frame_structures = [
    # Frame 1
    """3
Frame 1
C    0.0000    0.0000    0.0000
H    1.0000    0.0000    0.0000
H   -0.5000    0.8660    0.0000""",
    
    # Frame 2 (slightly moved)
    """3
Frame 2
C    0.1000    0.0000    0.0000
H    1.1000    0.0000    0.0000
H   -0.4000    0.8660    0.0000""",
    
    # Add more frames...
]

# Add frames to viewer
viewer.addFrames(frame_structures, filetype="xyz")

# Configure animation
viewer.startAnimation(speed=500, loop_mode="forward")

# Create controls
play_button = pn.widgets.Button(name="▶️ Play", button_type="primary")
stop_button = pn.widgets.Button(name="⏹️ Stop", button_type="primary")
frame_slider = pn.widgets.IntSlider(
    name="Frame", 
    start=0, 
    end=viewer.total_frames-1, 
    value=viewer.current_frame
)

# Animation control callbacks
def play_animation(event):
    viewer.startAnimation()

def stop_animation(event):
    viewer.stopAnimation()

def change_frame(event):
    viewer.setFrame(frame_slider.value)

play_button.on_click(play_animation)
stop_button.on_click(stop_animation)
frame_slider.param.watch(change_frame, 'value')

# Layout with controls
app = pn.Column(
    "## 🎬 Molecular Animation",
    viewer,
    pn.Row(play_button, stop_button),
    frame_slider,
    sizing_mode='stretch_width'
)

app.servable()
```

### Labeling and Annotations

```python
import panel as pn
from panel_3dmol import Mol3DViewer

# Enable Panel
pn.extension()

# Create viewer
viewer = Mol3DViewer()

# Load molecule
viewer.structure = """6
Benzene with labels
C    0.0000    1.3970    0.0000
C    1.2098    0.6985    0.0000  
C    1.2098   -0.6985    0.0000
C    0.0000   -1.3970    0.0000
C   -1.2098   -0.6985    0.0000
C   -1.2098    0.6985    0.0000"""
viewer.filetype = "xyz"

# Enable automatic atom numbering
viewer.show_atom_labels = True

# Add custom labels
viewer.addLabel("Benzene Ring", {
    'position': {'x': 0, 'y': 0, 'z': 1},
    'backgroundColor': 'yellow',
    'fontColor': 'black',
    'fontSize': 18
})

# Display
viewer
```

### Jupyter Notebook Usage

```python
import panel as pn
from panel_3dmol import Mol3DViewer

# Enable Panel in Jupyter
pn.extension()

# Create viewer
viewer = Mol3DViewer(width=600, height=400)

# Load sample molecule
caffeine_pdb = """ATOM      1  N   CAF     1      -0.744   1.329   0.000  1.00  0.00           N  
ATOM      2  C   CAF     1       0.558   1.875   0.000  1.00  0.00           C  
ATOM      3  C   CAF     1       1.657   1.080   0.000  1.00  0.00           C  
ATOM      4  N   CAF     1       1.657  -0.287   0.000  1.00  0.00           N  
ATOM      5  C   CAF     1       0.455  -0.832   0.000  1.00  0.00           C  
ATOM      6  C   CAF     1      -0.744  -0.037   0.000  1.00  0.00           C  """

viewer.structure = caffeine_pdb
viewer.filetype = "pdb"

# Display in notebook
viewer
```

## API Reference

### Mol3DViewer Parameters

**Core Parameters:**
- `structure` (str): Molecular structure data
- `filetype` (str): File format ('xyz', 'pdb', 'sdf', 'mol', 'mol2', etc.)
- `background_color` (str): Background color ('white', 'black', '#ffffff', etc.)

**Visualization Style Parameters:**
- `show_stick` (bool): Show stick representation (default: True)
- `show_sphere` (bool): Show sphere representation (default: True)
- `show_cartoon` (bool): Show cartoon representation for proteins (default: False)
- `show_line` (bool): Show line representation (default: False)
- `show_surface` (bool): Show molecular surface (default: False)

**Animation Parameters:**
- `current_frame` (int): Current animation frame (default: 0)
- `total_frames` (int): Total number of frames (default: 1)
- `animate` (bool): Enable/disable animation (default: False)
- `animation_speed` (int): Animation speed in milliseconds (default: 100)
- `animate_options` (dict): Custom 3Dmol.js animation options

**Label Parameters:**
- `labels` (list): List of custom labels to display
- `show_atom_labels` (bool): Automatically show atom indices (default: False)

### py3dmol-Compatible Methods

**Basic Visualization:**
```python
# Add molecular model
viewer.addModel(data, format)

# Set visualization style
viewer.setStyle({}, {'stick': {'radius': 0.2}, 'sphere': {'radius': 0.4}})

# Change background color
viewer.setBackgroundColor('lightgray')

# Clear viewer
viewer.clear()

# Force re-render
viewer.render()

# Center/zoom to molecule
viewer.center()
```

**Animation Control:**
```python
# Add multiple frames
viewer.addFrames(structures_list, filetype="xyz")

# Set current frame
viewer.setFrame(frame_number)

# Get current frame
current = viewer.getFrame()

# Start animation
viewer.startAnimation(speed=500, loop_mode="forward")

# Stop animation
viewer.stopAnimation()

# Set animation speed
viewer.setAnimationSpeed(200)
```

**Labeling:**
```python
# Add custom label
viewer.addLabel("Label Text", {
    'position': {'x': 0, 'y': 0, 'z': 0},
    'backgroundColor': 'white',
    'fontColor': 'black',
    'fontSize': 16
})

# Remove all labels
viewer.removeAllLabels()

# Show automatic atom labels
viewer.showAtomLabels(True)

# Auto-generate atom index labels
viewer.autoLabel()
```

### Factory Function

```python
from panel_3dmol import view

# Create viewer with specific dimensions
viewer = view(width=800, height=600)
```

## Supported File Formats

- **XYZ**: Simple Cartesian coordinates with multi-frame support
- **PDB**: Protein Data Bank format
- **SDF**: Structure Data Format (MDL)
- **MOL**: MDL Molfile format
- **MOL2**: Tripos MOL2 format
- **Other formats**: Any format supported by 3Dmol.js

## Panel Integration Features

- ✅ **Reactive Parameters**: Real-time updates when parameters change
- ✅ **File Upload**: Drag-and-drop file loading with Panel widgets
- ✅ **Dashboard Layout**: Seamless integration with Panel layouts
- ✅ **Jupyter Support**: Works in Jupyter notebooks and JupyterLab
- ✅ **Server Apps**: Deploy as Panel server applications
- ✅ **Animation Support**: Multi-frame molecular trajectories with controls
- ✅ **Labeling System**: Custom labels and automatic atom numbering
- ✅ **py3dmol Compatibility**: Drop-in replacement for py3dmol in many cases

## Running the Examples

### As a Panel Server

```bash
# Clone and install
git clone https://github.com/luvwinnie/panel-3dmol.git
cd panel-3dmol
pip install -e .

# Run the example
python test_viewer.py
# Open browser to http://localhost:5007
```

### In Jupyter

```bash
jupyter notebook
# Run the notebook examples in the notebooks/ directory
```

## Advanced Usage

### Custom Styling

```python
# Advanced styling with multiple representations
viewer.setStyle({}, {
    'stick': {'radius': 0.1, 'color': 'blue'},
    'sphere': {'radius': 0.3, 'colorscheme': 'Jmol'}
})

# Protein-specific styling
viewer.setStyle({'resn': 'ALA'}, {'cartoon': {'color': 'red'}})
viewer.setStyle({'resn': 'GLY'}, {'cartoon': {'color': 'green'}})
```

### Animation Options

```python
# Custom animation with 3Dmol.js options
viewer.setAnimationOptions(
    loop='bounce',          # 'forward', 'reverse', 'bounce'
    interval=50,            # Frame interval in ms
    reps=0                  # 0 = infinite, >0 = number of repeats
)
```

### Complex Labeling

```python
# Multiple custom labels with different styles
labels = [
    {
        'text': 'Active Site',
        'options': {
            'position': {'x': 10.5, 'y': 12.3, 'z': 8.7},
            'backgroundColor': 'yellow',
            'fontColor': 'red',
            'fontSize': 20,
            'borderThickness': 2
        }
    },
    {
        'text': 'Substrate',
        'options': {
            'position': {'x': 5.2, 'y': 8.1, 'z': 3.4},
            'backgroundColor': 'lightblue',
            'fontColor': 'navy',
            'fontSize': 16
        }
    }
]

for label in labels:
    viewer.addLabel(label['text'], label['options'])
```

## Deployment

### Panel Server

```python
# app.py
import panel as pn
from panel_3dmol import Mol3DViewer

pn.extension()

def create_app():
    viewer = Mol3DViewer()
    # ... your app logic
    return viewer

pn.serve(create_app, port=5007, show=True)
```

### Docker Deployment

```dockerfile
FROM python:3.9

RUN pip install panel git+https://github.com/luvwinnie/panel-3dmol.git

COPY app.py .
EXPOSE 5007

CMD ["python", "-m", "panel", "serve", "app.py", "--port", "5007", "--allow-websocket-origin=*"]
```

## License

MIT License