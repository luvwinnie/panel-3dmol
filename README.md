# Panel-3Dmol

A Panel extension for 3D molecular visualization using 3Dmol.js.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/luvwinnie/panel-chem.git
```

## Usage

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

# Display
viewer.show()
```

## Features

- 3D molecular visualization using 3Dmol.js
- Multiple file format support (XYZ, PDB, SDF, MOL, etc.)
- Interactive visualization styles (stick, sphere, cartoon, line, surface)
- py3dmol-compatible API
- Reactive parameters for real-time updates

## License

MIT License