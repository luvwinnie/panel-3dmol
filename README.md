# Panel-3Dmol

A Panel extension for 3D molecular visualization using 3Dmol.js. Create interactive molecular viewers that work seamlessly with Panel dashboards and Jupyter notebooks.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/luvwinnie/panel-chem.git
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

- `structure` (str): Molecular structure data
- `filetype` (str): File format ('xyz', 'pdb', 'sdf', 'mol', etc.)
- `background_color` (str): Background color ('white', 'black', '#ffffff', etc.)
- `show_stick` (bool): Show stick representation
- `show_sphere` (bool): Show sphere representation
- `show_cartoon` (bool): Show cartoon representation (for proteins)
- `show_line` (bool): Show line representation
- `show_surface` (bool): Show molecular surface

### py3dmol-Compatible Methods

```python
# Set visualization style
viewer.setStyle({}, {'stick': {'radius': 0.2}, 'sphere': {'radius': 0.4}})

# Change background color
viewer.setBackgroundColor('lightgray')

# Clear viewer
viewer.clear()

# Force re-render
viewer.render()
```

### Factory Function

```python
from panel_3dmol import view

# Create viewer with specific dimensions
viewer = view(width=800, height=600)
```

## Supported File Formats

- **XYZ**: Simple Cartesian coordinates
- **PDB**: Protein Data Bank format
- **SDF**: Structure Data Format
- **MOL**: MDL Molfile format
- **MOL2**: Tripos MOL2 format

## Panel Integration Features

- ✅ **Reactive Parameters**: Real-time updates when parameters change
- ✅ **File Upload**: Drag-and-drop file loading with Panel widgets
- ✅ **Dashboard Layout**: Seamless integration with Panel layouts
- ✅ **Jupyter Support**: Works in Jupyter notebooks and JupyterLab
- ✅ **Server Apps**: Deploy as Panel server applications
- ✅ **py3dmol Compatibility**: Drop-in replacement for py3dmol in many cases

## Running the Examples

### As a Panel Server

```bash
# Clone and install
git clone https://github.com/luvwinnie/panel-chem.git
cd panel-chem
pip install -e .

# Run the example
python test_viewer.py
# Open browser to http://localhost:5007
```

### In Jupyter

```bash
jupyter notebook
# Run the notebook examples
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
    return app

pn.serve(create_app, port=5007, show=True)
```

### Docker Deployment

```dockerfile
FROM python:3.9

RUN pip install panel git+https://github.com/luvwinnie/panel-chem.git

COPY app.py .
EXPOSE 5007

CMD ["python", "-m", "panel", "serve", "app.py", "--port", "5007", "--allow-websocket-origin=*"]
```

## License

MIT License