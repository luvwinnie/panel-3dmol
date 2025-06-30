#!/usr/bin/env python3
"""
Updated dual molecular viewer with user-controlled labeling
Shows how to add labels from user Python code, not hardcoded
"""

import panel as pn
import param
from panel_3dmol import Mol3DViewer

# Enable Panel extensions
pn.extension('filedropper')
pn.config.sizing_mode = 'stretch_width'

# Global variables to access uploaded files
uploaded_reactant = {
    'filename': None,
    'content': None,
    'format': None,
    'atoms': None,
    'local_path': None
}

uploaded_product = {
    'filename': None,
    'content': None,
    'format': None,
    'atoms': None,
    'local_path': None
}

def count_atoms(file_content, file_ext):
    """Count atoms in the molecular file"""
    try:
        lines = [line.strip() for line in file_content.strip().split('\n') if line.strip()]

        if file_ext == 'xyz':
            return int(lines[0]) if lines else 0
        elif file_ext == 'pdb':
            return len([line for line in lines if line.startswith(('ATOM', 'HETATM'))])
        elif file_ext == 'sdf':
            if len(lines) >= 4:
                counts_line = lines[3].split()
                if len(counts_line) >= 2:
                    return int(counts_line[0])
        else:
            return len([line for line in lines if line and not line.startswith('#')])
    except:
        return "Unknown"

def add_atom_labels_to_viewer(viewer, structure_data, filetype):
    """
    User function to add atom labels - similar to py3dmol example
    User has complete control over when and how this is called
    """
    if not structure_data:
        return
        
    lines = structure_data.strip().split('\n')
    
    if filetype == 'xyz' and len(lines) > 2:
        natoms = int(lines[0])
        atom_lines = lines[2:2 + natoms]
        
        # User controls the labeling loop - exact same as py3dmol
        for idx, line in enumerate(atom_lines):
            parts = line.split()
            if len(parts) >= 4:
                symbol = parts[0]
                x, y, z = map(float, parts[1:4])
                
                # User can customize label appearance
                viewer.addLabel(str(idx + 1), {
                    'position': {'x': x, 'y': y, 'z': z},
                    'backgroundColor': 'white',
                    'backgroundOpacity': 0,
                    'fontColor': 'blue',
                    'font': 'arial',
                    'fontSize': 16,
                    'fontOpacity': 1.0,
                    'inFront': True
                })
                
    elif filetype == 'pdb':
        atom_lines = [line for line in lines if line.startswith(('ATOM', 'HETATM'))]
        
        for idx, line in enumerate(atom_lines):
            if len(line) >= 54:
                x = float(line[30:38].strip())
                y = float(line[38:46].strip()) 
                z = float(line[46:54].strip())
                
                viewer.addLabel(str(idx + 1), {
                    'position': {'x': x, 'y': y, 'z': z},
                    'backgroundColor': 'white',
                    'backgroundOpacity': 0,
                    'fontColor': 'red',  # Different color for PDB
                    'font': 'arial',
                    'fontSize': 14,
                    'fontOpacity': 1.0,
                    'inFront': True
                })

# Create viewers
reactant_viewer = Mol3DViewer()
product_viewer = Mol3DViewer()

# Create file droppers
reactant_dropper = pn.widgets.FileDropper(
    name="🧪 Drop Reactant File (.xyz, .pdb, .mol, .sdf)",
    height=100
)

product_dropper = pn.widgets.FileDropper(
    name="🎯 Drop Product File (.xyz, .pdb, .mol, .sdf)", 
    height=100
)

# Create label control widgets (user controls when to add labels)
label_reactant_btn = pn.widgets.Button(name="Add Atom Labels to Reactant", button_type="primary")
label_product_btn = pn.widgets.Button(name="Add Atom Labels to Product", button_type="primary")
clear_labels_btn = pn.widgets.Button(name="Clear All Labels", button_type="light")

# Callback functions
def on_reactant_drop(event):
    global uploaded_reactant
    if reactant_dropper.value:
        try:
            filename, file_content = next(iter(reactant_dropper.value.items()))
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='ignore')

            extension = filename.split('.')[-1].lower()
            
            # Save file locally
            local_path = f"./{filename}"
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(file_content)

            # Store file data
            uploaded_reactant = {
                'filename': filename,
                'content': file_content,
                'format': extension,
                'atoms': count_atoms(file_content, extension),
                'local_path': local_path
            }

            # Load structure into viewer
            reactant_viewer.filetype = extension
            reactant_viewer.structure = file_content

            print(f"✅ Reactant {filename} loaded successfully as {extension.upper()}")

        except Exception as e:
            print(f"❌ Error reading reactant file: {e}")

def on_product_drop(event):
    global uploaded_product
    if product_dropper.value:
        try:
            filename, file_content = next(iter(product_dropper.value.items()))
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='ignore')

            extension = filename.split('.')[-1].lower()

            # Save file locally
            local_path = f"./{filename}"
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(file_content)

            # Store file data
            uploaded_product = {
                'filename': filename,
                'content': file_content,
                'format': extension,
                'atoms': count_atoms(file_content, extension),
                'local_path': local_path
            }

            # Load structure into viewer
            product_viewer.filetype = extension
            product_viewer.structure = file_content

            print(f"✅ Product {filename} loaded successfully as {extension.upper()}")

        except Exception as e:
            print(f"❌ Error reading product file: {e}")

# Label control callbacks (user triggers these)
def add_reactant_labels(event):
    """User-triggered function to add labels to reactant"""
    if uploaded_reactant['content']:
        # Clear existing labels first
        reactant_viewer.removeAllLabels()
        
        # User function adds labels
        add_atom_labels_to_viewer(
            reactant_viewer, 
            uploaded_reactant['content'], 
            uploaded_reactant['format']
        )
        print(f"🏷️ Added {len(reactant_viewer.labels)} labels to reactant")
    else:
        print("⚠️ No reactant structure loaded")

def add_product_labels(event):
    """User-triggered function to add labels to product"""
    if uploaded_product['content']:
        # Clear existing labels first
        product_viewer.removeAllLabels()
        
        # User function adds labels
        add_atom_labels_to_viewer(
            product_viewer, 
            uploaded_product['content'], 
            uploaded_product['format']
        )
        print(f"🏷️ Added {len(product_viewer.labels)} labels to product")
    else:
        print("⚠️ No product structure loaded")

def clear_all_labels(event):
    """User-triggered function to clear all labels"""
    reactant_viewer.removeAllLabels()
    product_viewer.removeAllLabels()
    print("🧹 All labels cleared")

# Register event handlers
reactant_dropper.param.watch(on_reactant_drop, 'value')
product_dropper.param.watch(on_product_drop, 'value')
label_reactant_btn.on_click(add_reactant_labels)
label_product_btn.on_click(add_product_labels)
clear_labels_btn.on_click(clear_all_labels)

# Utility functions for programmatic control
def sync_styles():
    """Copy all styles from reactant to product"""
    product_viewer.show_stick = reactant_viewer.show_stick
    product_viewer.show_sphere = reactant_viewer.show_sphere
    product_viewer.show_cartoon = reactant_viewer.show_cartoon
    product_viewer.show_line = reactant_viewer.show_line
    product_viewer.show_surface = reactant_viewer.show_surface
    product_viewer.background_color = reactant_viewer.background_color
    product_viewer.render()
    print("🔄 Styles synchronized: Reactant → Product")

# Create the app layout
app = pn.Column(
    "## 🧬 Dual Molecular Viewer with User-Controlled Labels",
    
    # File droppers
    pn.Row(reactant_dropper, product_dropper),
    
    # Label control buttons
    pn.Row(
        label_reactant_btn, 
        label_product_btn, 
        clear_labels_btn
    ),
    
    # Instructions
    pn.pane.Markdown("""
    **Instructions:**
    1. Drop your XYZ/PDB files above
    2. Click "Add Atom Labels" buttons to add numbered labels 
    3. Labels are added through user Python code, not automatically
    4. Use "Clear All Labels" to remove labels
    """),
    
    # Side-by-side viewers
    pn.Row(
        pn.Column("### 🧪 Reactant", reactant_viewer),
        pn.Column("### 🎯 Product", product_viewer)
    ),
    
    sizing_mode='stretch_width'
)

app.servable()

if __name__ == "__main__":
    print("🎉 Dual viewer with user-controlled labeling ready!")
    print("Users control when and how labels are added through Python code")
    print("Run 'panel serve dual_viewer_with_labels.py --show' to test")