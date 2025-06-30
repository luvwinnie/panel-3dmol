#!/usr/bin/env python3
"""
Example showing how users can control labeling from Python code
Direct equivalent to the py3dmol example provided
"""

import panel as pn
from panel_3dmol import Mol3DViewer

# Enable Panel extensions
pn.extension('filedropper')

def visualize_xyz_with_labels(xyz_path, title='Molecule'):
    """
    Function equivalent to the py3dmol example - user controls everything from Python
    """
    # Read the XYZ file
    with open(xyz_path) as f:
        xyz_data = f.read()

    # Parse the structure manually (user's responsibility, just like py3dmol)
    lines = xyz_data.strip().split('\n')
    natoms = int(lines[0])
    atom_lines = lines[2:2 + natoms]

    # Create the viewer (equivalent to py3Dmol.view())
    view = Mol3DViewer(width=500, height=400)
    
    # Add the model (equivalent to view.addModel())
    view.addModel(xyz_data, 'xyz')
    
    # Set the style (equivalent to view.setStyle())
    view.setStyle({}, {'sphere': {'scale': 0.12}, 'stick': {'radius': 0.08}})
    
    # Set background (equivalent to view.setBackgroundColor())
    view.setBackgroundColor('black')

    # User manually adds labels - exact same loop as py3dmol example
    for idx, line in enumerate(atom_lines):
        parts = line.split()
        if len(parts) >= 4:
            symbol = parts[0]
            x, y, z = map(float, parts[1:4])
            
            # addLabel works exactly like py3dmol
            view.addLabel(str(idx + 1), {
                'position': {'x': x, 'y': y, 'z': z},
                'backgroundColor': 'white',
                'backgroundOpacity': 0,
                'fontColor': 'blue',
                'font': 'arial',
                'fontSize': 16,
                'fontOpacity': 1.0,
                'inFront': True
            })

    # Center/zoom (equivalent to view.zoomTo())
    view.center()
    
    print(title)
    return view

# Create sample XYZ files for testing
reactant_xyz = """6
Benzene (Reactant)
C    0.0000    1.3970    0.0000
C    1.2098    0.6985    0.0000  
C    1.2098   -0.6985    0.0000
C    0.0000   -1.3970    0.0000
C   -1.2098   -0.6985    0.0000
C   -1.2098    0.6985    0.0000"""

product_xyz = """7
Cyclohexane (Product)
C    0.0000    1.4000    0.0000
C    1.2124    0.7000    0.0000  
C    1.2124   -0.7000    0.0000
C    0.0000   -1.4000    0.0000
C   -1.2124   -0.7000    0.0000
C   -1.2124    0.7000    0.0000
H    0.0000    0.0000    1.0000"""

# Write sample files
with open('reactant.xyz', 'w') as f:
    f.write(reactant_xyz)
    
with open('product.xyz', 'w') as f:
    f.write(product_xyz)

# Execute the function exactly like the py3dmol example
print("Creating viewers with user-controlled labeling...")

reactant_viewer = visualize_xyz_with_labels('reactant.xyz', 'Reactant')
product_viewer = visualize_xyz_with_labels('product.xyz', 'Product')

print(f"✅ Reactant viewer created with {len(reactant_viewer.labels)} labels")
print(f"✅ Product viewer created with {len(product_viewer.labels)} labels")

# Alternative: User can also control labeling step by step
print("\nAlternative approach - step by step control:")

# Method 1: User reads file and controls everything
with open('reactant.xyz') as f:
    xyz_data = f.read()

viewer = Mol3DViewer()
viewer.addModel(xyz_data, 'xyz')
viewer.setStyle({}, {'sphere': {'scale': 0.12}, 'stick': {'radius': 0.08}})
viewer.setBackgroundColor('black')

# User parses and adds labels manually
lines = xyz_data.strip().split('\n')
natoms = int(lines[0])
atom_lines = lines[2:2 + natoms]

for idx, line in enumerate(atom_lines):
    parts = line.split()
    if len(parts) >= 4:
        x, y, z = map(float, parts[1:4])
        viewer.addLabel(str(idx + 1), {
            'position': {'x': x, 'y': y, 'z': z},
            'fontColor': 'red',  # User can customize
            'fontSize': 14,
            'inFront': True
        })

print(f"✅ Manual step-by-step viewer created with {len(viewer.labels)} labels")

# Create Panel app to display the results
app = pn.Column(
    "# User-Controlled Labeling Example",
    "## Reactant and Product from Function",
    pn.Row(reactant_viewer, product_viewer),
    
    "## Manual Step-by-Step Control",
    viewer,
    
    sizing_mode='stretch_width'
)

app.servable()

if __name__ == "__main__":
    print("\n🎉 All viewers created with user-controlled labeling!")
    print("The user has complete control over when and how labels are added.")
    print("Run 'panel serve example_user_labels.py --show' to see the results")