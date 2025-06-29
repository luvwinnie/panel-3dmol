import panel as pn
from panel_3dmol import Mol3DViewer

# Enable Panel extensions
pn.extension()

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

# Sample benzene structure for testing
benzene_xyz = """6
Benzene molecule
C    0.0000    1.3970    0.0000
C    1.2098    0.6985    0.0000  
C    1.2098   -0.6985    0.0000
C    0.0000   -1.3970    0.0000
C   -1.2098   -0.6985    0.0000
C   -1.2098    0.6985    0.0000"""

# Load sample data
reactant_viewer.structure = benzene_xyz
reactant_viewer.filetype = "xyz"

# Callback functions
def on_reactant_drop(event):
    if reactant_dropper.value:
        try:
            filename, file_content = next(iter(reactant_dropper.value.items()))
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='ignore')

            extension = filename.split('.')[-1].lower()
            
            reactant_viewer.filetype = extension
            reactant_viewer.structure = file_content
            
            print(f"✅ Reactant {filename} loaded successfully as {extension.upper()}")

        except Exception as e:
            print(f"❌ Error reading reactant file: {e}")

def on_product_drop(event):
    if product_dropper.value:
        try:
            filename, file_content = next(iter(product_dropper.value.items()))
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='ignore')

            extension = filename.split('.')[-1].lower()
            
            product_viewer.filetype = extension
            product_viewer.structure = file_content
            
            print(f"✅ Product {filename} loaded successfully as {extension.upper()}")

        except Exception as e:
            print(f"❌ Error reading product file: {e}")

# Register event handlers
reactant_dropper.param.watch(on_reactant_drop, 'value')
product_dropper.param.watch(on_product_drop, 'value')

# Create layout
app = pn.Column(
    "## 🧬 Dual Molecular Viewer",
    
    # File droppers
    pn.Row(reactant_dropper, product_dropper),
    
    # Side-by-side viewers
    pn.Row(
        pn.Column("### 🧪 Reactant", reactant_viewer),
        pn.Column("### 🎯 Product", product_viewer)
    ),
    
    sizing_mode='stretch_width'
)

app.servable()

if __name__ == "__main__":
    app.show(port=5007)