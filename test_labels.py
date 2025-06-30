#!/usr/bin/env python3
"""
Test script demonstrating label functionality in panel_3dmol
Similar to the py3dmol example provided
"""

import panel as pn
from panel_3dmol import Mol3DViewer

# Enable Panel extensions
pn.extension('filedropper')

# Sample XYZ data (benzene molecule)
benzene_xyz = """6
Benzene molecule
C    0.0000    1.3970    0.0000
C    1.2098    0.6985    0.0000  
C    1.2098   -0.6985    0.0000
C    0.0000   -1.3970    0.0000
C   -1.2098   -0.6985    0.0000
C   -1.2098    0.6985    0.0000"""

# Create viewer
viewer = Mol3DViewer()

# Add structure
viewer.structure = benzene_xyz
viewer.filetype = 'xyz'

# Style similar to py3dmol example
viewer.setStyle({}, {'sphere': {'scale': 0.12}, 'stick': {'radius': 0.08}})
viewer.setBackgroundColor('black')

# Method 1: Enable automatic atom labeling
print("Method 1: Using showAtomLabels()")
viewer.showAtomLabels(True)

print("✅ Automatic atom labels enabled")

# Method 2: Manual labeling (similar to py3dmol example)
print("\nMethod 2: Using autoLabel() method")
viewer2 = Mol3DViewer()
viewer2.structure = benzene_xyz
viewer2.filetype = 'xyz'
viewer2.setStyle({}, {'sphere': {'scale': 0.12}, 'stick': {'radius': 0.08}})
viewer2.setBackgroundColor('black')

# Use autoLabel method (equivalent to the manual loop in py3dmol)
viewer2.autoLabel()

print("✅ Manual auto-labeling completed")

# Method 3: Custom labels
print("\nMethod 3: Custom labels")
viewer3 = Mol3DViewer()
viewer3.structure = benzene_xyz
viewer3.filetype = 'xyz'
viewer3.setStyle({}, {'sphere': {'scale': 0.12}, 'stick': {'radius': 0.08}})
viewer3.setBackgroundColor('black')

# Add custom labels manually
lines = benzene_xyz.strip().split('\n')
natoms = int(lines[0])
atom_lines = lines[2:2 + natoms]

for idx, line in enumerate(atom_lines):
    parts = line.split()
    if len(parts) >= 4:
        symbol = parts[0]
        x, y, z = map(float, parts[1:4])
        viewer3.addLabel(f"{idx + 1}", {
            'position': {'x': x, 'y': y, 'z': z},
            'backgroundColor': 'white',
            'backgroundOpacity': 0,
            'fontColor': 'blue',
            'font': 'arial',
            'fontSize': 16,
            'fontOpacity': 1.0,
            'inFront': True
        })

print("✅ Custom labels added")

# Create Panel app to display all three methods
app = pn.Column(
    "# Panel-3Dmol Label Demonstration",
    
    pn.Row(
        pn.Column("## Method 1: show_atom_labels=True", viewer),
        pn.Column("## Method 2: autoLabel()", viewer2)
    ),
    
    pn.Column("## Method 3: Custom addLabel()", viewer3),
    
    sizing_mode='stretch_width'
)

print("\n🎉 Label demonstration ready!")
print("The viewers now have atom labels just like the py3dmol example")
print(f"Viewer 1 labels: {len(viewer.labels)}")
print(f"Viewer 2 labels: {len(viewer2.labels)}")  
print(f"Viewer 3 labels: {len(viewer3.labels)}")

# For Jupyter/Panel server
app.servable()

if __name__ == "__main__":
    # Uncomment to serve the app
    # app.show(port=5007)
    print("Run 'panel serve test_labels.py --show' to view the demonstration")